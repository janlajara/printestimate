import math
from django.db import models
from django_measurement.models import MeasurementField
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure, Quantity
from core.utils.binpacker import BinPacker
from measurement.measures import Distance, Area, Volume
from measurement.utils import guess
from inventory.models import Item
from ..machine.models import SheetfedPress
from ..process.models import Process
from ..exceptions import InvalidProductMeasure, MismatchProductMeasure, UnrecognizedProductMeasure


class Product(PolymorphicModel):

    measures = ['length', 'width', 'base_quantity', 'alternative_quantity', ]

    name = models.CharField(max_length=40)
    length = MeasurementField(measurement=Distance)
    width = MeasurementField(measurement=Distance)
    base_quantity = MeasurementField(measurement=Quantity, default=1)
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
    def components(self):
        return ProductComponent.objects.filter(product=self)

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

    def get_materials(self, alternative_quantity):
        materials = []
        for component in self.components:
            count = component.material_count_ratio * alternative_quantity
            pair = (component.material, count)
            materials.append(pair)
        return materials

    def get_cost(self, alternative_quantity, processes):
        if alternative_quantity is not None:
            total_cost = 0
            total_cost += self._get_processes_cost(alternative_quantity, processes)
            total_cost += self._get_materials_cost(alternative_quantity)
            return total_cost

    def _get_materials_cost(self, alternative_quantity):
        cost = 0
        for component in self.components:
            cost += component.get_cost(alternative_quantity)
        return cost

    def _get_processes_cost(self, alternative_quantity, processes):
        cost = 0
        for process in processes:
            mapping = ProductProcessMapping.objects.get(process=process, product=self)
            if mapping is not None:
                total_measure = mapping.value * alternative_quantity
                cost += process.get_cost(total_measure)
        return cost


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
            self._validate_process()
            if self.measure_type == ProductProcessMapping.DYNAMIC and self.measure == 'alternative_quantity':
                return Quantity(pc=1)
            if self.measure_type == ProductProcessMapping.DYNAMIC and hasattr(self.product, self.measure):
                self._validate_measure()
                return getattr(self.product, self.measure)
            elif self.measure_type == ProductProcessMapping.STATIC and self.measure.isnumeric():
                return guess(float(self.measure), self.process.measure_unit,
                             measures=[Distance, Area, Volume, Quantity])
            else:
                measure_options = list(map((lambda m: m[0]), self.product.measures))
                raise InvalidProductMeasure(self.measure, self.measure_type, measure_options)

    def _validate_process(self):
        components = ProductComponent.objects.filter(product=self.product)
        for component in components:
            component.validate_process(self.process)

    def _validate_measure(self):
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


class ProductComponent(PolymorphicModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True)

    @property
    def material_count_ratio(self):
        return 1

    def get_cost(self, alternate_quantity):
        material_count = self.material_count_ratio * alternate_quantity
        return math.ceil(material_count) * self.material.price

    def validate_process(self, process):
        pass


class PackSheet(ProductComponent):
    rotate = models.BooleanField(default=False)

    @property
    def trimsheet_packer(self):
        if self.material is not None:
            parent = self.material.properties
            parentsheet_dimensions = (parent.width.value, parent.length.value)
            trimsheet_dimensions = (self.product.width.value, self.product.length.value)
            return self._pack(parentsheet_dimensions, trimsheet_dimensions)

    @property
    def trimsheet_per_parentsheet(self):
        return len(self.trimsheet_packer) if self.trimsheet_packer is not None else 0

    @property
    def material_count_ratio(self):
        product_base_quantity = self.product.base_quantity.value
        return product_base_quantity / self.trimsheet_per_parentsheet

    def validate_process(self, process):
        machine = process.machine
        if machine is not None:
            machine.validate_input(runsheet_length=self.material.length,
                                   runsheet_width=self.material.width)

    def _pack(self, parent_dimensions, child_dimensions):
        params = parent_dimensions + child_dimensions
        rect_count = BinPacker.estimate_rectangles(*params)
        rectangles = [child_dimensions] * rect_count
        bins = [parent_dimensions]

        if self.rotate:
            packer1 = BinPacker.pack_rectangles(rectangles, bins, True)[0]
            packer2 = BinPacker.pack_rectangles(rectangles, bins, False)[0]
            return packer1 if len(packer1) > len(packer2) else packer2
        else:
            return BinPacker.pack_rectangles(rectangles, bins)[0]


class PackPrintSheet(PackSheet):
    runsheet_width = MeasurementField(measurement=Distance, null=True)
    runsheet_length = MeasurementField(measurement=Distance, null=True)

    @property
    def runsheet_packer(self):
        if self.material is not None and self.product is not None:
            parent = self.material.properties
            parent_dimensions = (parent.width.value, parent.length.value)
            runsheet_dimensions = (self.runsheet_width.value, self.runsheet_length.value)
            return self._pack(parent_dimensions, runsheet_dimensions)

    @property
    def trimsheet_packer(self):
        if self.runsheet_width is not None and self.runsheet_length is not None:
            runsheet_dimensions = (self.runsheet_width.value, self.runsheet_length.value)
            trimsheet_dimensions = (self.product.width.value, self.product.length.value)
            return self._pack(runsheet_dimensions, trimsheet_dimensions)

    @property
    def runsheet_per_parentsheet(self):
        return len(self.runsheet_packer) if self.runsheet_packer is not None else 1

    @property
    def trimsheet_per_runsheet(self):
        return len(self.trimsheet_packer) if self.trimsheet_packer is not None else 1

    @property
    def material_count_ratio(self):
        product_base_quantity = self.product.base_quantity.value
        return product_base_quantity / (self.trimsheet_per_runsheet * self.runsheet_per_parentsheet)

    def validate_process(self, process):
        machine = process.machine
        if machine is not None:
            machine.validate_input(runsheet_length=self.runsheet_length,
                                   runsheet_width=self.runsheet_width)


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
    measures = Product.measures + ['runsheet_count', 'ply_count', 'total_ply_count']
    #with_numbering = models.BooleanField(default=False)
    #with_bir = models.BooleanField(default=False)
    #with_amienda = models.BooleanField(default=False)

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
    def runsheet_trimsheet_ratio(self):
        if self.plys is not None:
            ratios = [1/p.trimsheet_per_runsheet for p in self.plys]
            return max(ratios)

    @property
    def runsheet_count(self):
        count = math.ceil(self.runsheet_trimsheet_ratio * self.total_ply_count.value)
        return Quantity(sheet=count)

    @property
    def plys(self):
        return FormPly.objects.filter(product=self)

    @property
    def total_ply_count(self):
        total_count = self.base_quantity.value * self.ply_count.value
        return Quantity(sheet=total_count)

    @property
    def ply_count(self):
        ply_count = len(FormPly.objects.filter(product__pk=self.pk))
        return Quantity(sheet=ply_count)

    def add_ply(self, material, order, runsheet_length, runsheet_width, rotate=False):
        ply = FormPly.objects.create(product=self, material=material, order=order,
                                     runsheet_length=runsheet_length,
                                     runsheet_width=runsheet_width,
                                     rotate=rotate)
        return ply


class FormPly(PackPrintSheet):
    order = models.IntegerField(default=1)
