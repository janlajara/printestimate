import math
from django.db import models
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


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

    def create_material(self, type, quantity, name=None, **kwargs):
        clazz = MaterialManager.get_class(type)
        material = clazz.objects.create(name=name, 
            quantity=quantity, **kwargs)
        return material


class Material(PolymorphicModel, Shape):
    objects = MaterialManager()
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default='Material')
    quantity = models.IntegerField(default=1)

    @classmethod
    def get_class(cls, type):
        return cls.objects.get_class(type)
        

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