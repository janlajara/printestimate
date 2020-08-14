from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance, Volume


class MaterialProperties(models.Model):
    pass


class Tape(MaterialProperties):
    length = MeasurementField(measurement=Distance)


class Wire(MaterialProperties):
    length = MeasurementField(measurement=Distance)


class Rectangle(MaterialProperties):
    length = MeasurementField(measurement=Distance)
    width = MeasurementField(measurement=Distance)

    @property
    def area(self):
        return self.length * self.width

    @property
    def perimeter(self):
        return (self.length * 2) + (self.width * 2)


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
    finish = models.CharField(max_length=15, null=True, blank=False)


class Panel(Rectangle):
    thickness = MeasurementField(measurement=Distance)


class Liquid(MaterialProperties):
    volume = MeasurementField(measurement=Volume)
