from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance
from polymorphic.models import PolymorphicModel
from ..exceptions import SheetSizeInvalid


class Machine(PolymorphicModel):
    name = models.CharField(max_length=100)

    def validate_input(self, **kwargs):
        pass


class SheetfedPress(Machine):
    min_sheet_length = MeasurementField(measurement=Distance)
    max_sheet_length = MeasurementField(measurement=Distance)
    min_sheet_width = MeasurementField(measurement=Distance)
    max_sheet_width = MeasurementField(measurement=Distance)

    def validate_input(self, **kwargs):
        runsheet_width = kwargs.get('runsheet_width')
        runsheet_length = kwargs.get('runsheet_length')
        if runsheet_width is not None and runsheet_length is not None:
            length_valid = self.min_sheet_length.m <= runsheet_length.m \
                           <= self.max_sheet_length.m
            width_valid = self.min_sheet_width.m <= runsheet_width.m \
                          <= self.max_sheet_width.m
            if not (length_valid and width_valid):
                expected_min = "%s x %s" % (self.min_sheet_width, self.min_sheet_length)
                expected_max = "%s x %s" % (self.max_sheet_width, self.max_sheet_length)
                actual = "%s x %s" % (runsheet_width, runsheet_length)
                raise SheetSizeInvalid(expected_min, expected_max, actual)


class RollfedPress(Machine):
    min_sheet_width = MeasurementField(measurement=Distance)
    max_sheet_width = MeasurementField(measurement=Distance)

