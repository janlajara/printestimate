from django.db import models
from measurement.measures import Distance
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure
from core.utils.shapes import Shape, Line, Tape, Rectangle, Liquid


class Paper(Rectangle):
    class Finish:
        UNCOATED = 'uncoated'
        MATTE = 'matte'
        GLOSS = 'gloss'
        SATIN = 'satin'
        TYPES = [
            (UNCOATED, 'Uncoated'),
            (MATTE, 'Matte'),
            (GLOSS, 'Gloss'),
            (SATIN, 'Satin')
        ]
    gsm = models.IntegerField(null=True, blank=False)
    finish = models.CharField(max_length=15, choices=Finish.TYPES, null=True, blank=False)

    def __str__(self):
        gsm = str(self.gsm) + ' gsm' if self.gsm is not None else self.gsm
        arr = [super().__str__(), self.finish, super().format(gsm)]
        return super().join(arr)


class Panel(Rectangle):
    thickness_value = models.FloatField(null=True, blank=True)
    thickness_uom = models.CharField(max_length=30, null=True, blank=True,
                                     choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def thickness(self):
        if self.thickness_value is not None and self.thickness_uom is not None:
            return Distance(**{self.thickness_uom: self.thickness_value})

    def __str__(self):
        thickness_str = ''
        if self.thickness is not None:
            thickness = self.thickness_value
            thickness_str = '%s%s' % (super().format(thickness),
                                      self.thickness_uom)
        arr = [super().__str__(), thickness_str]
        return super().join(arr)


class ItemProperties(PolymorphicModel, Shape):
    properties_id = models.AutoField(primary_key=True)


class TapeProperties(ItemProperties, Tape):
    pass


class LineProperties(ItemProperties, Line):
    pass


class PaperProperties(ItemProperties, Paper):
    pass


class PanelProperties(ItemProperties, Panel):
    pass


class LiquidProperties(ItemProperties, Liquid):
    pass