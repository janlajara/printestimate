from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance, Volume
from polymorphic.models import PolymorphicModel


class ItemProperties(PolymorphicModel):

    def __str__(self):
        return ''


class Tape(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)

    def __str__(self):
        return str(self.length) if self.length is not None else ''


class Wire(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)

    def __str__(self):
        return str(self.length) if self.length is not None else ''


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
            str_name = '%s x %s' % (self.width.value, self.length)
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
        s = '%s %s %s' % (super().__str__(),
                          self.finish if self.finish is not None else '',
                          (self.gsm + 'gsm') if self.gsm is not None else '')
        return s.strip()


class Panel(Rectangle):
    thickness = MeasurementField(measurement=Distance, null=True, blank=True)

    def __str__(self):
        s = '%s %s' % (super().__str__(),
                       self.thickness if self.thickness is not None else '')
        return s


class Liquid(ItemProperties):
    volume = MeasurementField(measurement=Volume, null=True, blank=True)

    def __str__(self):
        return '%s' % self.volume if self.volume is not None else ''
