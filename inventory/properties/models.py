from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance, Volume
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure
from ..models import Item


class Shape(models.Model):
    class Meta:
        abstract = True
    
    @classmethod
    def join(cls, arr):
        return " ".join([prop for prop in arr if prop is not None and prop != ''])

    @classmethod
    def format(cls, value):
        if value is None:
            return ''
        split = str(value).split()
        num = float(split[0])
        uom = split[1] if len(split) == 2 else ''
        num_fmt = int(num) if num.is_integer() else num
        return '%s%s' % (num_fmt, uom)


class Line(Shape):
    length_value = models.FloatField(null=True, blank=True)
    length_uom = models.CharField(max_length=30, blank=True, null=True, 
                                  choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def length(self):
        if self.length_value is not None and self.length_uom is not None:
            return Distance(**{self.length_uom: self.length_value})

    def __str__(self):
        name = ''
        if self.length is not None:
            length = self.length_value
            name = '%s%s' % (super().format(length),
                             self.length_uom)
        return name


class Tape(Line):
    width_value = models.FloatField(null=True, blank=True)
    width_uom = models.CharField(max_length=30, blank=True, null=True, 
                                 choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def width(self):
        if self.width_value is not None and self.width_uom is not None:
            return Distance(**{self.width_uom: self.width_value})

    def __str__(self):
        width_str = ''
        if self.width is not None:
            width = self.width_value
            width_str = '%s%s' % (super().format(width),
                                  self.width_uom)
        arr = [super().__str__(), width_str]
        return super().join(arr)


class Rectangle(Shape):
    length_value = models.FloatField(null=False, blank=False)
    width_value = models.FloatField(null=False, blank=False)
    size_uom = models.CharField(max_length=30, null=False, blank=False,
                                choices=Measure.UNITS[Measure.DISTANCE])

    class Meta:
        abstract = True

    @property
    def length(self):
        if self.length_value is not None and self.length_value > 0:
            arg = {self.size_uom: self.length_value}
            return Distance(**arg)

    @property
    def width(self):
        if self.width_value is not None and self.width_value > 0:
            arg = {self.size_uom: self.width_value}
            return Distance(**arg)

    @property
    def area(self):
        if self._is_not_none():
            return self.length * self.width

    @property
    def perimeter(self):
        if self._is_not_none():
            return (self.length * 2) + (self.width * 2)

    def _is_not_none(self):
        return self.length is not None and self.width is not None

    def __str__(self):
        str_name = ''
        if self._is_not_none():
            width = self.width_value
            length = self.length_value
            str_name = '%sx%s%s' % (super().format(width),
                                    super().format(length),
                                    self.size_uom)
        return str_name


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


class Liquid(Shape):
    volume_value = models.FloatField(null=True, blank=True)
    volume_uom = models.CharField(max_length=30, blank=True, null=True,
                                  choices=Measure.UNITS[Measure.VOLUME])

    @property
    def volume(self):
        if self.volume_value is not None:
            return Volume(**{self.volume_uom: self.volume_value})

    def __str__(self):
        name = ''
        if self.volume is not None:
            volume = self.volume_value
            name = '%s%s' % (super().format(volume),
                             self.volume_uom)
        return name


class ItemProperties(PolymorphicModel, Shape):
    properties_id = models.AutoField(primary_key=True)
    item = models.OneToOneField(Item, on_delete=models.CASCADE, null=True, 
        related_name='properties')

    @staticmethod
    def get_class(item_type):
        mapping = {
            Item.TAPE: TapeProperties,
            Item.LINE: LineProperties,
            Item.PAPER: PaperProperties,
            Item.PANEL: PanelProperties,
            Item.LIQUID: LiquidProperties,
            Item.OTHER: ItemProperties
        }
        return mapping.get(item_type, ItemProperties)

    def __str__(self):
        return ''


class TapeProperties(Tape, ItemProperties):
    objects = ItemProperties.objects


class LineProperties(Line, ItemProperties):
    objects = ItemProperties.objects


class PaperProperties(Paper, ItemProperties):
    objects = ItemProperties.objects


class PanelProperties(Panel, ItemProperties):
    objects = ItemProperties.objects


class LiquidProperties(Liquid, ItemProperties):
    objects = ItemProperties.objects