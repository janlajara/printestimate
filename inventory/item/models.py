from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance, Volume
from polymorphic.models import PolymorphicModel


class ItemProperties(PolymorphicModel):

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

    def __str__(self):
        return ''


class Tape(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)

    def __str__(self):
        return super().format(self.length)


class Wire(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)

    def __str__(self):
        return super().format(self.length)


class Rectangle(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)
    width = MeasurementField(measurement=Distance, null=True, blank=True)

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
            str_name = '%sx%s' % (super().format(self.width.value),
                                  super().format(self.length))
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
    thickness = MeasurementField(measurement=Distance, null=True, blank=True)

    def __str__(self):
        arr = [super().__str__(), super().format(self.thickness)]
        return super().join(arr)


class Liquid(ItemProperties):
    volume = MeasurementField(measurement=Volume, null=True, blank=True)

    def __str__(self):
        return super().format(self.volume)
