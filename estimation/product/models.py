from django.db import models
from django_measurement.models import MeasurementField
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure
from measurement.measures import Distance
from inventory.models import Item
from ..process.models import Process
from ..exceptions import InvalidProductMeasure, MismatchProductMeasure, UnrecognizedProductMeasure


class Product(PolymorphicModel):

    measures = [('base_length', Measure.DISTANCE),
                ('base_width', Measure.DISTANCE),
                ('base_quantity', Measure.QUANTITY),
                ('alternative_quantity', Measure.QUANTITY)]

    name = models.CharField(max_length=40)
    length = MeasurementField(measurement=Distance)
    width = MeasurementField(measurement=Distance)
    base_quantity = models.IntegerField(default=1)
    base_uom = models.CharField(max_length=15, choices=Measure.QUANTITY_UNITS)
    alternative_uom = models.CharField(max_length=15, choices=Measure.QUANTITY_UNITS)
    processes = models.ManyToManyField(Process, related_name='products')

    @property
    def base_length(self):
        if self.length is not None:
            return getattr(self.length, Measure.STANDARD_UNITS[Measure.DISTANCE])

    @property
    def base_width(self):
        if self.width is not None:
            return getattr(self.width, Measure.STANDARD_UNITS[Measure.DISTANCE])

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
            return mapping.value
            # mapping.save()

    def get_cost(self, alternative_quantity):
        pass


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
            match = [m for m in self.product.measures if m[0] == self.measure]
            if len(match) == 1:
                if match[0][1] == self.process.measure:
                    return True
                else:
                    raise MismatchProductMeasure(match, self.process.measure)
            else:
                raise UnrecognizedProductMeasure(self.measure, self.__class__)


class Paper(Product):
    SHEET = 'sheet'
    PADDED = 'padded'
    CONTINUOUS = 'continuous'
    TYPES = [
        (SHEET, 'Sheet'),
        (PADDED, 'Padded'),
        (CONTINUOUS, 'Continuous')
    ]
    type = models.CharField(max_length=15, choices=TYPES)

    @property
    def substrate_options(self):
        def __get_materials(paper_type):
            return Item.objects.filter(type=paper_type)
        if self.type == Form.PADDED or self.type == Form.SHEET:
            substrate = __get_materials(Item.PAPER_SHEET)
        else:
            substrate = __get_materials(Item.PAPER_ROLL)
        return substrate


class Form(Paper):
    measures = Product.measures + \
                     [('ply_count', Measure.QUANTITY),
                      ('total_ply_count', Measure.QUANTITY)]

    with_numbering = models.BooleanField(default=False)
    with_bir = models.BooleanField(default=False)
    with_amienda = models.BooleanField(default=False)

    @property
    def total_ply_count(self):
        return self.base_quantity * self.ply_count

    @property
    def ply_count(self):
        return len(FormPly.objects.filter(form__pk=self.pk))

    def add_ply(self, item, order):
        ply = FormPly.objects.create(form=self, item=item, order=order)
        return ply


class FormPly(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    item = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True)
