import functools
from django.db import models
from rest_framework import serializers  
from measurement.utils import guess
from measurement.base import MeasureBase, BidimensionalMeasure
from measurement.measures import Area, Time, Volume, Distance
from django_measurement.models import MeasurementField
import inflect

_inflect = inflect.engine()


# Create your models here.
class Measure:
    class Unit:
        def __init__(self, value, display_name):
            self.value = value
            self.display_name = display_name

    QUANTITY_UNITS = [
        ('set', 'Set'),
        ('pad', 'Pad'),
        ('box', 'Box'),
        ('booklet', 'Booklet'),
        ('ream', 'Ream'),
        ('pc', 'Piece'),
        ('sheet', 'Sheet')
    ]

    DISTANCE = 'Distance'
    AREA = 'Area'
    VOLUME = 'Volume'
    QUANTITY = 'Quantity'
    TIME = 'Time'
    UNITS = {
        DISTANCE: [('mm', 'Millimeter'),
                   ('cm', 'Centimeter'),
                   ('m', 'Meter'),
                   ('inch', 'Inch'),
                   ('ft', 'Feet')],
        AREA: [('sq_mm', 'Square millimeter'),
               ('sq_m', 'Square meter'),
               ('sq_inch', 'Square inch'),
               ('sq_ft', 'Square feet')],
        VOLUME: [('ml', 'Milliliter'),
                 ('cl', 'Centiliter'),
                 ('l', 'Liter'),
                 ('imperial_oz', 'Ounce')],
        QUANTITY: [('layout', 'Lay-out'),
                    ('count', 'Count')] + QUANTITY_UNITS,
        TIME: [('sec', 'Second'),
               ('min', 'Minute'),
               ('hr', 'Hour'),
               ('day', 'Day')]
    }

    PRIMARY_UNITS = UNITS[DISTANCE] + UNITS[AREA] + \
        UNITS[VOLUME] + UNITS[QUANTITY]
    TIME_UNITS = UNITS[TIME]

    STANDARD_UNITS = {
        DISTANCE: 'm',
        AREA: 'sqm',
        VOLUME: 'l',
        QUANTITY: 'pc',
    }

    STANDARD_SPEED_UNITS = {
        DISTANCE: 'm__hr',
        AREA: 'sqm__hr',
        VOLUME: 'l__hr',
        QUANTITY: 'pc__hr',
    }

    @classmethod
    def get_units(cls, measure):
        return cls.UNITS.get(measure)

    @classmethod
    def get_measure(cls, unit):
        measure = None
        for key in cls.UNITS.keys():
            for uom in cls.UNITS[key]:
                is_match = uom[0] == unit
                if is_match:
                    measure = key
                    break
        return measure



class CostingMeasure:
    LENGTH = 'length'
    AREA = 'area'
    VOLUME = 'volume'
    QUANTITY = 'quantity'
    PERIMETER = 'perimeter'
    TYPES = [
        (LENGTH, 'Length'),
        (AREA, 'Area'),
        (VOLUME, 'Volume'),
        (QUANTITY, 'Quantity'),
        (PERIMETER, 'Perimeter'),
    ]

    def __init__(self, name, units):
        self.name = name
        self.units = units

    @classmethod
    def create(cls, name):
        uom_choices = CostingMeasure.get_unit_of_measure_choices([name])
        units = []

        for uom_choice in uom_choices:
            unit = Measure.Unit(uom_choice[0], uom_choice[1])
            units.append(unit)

        costing_measure = CostingMeasure(name, units)
        return costing_measure
    
    @classmethod
    def get_all_measures(cls):
        measures = []

        for type in CostingMeasure.TYPES:
            measure_name = type[0]
            measure = CostingMeasure.create(measure_name)
            measures.append(measure)
        
        return measures

    @classmethod
    def get_base_measure(cls, costing_measure):
        mapping = {
            cls.LENGTH: Measure.DISTANCE,
            cls.AREA: Measure.AREA,
            cls.VOLUME: Measure.VOLUME,
            cls.QUANTITY: Measure.QUANTITY,
            cls.PERIMETER: Measure.DISTANCE}
        return mapping.get(costing_measure, None)

    @classmethod
    def get_unit_of_measure_choices(cls, costing_measures):
        base_measures = [cls.get_base_measure(x) for x in costing_measures]
        choices = []
        for x in base_measures:
            choices += Measure.UNITS[x]
        return choices


class Quantity(MeasureBase):
    STANDARD_UNIT = 'pc'
    UNITS = {
        'pc': 1.0,
        'sheet': 1.0,
        'set': 1.0,
        'layout': 1.0,
        'pad': 1.0,
        'box': 1.0,
        'booklet': 1.0,
        'ream': 1.0,
        'count': 1.0
    }


class QuantitySpeed(BidimensionalMeasure):
    PRIMARY_DIMENSION = Quantity
    REFERENCE_DIMENSION = Time


class AreaSpeed(BidimensionalMeasure):
    PRIMARY_DIMENSION = Area
    REFERENCE_DIMENSION = Time
    ALIAS = {
        'sqm_min': 'sq_m__min',
        'sqm_hr': 'sq_m__hr',
        'sqft_hr': 'sq_ft__hr',
    }


class VolumeSpeed(BidimensionalMeasure):
    PRIMARY_DIMENSION = Volume
    REFERENCE_DIMENSION = Time


class MeasurementSerializerField(serializers.Field):

    def __init__(self, display_unit=None, decimal_places=None, **kwargs):
        super().__init__(**kwargs)
        self.display_unit = display_unit
        self.decimal_places = decimal_places

    def _format(self, value, unit_singular, unit_plural, decimal_places=None):
        unit = unit_plural
        if value == 1:
            unit = unit_singular
        if decimal_places is not None:
            value = round(value, decimal_places)
        return '%s %s' % (value, unit)

    def to_representation(self, value):
        rep = self._format(
            value.value, value.unit , 
            _inflect.plural(value.unit), self.decimal_places)
        
        if self.display_unit is not None:
            rep = self._format(
                getattr(value, self.display_unit),
                self.display_unit,
                _inflect.plural(self.display_unit), self.decimal_places)

        return rep

    def to_internal_value(self, data):
        split = data.split(' ') 
        if len(split) == 2:
            value = split[0]
            unit = split[1]
            measurement = guess(value, unit)
            return measurement
        else:
            raise ValueError('Incorrect format for MeasurementSerializerField: %s' % data)
