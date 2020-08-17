from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance, Volume


class ItemProperties(models.Model):
    pass


class Tape(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)


class Wire(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)


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
        return self.length is not None & self.width is not None


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


class Panel(Rectangle):
    thickness = MeasurementField(measurement=Distance, null=True, blank=True)


class Liquid(ItemProperties):
    volume = MeasurementField(measurement=Volume, null=True, blank=True)
