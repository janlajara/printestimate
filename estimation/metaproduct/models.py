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

    def add_meta_component(self, name, type, **kwargs):
        return MetaComponent.objects.create(name=name, type=type, 
            meta_product=self, **kwargs)

    def add_meta_service(self, name, type, costing_measure, **kwargs):
        count = MetaService.objects.filter(meta_product=self).count()
        sequence = count + 1

        return MetaService.objects.create(meta_product=self, 
            sequence=sequence, name=name, type=type,
            costing_measure=costing_measure, **kwargs)


class MetaProductData(PolymorphicModel):
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=Item.TYPES)
    meta_product = models.ForeignKey(MetaProduct, on_delete=models.CASCADE,
        related_name='meta_product_datas')
    
    def add_meta_operation(self, name, options_type, **kwargs):
        return MetaOperation.objects.create(name=name, options_type=options_type,
            meta_product_data=self, **kwargs)


class MetaEstimateVariable:
    # Total number of raw materials needed
    RAW_MATERIAL = 'Raw Material'   
    # Total number of sets needed (product qty) 
    SET_MATERIAL = 'Component Set'
    # Product quantity x set quantity
    TOTAL_MATERIAL = 'Component Total'
    MACHINE_RUN = 'Running Material'

    # Cut Properties for Paper Materials
    RAW_TO_RUNNING_CUT = 'Parent-to-Runsheet Cut'
    RUNNING_TO_FINAL_CUT = 'Runsheet-to-Finalsheet Cut'
    RAW_TO_FINAL_CUT = 'Parent-to-Finalsheet Cut'

    TYPE_CHOICES = [
        (RAW_MATERIAL, RAW_MATERIAL),
        (SET_MATERIAL, SET_MATERIAL),
        (TOTAL_MATERIAL, TOTAL_MATERIAL),
        (MACHINE_RUN, MACHINE_RUN),
        (RAW_TO_RUNNING_CUT, RAW_TO_RUNNING_CUT),
        (RUNNING_TO_FINAL_CUT, RUNNING_TO_FINAL_CUT),
        (RAW_TO_FINAL_CUT, RAW_TO_FINAL_CUT)
    ]

    def __init__(self, type, costing_measure):
        self.type = type
        self.costing_measure = costing_measure

    @property
    def label(self):
        return '%s %s' % (self.type, self.costing_measure.capitalize() )

    @classmethod
    def material_derived_variables(cls, material_type):
        variable_types = [cls.RAW_MATERIAL, cls.SET_MATERIAL, cls.TOTAL_MATERIAL]
        return cls._get_variables(material_type, variable_types)
    
    @classmethod
    def machine_derived_variables(cls, material_type):
        variable_types = [cls.MACHINE_RUN]
        variables = cls._get_variables(material_type, variable_types)

        if (material_type in [Item.PAPER, Item.PANEL]):
            variable_types = [cls.RAW_TO_RUNNING_CUT, cls.RUNNING_TO_FINAL_CUT, cls.RAW_TO_FINAL_CUT]
            variables += cls._get_variables(Item.OTHER, variable_types)
        
        return variables

    @classmethod
    def _get_variables(cls, material_type, variable_types):
        variables = []
        costing_measures = Item.get_costing_measure_choices(material_type)

        for type in variable_types:
            for costing_measure in costing_measures:
                variable = MetaEstimateVariable(type, costing_measure[0])
                variables.append(variable)

        return variables


class MetaComponent(MetaProductData):
    allow_multiple_materials = models.BooleanField(default=False)
 
    @property
    def meta_estimate_variables(self):
        material_type = self.type
        variables = []

        if len(self.meta_material_options.all()) > 0:
            material_variables = MetaEstimateVariable.material_derived_variables(material_type)
            variables = material_variables

        if len(self.meta_machine_options.all()) > 0:
            machine_variables = MetaEstimateVariable.machine_derived_variables(material_type)
            variables  += machine_variables

        return variables

    def add_meta_operation(self, name, options_type, **kwargs):
        return MetaComponentOperation.objects.create(name=name, options_type=options_type,
            meta_product_data=self, **kwargs)

    def add_meta_material_option(self, item:Item):
        return MetaMaterialOption.objects.create(
            meta_component=self, item=item)

    def add_meta_machine_option(self, machine:Machine):
        if machine.material_type != self.type:
            raise Exception("Cannot add machine with type '%s'. Expected type '%s'" % 
                (machine.material_type, self.type))

        return MetaMachineOption.objects.create(
            meta_component=self, machine=machine)


class MetaService(MetaProductData):
    sequence = models.IntegerField(default=0)
    costing_measure = models.CharField(max_length=15, choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.SET_NULL, 
        blank=True, null=True)
    estimate_variable_type = models.CharField(choices=MetaEstimateVariable.TYPE_CHOICES,
        max_length=30, blank=True, null=True)


class MetaMaterialOption(models.Model):
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.CASCADE, 
        related_name='meta_material_options')
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, 
        related_name='meta_material_options')

    @property
    def label(self):
        return self.item.full_name

    @property
    def type(self):
        return self.item.type

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

    @property
    def costing_measures(self):
        return self.machine.costing_measures


class MetaOperation(PolymorphicModel):
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
        related_name='meta_operations')

    @property
    def options(self):
        if self.options_type in [MetaOperation.SINGLE_OPTION, 
                MetaOperation.MULTIPLE_OPTIONS]:
            return self.meta_operation_options.all()
        else:
            return [self.meta_operation_options.first()]

    def add_option(self, operation):
        if self.options_type == MetaOperation.BOOLEAN_OPTION and \
                len(self.meta_operation_options.all()) > 0:
            raise Exception('Cannot add more options for Boolean type operation')
        else:
            return MetaOperationOption.objects.create(
                meta_operation=self, operation=operation)

    def clear_options(self):
        self.meta_operation_options.all().delete()


class MetaComponentOperation(MetaOperation):
    costing_measure = models.CharField(max_length=15, choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)


class MetaOperationOption(models.Model):
    meta_operation = models.ForeignKey(MetaOperation, on_delete=models.CASCADE,
        related_name='meta_operation_options')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE,
        related_name='meta_operation_options')

    @property
    def label(self):
        return self.operation.name
