from django.db import models
from inventory.models import Item
from estimation.process.models import Operation
from polymorphic.models import PolymorphicModel


class MetaComponent(models.Model):
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=Item.TYPES)

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