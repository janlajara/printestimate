from django.db import models
from django_measurement.models import MeasurementField
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure, Quantity
from measurement.measures import Distance
from inventory.models import Item
from ..process.models import Process
from ..exceptions import InvalidProductMeasure, MismatchProductMeasure, UnrecognizedProductMeasure


class Product(PolymorphicModel):

    measures = ['length', 'width', 'base_quantity', 'alternative_quantity', ]

    name = models.CharField(max_length=40)
    length = MeasurementField(measurement=Distance)
    width = MeasurementField(measurement=Distance)
    base_quantity = MeasurementField(measurement=Quantity, default=Quantity(pc=1))
    base_uom = models.CharField(max_length=15, choices=Measure.QUANTITY_UNITS)
    alternative_uom = models.CharField(max_length=15, choices=Measure.QUANTITY_UNITS)
    processes = models.ManyToManyField(Process, related_name='products')

    @property
    def finished_size(self):
        return {'length': self.length, 'width': self.width}

    @property
    def flat_size(self):
        return {'length': self.length, 'width': self.width}

    @property
    def measure_options(self):
        return self.measures

    @property
    def process_options(self):
        return Process.objects.filter(products__pk=self.pk)

    def link_process(self, process):
        self.processes.add(process)
        ProductProcessMapping.objects.create(product=self, process=process)

    def unlink_process(self, process):
        self.processes.remove(process)
        mapping = ProductProcessMapping.objects.get(process=process)
        if mapping is not None:
            mapping.delete()

    def set_process_measure(self, process, measure, measure_type=None):
        mapping = ProductProcessMapping.objects.get(process=process, product=self)
        if mapping is not None:
            mapping.measure = measure if measure is not None else mapping.measure
            mapping.measure_type = measure_type if measure_type is not None else mapping.measure_type
            if mapping.value is not None:
                mapping.save()
                return mapping.value

    def get_cost(self, alternative_quantity):
        if alternative_quantity is not None:
            total_cost = 0
            total_cost += self._get_processes_cost(alternative_quantity)
            return total_cost

    def _get_processes_cost(self, alternative_quantity):
        for process in self.processes:
            mapping = ProductProcessMapping.objects.get(process=process, product=self)
            total_measure_value = mapping.value * alternative_quantity


class ProductProcessMapping(models.Model):
    STATIC = 'static'
    DYNAMIC = 'dynamic'
    TYPES = [
        (STATIC, 'Static'),
        (DYNAMIC, 'Dynamic')
    ]
    measure = models.CharField(max_length=40, default='')
    measure_type = models.CharField(max_length=10, choices=TYPES, default=STATIC)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.RESTRICT)

    @property
    def value(self):
        if self.product is not None and self.process is not None and self.measure != '':
            if self.measure_type == ProductProcessMapping.DYNAMIC and self.measure == 'alternative_quantity':
                return 1
            if self.measure_type == ProductProcessMapping.DYNAMIC and hasattr(self.product, self.measure):
                self._validate()
                return getattr(self.product, self.measure)
            elif self.measure_type == ProductProcessMapping.STATIC and self.measure.isnumeric():
                return float(self.measure)
            else:
                measure_options = list(map((lambda m: m[0]), self.product.measures))
                raise InvalidProductMeasure(self.measure, self.measure_type, measure_options)
        else:
            return 0

    def _validate(self):
        if self.measure_type == ProductProcessMapping.DYNAMIC:
            # Get the measurement type associated with the product measure
            # and compare with the correct process measure
            if self.measure in self.product.measures:
                measure = getattr(self.product, self.measure).__class__.__name__
                if measure == self.process.measure:
                    return True
                else:
                    raise MismatchProductMeasure(measure, self.process.measure)
            else:
                raise UnrecognizedProductMeasure(self.measure, self.product.__class__)


class Paper(Product):
    item = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True)

    @property
    def substrate_options(self):
        return Item.objects.filter(models.Q(type=Item.PAPER_ROLL) |
                                   models.Q(type=Item.PAPER_SHEET))


class Form(Product):
    SHEET = 'sheet'
    PADDED = 'padded'
    CONTINUOUS = 'continuous'
    TYPES = [
        (SHEET, 'Sheet'),
        (PADDED, 'Padded'),
        (CONTINUOUS, 'Continuous')
    ]
    type = models.CharField(max_length=15, choices=TYPES)
    measures = Product.measures + ['ply_count', 'total_ply_count']

    with_numbering = models.BooleanField(default=False)
    with_bir = models.BooleanField(default=False)
    with_amienda = models.BooleanField(default=False)

    @property
    def substrate_options(self):
        def __get_materials(paper_type):
            return Item.objects.filter(type=paper_type)
        if self.type == Form.PADDED or self.type == Form.SHEET:
            substrate = __get_materials(Item.PAPER_SHEET)
        else:
            substrate = __get_materials(Item.PAPER_ROLL)
        return substrate

    @property
    def total_ply_count(self):
        total_count = self.base_quantity.value * self.ply_count.value
        return Quantity(sheet=total_count)

    @property
    def ply_count(self):
        ply_count = len(FormPly.objects.filter(form__pk=self.pk))
        return Quantity(sheet=ply_count)

    def add_ply(self, item, order):
        ply = FormPly.objects.create(form=self, item=item, order=order)
        return ply


class FormPly(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    item = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True)
