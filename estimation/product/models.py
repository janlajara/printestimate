import math
from django.db import models
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class Material(PolymorphicModel, Shape):
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default='Material')
    quantity = models.IntegerField(default=1)

    @property
    def type(self):
        return self.component.type


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