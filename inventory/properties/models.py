from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance, Volume
from polymorphic.models import PolymorphicModel
from core.utils.measures import Measure


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

    @classmethod
    def _eval_attr(cls, measurement, uom):
        evaluated = getattr(measurement, uom)
        return evaluated if evaluated is not None else measurement

    def __str__(self):
        return ''


class Line(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)
    length_uom = models.CharField(max_length=30, choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def length_value(self):
        return self._eval_attr(self.length, self.length_uom)

    def __str__(self):
        name = ''
        if self.length is not None:
            try:
                length = self.length_value
                name = '%s%s' % (ItemProperties.format(length),
                                 self.length_uom)
            except AttributeError:
                name = ItemProperties.format(self.length)
        return name


class Tape(Line):
    width = MeasurementField(measurement=Distance, null=True, blank=True)
    width_uom = models.CharField(max_length=30, choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def width_value(self):
        return self._eval_attr(self.width, self.width_uom)

    def __str__(self):
        width_str = ''
        if self.width is not None:
            try:
                width = self.width_value
                width_str = '%s%s' % (ItemProperties.format(width),
                                          self.width_uom)
            except AttributeError:
                width_str = ItemProperties.format(self.width)

        arr = [super().__str__(), width_str]
        return super().join(arr)


class Rectangle(ItemProperties):
    length = MeasurementField(measurement=Distance, null=True, blank=True)
    width = MeasurementField(measurement=Distance, null=True, blank=True)
    size_uom = models.CharField(max_length=30, choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def length_value(self):
        return self._eval_attr(self.length, self.size_uom)

    @property
    def width_value(self):
        return self._eval_attr(self.width, self.size_uom)

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
            try:
                width = self.width_value
                length = self.length_value
                str_name = '%sx%s%s' % (ItemProperties.format(width),
                                        ItemProperties.format(length),
                                        self.size_uom)
            except AttributeError:
                str_name = '%sx%s' % (ItemProperties.format(self.width.value),
                                      ItemProperties.format(self.length))
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
    thickness_uom = models.CharField(max_length=30, choices=Measure.UNITS[Measure.DISTANCE])

    @property
    def thickness_value(self):
        return self._eval_attr(self.thickness, self.thickness_uom)

    def __str__(self):
        thickness_str = ''
        if self.thickness is not None:
            try:
                thickness = self.thickness_value
                thickness_str = '%s%s' % (ItemProperties.format(thickness),
                                          self.thickness_uom)
            except AttributeError:
                thickness_str = ItemProperties.format(self.thickness)

        arr = [super().__str__(), thickness_str]
        return super().join(arr)


class Liquid(ItemProperties):
    volume = MeasurementField(measurement=Volume, null=True, blank=True)
    volume_uom = models.CharField(max_length=30, choices=Measure.UNITS[Measure.VOLUME])

    @property
    def volume_value(self):
        return self._eval_attr(self.volume, self.volume_uom)

    def __str__(self):
        name = ''
        if self.volume is not None:
            try:
                volume = self.volume_value
                name = '%s%s' % (ItemProperties.format(volume),
                                 self.volume_uom)
            except AttributeError:
                name = ItemProperties.format(self.volume)
        return name
