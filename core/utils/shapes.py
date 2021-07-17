import math
from django.db import models
from core.utils.measures import Measure
from measurement.measures import Distance, Volume
from .binpacker import BinPacker


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

    def gte(self, obj):
        pass

    def _validate(self, obj):
        pass

    def _raise_type_error(self, expected, actual):
        raise TypeError('Instance expected must of be type %s. Actual is %' % 
            (expected.__class__, actual.__class__))


class Line(Shape):
    measures = [Measure.DISTANCE]
    length_value = models.FloatField(null=True, blank=True)
    length_uom = models.CharField(max_length=30, blank=True, null=True, 
                                  choices=Measure.UNITS[Measure.DISTANCE])

    class Meta:
        abstract = True

    @property
    def length(self):
        if self.length_value is not None and self.length_uom is not None:
            return Distance(**{self.length_uom: self.length_value})

    def pack(self, line):
        self._validate(line)
        if 0 < line.length.mm <= self.length.mm:
            return math.floor(self.length.mm / line.length.mm)
        else:
            return 0

    def gte(self, line):
        self._validate(line)
        return self.length.mm >= line.length.mm

    def _validate(self, line):
        if not isinstance(line, Line):
            self._raise_type_error(self, line)

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

    class Meta:
        abstract = True

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
    measures = [Measure.DISTANCE, Measure.AREA]
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

    @property
    def pack_width(self):
        return self.width_value

    @property
    def pack_length(self):
        return self.length_value

    def pack(self, rectangle, rotate=True):
        return len(self.packer(rectangle, rotate))

    def packer(self, rectangle, rotate):
        self._validate(rectangle)

        parent_width = Distance(**{self.size_uom: self.pack_width})
        parent_length = Distance(**{self.size_uom: self.pack_length})
        child_width = Distance(**{rectangle.size_uom: rectangle.pack_width})
        child_length = Distance(**{rectangle.size_uom: rectangle.pack_length})

        parent_dimensions = (parent_width.mm, parent_length.mm)
        child_dimensions = (child_width.mm, child_length.mm)
        params = parent_dimensions + child_dimensions
        estimate_count = BinPacker.estimate_rectangles(*params)
        child_rects = [child_dimensions] * estimate_count
        parent_rect = [parent_dimensions]

        if rotate:
            packer1 = BinPacker.pack_rectangles(child_rects, parent_rect, True)[0]
            packer2 = BinPacker.pack_rectangles(child_rects, parent_rect, False)[0]
            return packer1 if len(packer1) > len(packer2) else packer2
        else:
            return BinPacker.pack_rectangles(child_rects, parent_rect, False)[0]

    def gte(self, rectangle):
        self._validate(rectangle)
        return self.width.mm >= rectangle.width.mm and self.length.mm >= rectangle.length.mm

    def within_bounds(self, width, length, unit):
        w = Distance(**{unit: width})
        l = Distance(**{unit: length})
        return (self.width >= w and self.length >= l) or (self.width >= l and self.length >= w)

    def _validate(self, rectangle):
        if not isinstance(rectangle, Rectangle):
            self._raise_type_error(self, rectangle)

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


class Liquid(Shape):
    measures = [Measure.VOLUME]
    volume_value = models.FloatField(null=True, blank=True)
    volume_uom = models.CharField(max_length=30, blank=True, null=True,
                                  choices=Measure.UNITS[Measure.VOLUME])

    class Meta:
        abstract = True
        
    @property
    def volume(self):
        if self.volume_value is not None:
            return Volume(**{self.volume_uom: self.volume_value})

    def pack(self, liquid):
        self._validate(liquid)
        if 0 < liquid.length.ml <= self.length.ml:
            return math.floor(self.length.ml / liquid.length.ml)
        else:
            return 0

    def gte(self, liquid):
        self._validate(liquid)
        return self.volume.ml >= liquid.volume.ml

    def _validate(self, liquid):
        if not isinstance(liquid, Liquid):
            self._raise_type_error(self, liquid)

    def __str__(self):
        name = ''
        if self.volume is not None:
            volume = self.volume_value
            name = '%s%s' % (super().format(volume),
                             self.volume_uom)
        return name