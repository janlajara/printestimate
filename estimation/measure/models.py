from django.db import models
from measurement.base import MeasureBase, BidimensionalMeasure
from measurement.measures import Area, Time, Volume


# Create your models here.
class Measure:
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
        QUANTITY: [('pc', 'Piece')],
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
    def get_measure(cls, unit):
        measure = None
        for key in cls.UNITS.keys():
            for uom in cls.UNITS[key]:
                is_match = uom[0] == unit
                if is_match:
                    measure = key
                    break
        return measure


class Quantity(MeasureBase):
    STANDARD_UNIT = 'pc'
    UNITS = {
        'pc': 1.0
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
