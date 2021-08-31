import math
from django.db import models
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.exceptions import MaterialTypeMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class Product(models.Model):
    name = models.CharField(max_length=20, null=True)
    quantity = models.IntegerField(default=1)


class Component(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    @property
    def total_material_quantity(self):
        return self.materials.count() * self.quantity


class MaterialManager(PolymorphicManager):

    @classmethod
    def get_class(cls, type):
        mapping = {
            Item.TAPE: TapeMaterial,
            Item.LINE: LineMaterial,
            Item.PAPER: PaperMaterial,
            Item.PANEL: PanelMaterial,
            Item.LIQUID: LiquidMaterial,
            Item.OTHER: Material
        }
        clazz = mapping.get(type, Material)
        return clazz

    def create_material(self, component, type, item, name=None, **kwargs):
        if item.type != type:
            raise MaterialTypeMismatch(item.type, type)
        clazz = MaterialManager.get_class(type)
        material = clazz.objects.create(component=component, name=name, 
            item=item, **kwargs)
        return material


class Material(PolymorphicModel, Shape):
    objects = MaterialManager()
    component = models.ForeignKey(Component, on_delete=models.CASCADE,
        related_name='materials')
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=True)
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, 
        related_name='materials')

    @classmethod
    def get_class(cls, type):
        return cls.objects.get_class(type)

    @property
    def quantity(self):
        return self.component.quantity

    @property
    def item_properties(self):
        return self.item.properties

    def estimate_stock_needed(self, quantity):
        return self.item.properties.estimate(self, quantity)

    def estimate(self, obj, quantity):
        qty = self.quantity * quantity
        return Quantity(pc=qty)
        

class TapeMaterial(Material, Tape):
    type = Item.TAPE


class LineMaterial(Material, Line):
    type = Item.LINE


class PaperMaterial(Material, Paper):
    type = Item.PAPER

 
class PanelMaterial(Material, Panel):
    type = Item.PANEL


class LiquidMaterial(Material, Liquid):
    type = Item.LIQUID