import math
from django.db import models
from rest_framework import serializers
from core.utils.measures import Measure, CostingMeasure
from measurement.measures import Distance, Volume
from .binpacker import BinPacker


class Shape(models.Model):
    costing_measures = [CostingMeasure.QUANTITY]

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

    def pack(self):
        pass

    def estimate(self, obj, quantity):
        pass

    def gte(self, obj):
        pass

    def _validate(self, obj):
        pass

    def _raise_type_error(self, expected, actual):
        raise TypeError('Instance expected must of be type %s. Actual is %' % 
            (expected.__class__, actual.__class__))

    def __str__(self):
        return ''


class Line(Shape):
    costing_measures = [CostingMeasure.LENGTH]
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

    def estimate(self, line, quantity):
        outs = self.pack(line)
        estimate = quantity / outs
        return {
            Measure.DISTANCE: self.length * estimate
        }

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
    class Layout:
        def __init__(self, i=0, x=0, y=0, width=0, length=0, 
                is_rotated=False, uom=None):
            self.i = i
            self.x = x 
            self.y = y 
            self.width = width
            self.length = length
            self.is_rotated = is_rotated
            self.uom = uom
    
        def area(self):
            return self.width * self.length
    
    class LayoutMeta:
        def __init__(self, layouts, count, usage, wastage, rotate, 
                name=None, cut_count=0):
            self.name = name
            self.layouts = layouts
            self.count = count
            self.usage = usage
            self.wastage = wastage
            self.rotate = rotate
            self.cut_count = cut_count

        def __str__(self):
            return self.name

    costing_measures = [CostingMeasure.AREA, CostingMeasure.PERIMETER, CostingMeasure.QUANTITY]
    length_value = models.FloatField(null=False, blank=False)
    width_value = models.FloatField(null=False, blank=False)
    size_uom = models.CharField(max_length=30, null=False, blank=False,
                                choices=Measure.UNITS[Measure.DISTANCE])

    class Meta:
        abstract = True

    @property
    def layout(self):
        return Rectangle.Layout(width=self.width_value, 
            length=self.length_value, uom=self.size_uom)

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
        return Rectangle.binpacker(
            self.pack_width, self.pack_length, self.size_uom,
            rectangle.pack_width, rectangle.pack_length, rectangle.size_uom, 
            rotate)

    def estimate(self, rectangle, quantity):
        outs = self.pack(rectangle)
        estimate = quantity / outs
        return {
            CostingMeasure.AREA: self.area * estimate, 
            CostingMeasure.PERIMETER: self.perimeter * estimate, 
            CostingMeasure.QUANTITY: Quantity(pc=estimate)
        }

    # Returns the following:
    # layouts, count, usage, wastage, indices of rotated rectangles
    @classmethod
    def get_layout(cls, parent_layout, child_layout, rotate=False, name=None):
        def __round__(number):
            return round(number * 100, 2)

        def __get_usage__(pw, pl, pu, cw, cl, cu, count):
            d_cw = Distance(**{cu: cw})
            d_cl = Distance(**{cu: cl})
            d_pw = Distance(**{pu: pw})
            d_pl = Distance(**{pu: pl})
            ca = d_cw.mm * d_cl.mm * count
            pa = d_pw.mm * d_pl.mm
            return (ca / pa)

        def __get_layouts__(packer, rotated):
            layouts = []
            for key, rect in enumerate(packer.rect_list()):
                x, y, width, length, rid = rect
                is_rotated = key in rotated
                layout = Rectangle.Layout(key + 1, x, y, width, length, is_rotated)
                layouts.append(layout) 
            return layouts
        
        def __get_cut_count__(packer, bin_width, bin_length):
            unique_x = []
            unique_y = []

            for rect in packer:
                x = rect.x 
                y = rect.y 
                w = rect.width 
                h = rect.height
                if x not in unique_x:
                    if x > 0:
                        unique_x.append(x)
                    if x+w < bin_width:
                        unique_x.append(x+w)
                if y not in unique_y:
                    if y > 0:
                        unique_y.append(y)
                    if y+h < bin_length:
                        unique_y.append(y+h)
                        
            cut_count = len(unique_x) + len(unique_y)
            return cut_count

        parent_width = parent_layout.width
        parent_length = parent_layout.length
        parent_uom = parent_layout.uom
        child_width = child_layout.width
        child_length = child_layout.length
        child_uom = child_layout.uom
        
        packer = Rectangle.binpacker(
            parent_width, parent_length, parent_uom,
            child_width, child_length, child_uom, rotate)

        count = len(packer) if packer is not None else 0
        usage = __get_usage__(parent_width, parent_length, parent_uom, 
            child_width, child_length, child_uom, count) if packer is not None else 0
        wastage = 1 - usage
        # list the rectangles that have been rotated
        rotated = [i for i, x in enumerate(packer) if x.width != child_width and x.height != child_length] if \
            packer is not None and rotate else []
        layouts = __get_layouts__(packer, rotated)
        cut_count = __get_cut_count__(packer, parent_width, parent_length)

        layout_meta = Rectangle.LayoutMeta(layouts, count, 
            __round__(usage), __round__(wastage), rotated, name, cut_count)

        return layout_meta

    @classmethod
    def binpacker(cls, 
            parent_width, parent_length, parent_uom,
            child_width, child_length, child_uom, rotate):

        def __get_size__(unit, distance):
            d = Distance(**{unit: distance})
            return distance if unit == parent_uom else getattr(d, parent_uom)
        
        parent_width = __get_size__(parent_uom, parent_width)
        parent_length = __get_size__(parent_uom, parent_length) 
        child_width = __get_size__(child_uom, child_width)  
        child_length = __get_size__(child_uom, child_length) 

        parent_dimensions = (parent_width, parent_length)
        child_dimensions = (child_width, child_length)

        params = parent_dimensions + child_dimensions
        estimate_count = BinPacker.estimate_rectangles(*params)
        child_rects = [child_dimensions] * estimate_count
        parent_rect = [parent_dimensions]

        if rotate:
            packer1 = BinPacker.pack_rectangles(child_rects, parent_rect, True)
            packer2 = BinPacker.pack_rectangles(child_rects, parent_rect, False)
            if len(packer1) > 0 or len(packer2) > 0:
                p1 = packer1[0]
                p2 = packer2[0]
                return p1 if len(p1) > len(p2) else p2
            else:
                None
        else:
            x = BinPacker.pack_rectangles(child_rects, parent_rect, False)
            return x[0] if len(x) > 0 else None

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
    costing_measures = [CostingMeasure.VOLUME]
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

    def estimate(self, liquid, quantity):
        outs = self.pack(liquid)
        estimate = quantity / outs
        return {
            CostingMeasure.VOLUME: self.volume * estimate, 
        }

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

class RectangleLayoutSerializer(serializers.Serializer):
    i = serializers.IntegerField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    width = serializers.FloatField()
    length = serializers.FloatField()
    is_rotated = serializers.BooleanField()
    uom = serializers.CharField()

    def update(self, instance, validated_data):
        instance.b = validated_data.get('i', instance.b)
        instance.x = validated_data.get('x', instance.x)
        instance.y = validated_data.get('y', instance.y)
        instance.width = validated_data.get('width', instance.width)
        instance.length = validated_data.get('length', instance.length)
        instance.is_rotated = validated_data.get('is_rotated', instance.is_rotated)
        instance.uom = validated_data.get('uom', instance.uom)
        return instance

    def create(self, validated_data):
        return Rectangle.Layout(**validated_data)