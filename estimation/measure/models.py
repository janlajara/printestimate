from django.db import models
from measurement.base import MeasureBase, BidimensionalMeasure
from measurement.measures import Area, Time, Volume


# Create your models here.
class Measure:
    LENGTH = 'lnth'
    PERIMETER = 'pmtr'
    AREA = 'area'
    VOLUME = 'vlme'
    QUANTITY = 'qtty'
    TYPES = [
        (LENGTH, 'Length'),
        (PERIMETER, 'Perimeter'),
        (AREA, 'Area'),
        (VOLUME, 'Volume'),
        (QUANTITY, 'Quantity'),
    ]


class StandardUnits:
    class Speed:
        UOMS = {
            Measure.LENGTH: 'm_hr',
            Measure.PERIMETER: 'm_hr',
            Measure.AREA: 'sqm_hr',
            Measure.VOLUME: 'liter_hr',
            Measure.QUANTITY: 'unit_hr',
        }

    class Measure:
        UOMS = {
            Measure.LENGTH: 'm',
            Measure.PERIMETER: 'm',
            Measure.AREA: 'sqm',
            Measure.VOLUME: 'liter',
            Measure.QUANTITY: 'unit',
        }


class Quantity(MeasureBase):
    STANDARD_UNIT = 'unit'
    UNITS = {
        'unit': 1.0
    }


class QuantitySpeed(BidimensionalMeasure):
    PRIMARY_DIMENSION = Quantity
    REFERENCE_DIMENSION = Time


class AreaSpeed(BidimensionalMeasure):
    PRIMARY_DIMENSION = Area
    REFERENCE_DIMENSION = Time
    ALIAS = {
        'sqm_hr': 'sq_m__hr',
        'sqft_hr': 'sq_ft__hr',
    }


class VolumeSpeed(BidimensionalMeasure):
    PRIMARY_DIMENSION = Volume
    REFERENCE_DIMENSION = Time
