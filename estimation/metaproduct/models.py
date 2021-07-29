from django.db import models
from core.utils.measures import CostingMeasure
from inventory.models import Item
from estimation.process.models import Operation
from polymorphic.models import PolymorphicModel


class MetaProduct(models.Model):
    name = models.CharField(max_length=40)

    def add_meta_component(self, name, type):
        return MetaComponent.objects.create(name=name, type=type, 
            meta_product=self)

    def add_meta_service(self, name, type, costing_measure):
        return MetaService.objects.create(name=name, type=type,
            costing_measure=costing_measure, meta_product=self)


class MetaService(models.Model):
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=Item.TYPES)
    costing_measure = models.CharField(max_length=15, choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)
    meta_product = models.ForeignKey(MetaProduct, on_delete=models.CASCADE)


class MetaComponent(models.Model):
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=Item.TYPES)
    meta_product = models.ForeignKey(MetaProduct, on_delete=models.CASCADE)

    def add_meta_material_option(self, label, item:Item):
        return MetaMaterialOption.objects.create(label=label, 
            meta_component=self, item=item)
    
    def add_meta_property(self, name, options_type):
        return MetaProperty.objects.create(name=name, options_type=options_type,
            meta_component=self)


class MetaMaterialOption(models.Model):
    label = models.CharField(max_length=40)
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.CASCADE, 
        related_name='meta_material_options')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, 
        related_name='meta_material_options')


class MetaProperty(models.Model):
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
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.CASCADE, 
        related_name='meta_properties')
    meta_service = models.ForeignKey(MetaService, on_delete=models.SET_NULL,
        related_name='meta_properties', null=True)

    @property
    def options(self):
        if self.options_type in [MetaProperty.SINGLE_OPTION, 
                MetaProperty.MULTIPLE_OPTIONS]:
            return self.meta_property_options.all()
        else:
            return [self.meta_property_options.first()]

    def add_option(self, label, operation):
        if self.options_type == MetaProperty.BOOLEAN_OPTION and \
                len(self.meta_property_options.all()) > 0:
            raise Exception('Cannot add more options for Boolean type property')
        else:
            return MetaPropertyOption.objects.create(
                meta_property=self, label=label, operation=operation)

    def clear_options(self):
        self.meta_property_options.all().delete()


class MetaPropertyOption(models.Model):
    label = models.CharField(max_length=40)
    meta_property = models.ForeignKey(MetaProperty, on_delete=models.CASCADE,
        related_name='meta_property_options')
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL,
        related_name='meta_property_options', null=True)