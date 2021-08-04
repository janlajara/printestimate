from django.db import models
from core.utils.measures import CostingMeasure
from inventory.models import Item
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

    def add_meta_property(self, name, options_type, **kwargs):
        return MetaComponentProperty.objects.create(name=name, options_type=options_type,
            meta_product_data=self, **kwargs)

    def add_meta_material_option(self, item:Item):
        return MetaMaterialOption.objects.create(
            meta_component=self, item=item)


class MetaMaterialOption(models.Model):
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.CASCADE, 
        related_name='meta_material_options')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, 
        related_name='meta_material_options')

    @property
    def label(self):
        return self.item.full_name


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
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL,
        related_name='meta_property_options', null=True)

    @property
    def label(self):
        return self.operation.name