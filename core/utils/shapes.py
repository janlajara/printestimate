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


class Estimator:
    class Rectangle:
        def __init__(self, width, length, border=(0,0,0,0)):
            self._width = width
            self._length = length
            self.border = border
        
        @property
        def dimensions(self):
            return (self.width, self.length)

        @property
        def width(self):
            return self._width + self.border_x
        
        @property
        def length(self):
            return self._length + self.border_y

        @property
        def border(self):
            return self._border

        @border.setter
        def border(self, value):
            if value is not None and len(value) == 4:
                self._border = value
            else:
                raise ValueError("Tuple must contain 4 numbers")

        @property
        def border_x(self):
            if self._border is not None:
                return self.border[1] + self.border[3]

        @property
        def border_y(self):
            if self._border is not None:
                return self.border[0] + self.border[2]       

        @classmethod
        def plot(cls, parent, child, rotate=True):
            if isinstance(parent, cls) and isinstance(child, cls):
                params = parent.dimensions + child.dimensions
                estimate_count = BinPacker.estimate_rectangles(*params)
                child_rects = [child.dimensions] * estimate_count
                parent_rect = [parent.dimensions]

                if rotate:
                    packer1 = BinPacker.pack_rectangles(child_rects, parent_rect, True)[0]
                    packer2 = BinPacker.pack_rectangles(child_rects, parent_rect, False)[0]
                    return packer1 if len(packer1) > len(packer2) else packer2
                else:
                    return BinPacker.pack_rectangles(child_rects, parent_rect, False)[0]
            else:
                raise TypeError("Parent or child must be of type Rectangle")

        
