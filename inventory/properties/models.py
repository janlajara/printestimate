from django.db import models
from measurement.measures import Distance
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure
from core.utils.shapes import Shape, Line, Tape, Rectangle, Liquid


class Paper(Rectangle):
    class Meta:
        abstract = True

    class Layout(Rectangle.Layout):
        def __init__(self, gsm=None, finish=None, **kwargs):
            super().__init__(**kwargs)
            self.gsm = gsm
            self.finish = finish

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

    @property
    def layout(self):
        layout = Paper.Layout(width=self.width_value, length=self.length_value, 
            uom=self.size_uom, gsm=self.gsm, finish=self.finish)
        return layout

    def __str__(self):
        gsm = str(self.gsm) + ' gsm' if self.gsm is not None else self.gsm
        arr = [super().__str__(), self.finish, super().format(gsm)]
        return super().join(arr)


class Panel(Rectangle):
    thickness_value = models.FloatField(null=True, blank=True)
    thickness_uom = models.CharField(max_length=30, null=True, blank=True,
                                     choices=Measure.UNITS[Measure.DISTANCE])

    class Meta:
        abstract = True

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

    @staticmethod
    def get_class(item_type):
        mapping = {
            'tape': TapeProperties,
            'line': LineProperties,
            'paper': PaperProperties,
            'panel': PanelProperties,
            'liquid': LiquidProperties,
            'other': ItemProperties
        }
        return mapping.get(item_type, ItemProperties)


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