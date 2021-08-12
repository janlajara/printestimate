from django.db import models
from core.utils.shapes import Shape
from core.utils.measures import CostingMeasure
from inventory.models import Item
from estimation.machine.models import Machine
from estimation.process.models import Operation
from polymorphic.models import PolymorphicModel


class MetaProduct(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100, null=True)

    def add_meta_component(self, name, type):
        return MetaComponent.objects.create(name=name, type=type, 
            meta_product=self)

    def add_meta_service(self, name, type, costing_measure):
        return MetaService.objects.create(name=name, type=type,
            costing_measure=costing_measure, meta_product=self)


class MetaProductData(models.Model):
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=Item.TYPES)
    meta_product = models.ForeignKey(MetaProduct, on_delete=models.CASCADE)
    
    def add_meta_property(self, name, options_type, **kwargs):
        return MetaProperty.objects.create(name=name, options_type=options_type,
            meta_product_data=self, **kwargs)


class MetaService(MetaProductData):
    costing_measure = models.CharField(max_length=15, choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)


class MetaComponent(MetaProductData):
    multiple_materials = models.BooleanField(default=False)

    @property
    def meta_estimate_variables(self):
        variables = []
        counter = 0

        mat = self.meta_material_options.first()
        if mat is not None:
            for type in MetaEstimateVariable.MATERIAL_DERIVED_TYPES:
                for costing_measure in mat.costing_measures:
                    variable = MetaEstimateVariable(counter, type, costing_measure) 
                    variables.append(variable)
                    counter += 1

        mac = self.meta_machine_options.first()
        if mac is not None:
            for type in MetaEstimateVariable.MACHINE_DERIVED_TYPES:
                for costing_measure in mac.costing_measures:
                    variable = MetaEstimateVariable(counter, type, costing_measure) 
                    variables.append(variable)
                    counter += 1
        
        return variables

    def add_meta_property(self, name, options_type, **kwargs):
        return MetaComponentProperty.objects.create(name=name, options_type=options_type,
            meta_product_data=self, **kwargs)

    def add_meta_material_option(self, item:Item):
        return MetaMaterialOption.objects.create(
            meta_component=self, item=item)

    def add_meta_machine_option(self, machine:Machine):
        if machine.type != self.type:
            raise Exception("Cannot add machine with type '%s'. Expected type '%s'" % 
                (machine.type, self.type))

        return MetaMachineOption.objects.create(
            meta_component=self, machine=machine)


class MetaEstimateVariable:
    RAW_MATERIAL = 'Raw Material'
    SET_MATERIAL = 'Set Material'
    TOTAL_MATERIAL = 'Total Material'
    MACHINE_RUN = 'Machine Run Material'

    MATERIAL_DERIVED_TYPES = [
        RAW_MATERIAL, SET_MATERIAL,
        TOTAL_MATERIAL
    ]
    MACHINE_DERIVED_TYPES = [
        MACHINE_RUN
    ]
    TYPES = [
        RAW_MATERIAL, SET_MATERIAL,
        TOTAL_MATERIAL, MACHINE_RUN
    ]

    def __init__(self, id, type, costing_measure):
        self.id = id
        self.type = type
        self.costing_measure = costing_measure

    @property
    def label(self):
        return '%s %s' % (self.type, self.costing_measure.capitalize() )


class MetaMaterialOption(models.Model):
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.CASCADE, 
        related_name='meta_material_options')
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, 
        related_name='meta_material_options')

    @property
    def label(self):
        return self.item.full_name

    @property
    def costing_measures(self):
        return self.item.properties.costing_measures


class MetaMachineOption(models.Model):
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.CASCADE,
        related_name='meta_machine_options')
    machine = models.ForeignKey(Machine, on_delete=models.RESTRICT,
        related_name='meta_machine_option')

    @property
    def label(self):
        return self.machine.name


class MetaProperty(PolymorphicModel):
    SINGLE_OPTION = 'Single'
    MULTIPLE_OPTIONS = 'Multiple'
    BOOLEAN_OPTION = 'Boolean'
    TYPES = [
        (SINGLE_OPTION, 'Single'),
        (MULTIPLE_OPTIONS, 'Multiple'),
        (BOOLEAN_OPTION, 'On/Off')
    ]
    name = models.CharField(max_length=40)
    options_type = models.CharField(max_length=26, choices=TYPES)
    is_required = models.BooleanField(default=False)
    meta_product_data = models.ForeignKey(MetaProductData, on_delete=models.CASCADE, 
        related_name='meta_properties')

    @property
    def options(self):
        if self.options_type in [MetaProperty.SINGLE_OPTION, 
                MetaProperty.MULTIPLE_OPTIONS]:
            return self.meta_property_options.all()
        else:
            return [self.meta_property_options.first()]

    def add_option(self, operation):
        if self.options_type == MetaProperty.BOOLEAN_OPTION and \
                len(self.meta_property_options.all()) > 0:
            raise Exception('Cannot add more options for Boolean type property')
        else:
            return MetaPropertyOption.objects.create(
                meta_property=self, operation=operation)

    def clear_options(self):
        self.meta_property_options.all().delete()


class MetaComponentProperty(MetaProperty):
    costing_measure = models.CharField(max_length=15, choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)


class MetaPropertyOption(models.Model):
    meta_property = models.ForeignKey(MetaProperty, on_delete=models.CASCADE,
        related_name='meta_property_options')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE,
        related_name='meta_property_options')

    @property
    def label(self):
        return self.operation.name