from django.db import models
from estimation.metaproduct.models import MetaProduct, MetaComponent, MetaService, \
    MetaMaterialOption, MetaOperation, MetaOperationOption
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.exceptions import MaterialTypeMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class ProductTemplate(models.Model):
    meta_product = models.ForeignKey(MetaProduct, on_delete=models.RESTRICT)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100, null=True)

    def add_component_template(self, meta_component, quantity):
        component_template = ComponentTemplate.objects.create(
            product_template=self, meta_component=meta_component,
            quantity=quantity)
        return component_template


class ComponentTemplate(models.Model):
    product_template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE,
        related_name='component_templates')
    meta_component = models.ForeignKey(MetaComponent, on_delete=models.RESTRICT)
    quantity = models.IntegerField(default=1)

    @property
    def name(self):
        return self.meta_component.name

    @property
    def type(self):
        return self.meta_component.type

    @property
    def total_material_quantity(self):
        return self.quantity * self.material_templates.count()

    def add_material_template(self, meta_material_option, **kwargs):
        material_template = MaterialTemplate.objects.create_material_template(
            component_template=self, meta_material_option=meta_material_option,
            **kwargs)
        return material_template


class MaterialTemplateManager(PolymorphicManager):

    @classmethod
    def get_class(cls, type):
        mapping = {
            Item.TAPE: TapeMaterialTemplate,
            Item.LINE: LineMaterialTemplate,
            Item.PAPER: PaperMaterialTemplate,
            Item.PANEL: PanelMaterialTemplate,
            Item.LIQUID: LiquidMaterialTemplate,
            Item.OTHER: MaterialTemplate
        }
        clazz = mapping.get(type, MaterialTemplate)
        return clazz

    def create_material_template(self, component_template, 
            meta_material_option, **kwargs):
        if component_template.type != meta_material_option.type:
            raise MaterialTypeMismatch(component_template.type, meta_material_option.type)
        clazz = MaterialTemplateManager.get_class(component_template.type)
        material_template = clazz.objects.create(component_template=component_template, 
            meta_material_option=meta_material_option, **kwargs)
        return material_template


class MaterialTemplate(PolymorphicModel, Shape):
    objects = MaterialTemplateManager()
    material_template_id = models.AutoField(primary_key=True)
    component_template = models.ForeignKey(ComponentTemplate, on_delete=models.CASCADE,
        related_name='material_templates')
    meta_material_option = models.ForeignKey(MetaMaterialOption, on_delete=models.RESTRICT)

    @property
    def quantity(self):
        return self.component_template.quantity

    @property
    def label(self):
        return self.meta_material_option.label


class TapeMaterialTemplate(MaterialTemplate, Tape):
    pass


class LineMaterialTemplate(MaterialTemplate, Line):
    pass


class PaperMaterialTemplate(MaterialTemplate, Paper):
    pass
 

class PanelMaterialTemplate(MaterialTemplate, Panel):
    pass


class LiquidMaterialTemplate(MaterialTemplate, Liquid):
    pass