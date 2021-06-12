import math
from django.db import models
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class Component(models.Model):
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=Item.TYPES)

    def add_material(self, name, quantity, **kwargs):
        material = Material.objects.create_material(component=self, 
            quantity=quantity, name=name, **kwargs)
        return material


class MaterialManager(PolymorphicManager):
    def create_material(self, component, quantity, name=None, **kwargs):
        mapping = {
            Item.TAPE: TapeMaterial,
            Item.LINE: LineMaterial,
            Item.PAPER: PaperMaterial,
            Item.PANEL: PanelMaterial,
            Item.LIQUID: LiquidMaterial,
            Item.OTHER: Material
        }
        clazz = mapping.get(component.type, Material)
        material = clazz.objects.create(name=name, component=component,
            quantity=quantity, **kwargs)
        return material


class Material(PolymorphicModel, Shape):
    objects = MaterialManager()
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default='Material')
    component = models.ForeignKey(Component, on_delete=models.CASCADE,
        related_name='materials')
    items = models.ManyToManyField(Item, related_name='materials', blank=True)
    quantity = models.IntegerField(default=1)

    @property
    def type(self):
        return self.component.type

    def link_item(self, item):
        self.items.add(item)


class TapeMaterial(Material, Tape):
    pass


class LineMaterial(Material, Line):
    pass


class PaperMaterial(Material, Paper):
    pass

 
class PanelMaterial(Material, Panel):
    pass


class LiquidMaterial(Material, Liquid):
    pass