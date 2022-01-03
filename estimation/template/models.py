from django.db import models
from estimation.metaproduct.models import MetaProduct, MetaComponent, MetaService, \
    MetaMaterialOption, MetaOperation, MetaOperationOption, MetaMachineOption
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.exceptions import MaterialTypeMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class ProductTemplate(models.Model):
    meta_product = models.ForeignKey(MetaProduct, on_delete=models.RESTRICT)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100, null=True)

    @property
    def code(self):
        return 'PT-%s' % (str(self.id).zfill(4))

    def add_component_template(self, meta_component, quantity, **kwargs):
        component_template = ComponentTemplate.objects.create_component_template(
            product_template=self, meta_component=meta_component,
            quantity=quantity, **kwargs)
        return component_template

    def add_service_template(self, meta_service):
        service_template = ServiceTemplate.objects.create(
            product_template=self, meta_service=meta_service)
        return service_template


class ComponentTemplateManager(PolymorphicManager):

    @classmethod
    def get_class(cls, type):
        mapping = {
            Item.TAPE: TapeComponentTemplate,
            Item.LINE: LineComponentTemplate,
            Item.PAPER: PaperComponentTemplate,
            Item.PANEL: PanelComponentTemplate,
            Item.LIQUID: LiquidComponentTemplate,
            Item.OTHER: ComponentTemplate
        }
        clazz = mapping.get(type, ComponentTemplate)
        return clazz

    def update_component_template(self, id, type, **kwargs):
        clazz = ComponentTemplateManager.get_class(type)
        clazz.objects.filter(pk=id).update(**kwargs)

    def create_component_template(self, product_template, meta_component, **kwargs):
        clazz = ComponentTemplateManager.get_class(meta_component.type)
        component_template = clazz.objects.create(product_template=product_template, 
            meta_component=meta_component, **kwargs)
        return component_template


class ComponentTemplate(PolymorphicModel, Shape):
    objects = ComponentTemplateManager()
    component_template_id = models.AutoField(primary_key=True)
    product_template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE,
        related_name='component_templates')
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.RESTRICT)
    machine_option = models.ForeignKey(MetaMachineOption, on_delete=models.RESTRICT,
        null=True, blank=True)
    quantity = models.IntegerField(default=1)

    @property
    def name(self):
        return self.meta_component.name

    @property
    def size(self):
        return str(self)

    @property
    def type(self):
        return self.meta_component.type

    @property
    def total_material_quantity(self):
        return self.quantity * self.material_templates.count()

    def add_material_template(self, meta_material_option, **kwargs):
        material_template = MaterialTemplate.objects.create(
            component_template=self, meta_material_option=meta_material_option,
            **kwargs)
        return material_template


class TapeComponentTemplate(ComponentTemplate, Tape):
    pass


class LineComponentTemplate(ComponentTemplate, Line):
    pass


class PaperComponentTemplate(ComponentTemplate, Paper):
    pass
 

class PanelComponentTemplate(ComponentTemplate, Panel):
    pass


class LiquidComponentTemplate(ComponentTemplate, Liquid):
    pass


class MaterialTemplate(models.Model):
    component_template = models.ForeignKey(ComponentTemplate, on_delete=models.CASCADE,
        related_name='material_templates')
    meta_material_option = models.ForeignKey(MetaMaterialOption, on_delete=models.RESTRICT)

    @property
    def item(self):
        return self.meta_material_option.item

    @property
    def type(self):
        return self.meta_material_option.type

    @property
    def quantity(self):
        return self.component_template.quantity

    @property
    def label(self):
        return self.meta_material_option.label


class ServiceTemplate(models.Model):
    product_template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE,
        related_name='service_templates')
    meta_service = models.ForeignKey(MetaService, on_delete=models.RESTRICT)

    @property
    def name(self):
        return self.meta_service.name

    @property
    def component_template(self):
        if self.meta_service is not None:
            meta_component = self.meta_service.meta_component
            component_template = self.product_template.component_templates.get(
                meta_component__pk=meta_component.pk)
            return component_template

    @property
    def type(self):
        return self.meta_service.type

    @property
    def sequence(self):
        return self.meta_service.sequence

    @property
    def costing_measure(self):
        return self.meta_service.costing_measure

    @property
    def estimate_variable_type(self):
        return self.meta_service.estimate_variable_type

    def add_operation_template(self, meta_operation):
        operation_template = OperationTemplate.objects.create(
            service_template=self, meta_operation=meta_operation)
        return operation_template


class OperationTemplate(models.Model):
    service_template = models.ForeignKey(ServiceTemplate, on_delete=models.CASCADE,
        related_name='operation_templates')
    meta_operation = models.ForeignKey(MetaOperation, on_delete=models.RESTRICT)

    @property
    def name(self):
        return self.meta_operation.name

    def add_operation_option_template(self, meta_operation_option):
        operation_option_template = OperationOptionTemplate.objects.create(
            operation_template=self, meta_operation_option=meta_operation_option)
        return operation_option_template


class OperationOptionTemplate(models.Model):
    operation_template = models.ForeignKey(OperationTemplate, on_delete=models.CASCADE,
        related_name='operation_option_templates')
    meta_operation_option = models.ForeignKey(MetaOperationOption, on_delete=models.RESTRICT)

    @property
    def label(self):
        return self.meta_operation_option.label
