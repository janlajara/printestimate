from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance


class Machine(models.Model):
    name = models.CharField(max_length=100)


class SheetfedPress(Machine):
    min_sheet_length = MeasurementField(measurement=Distance)
    max_sheet_length = MeasurementField(measurement=Distance)
    min_sheet_width = MeasurementField(measurement=Distance)
    max_sheet_width = MeasurementField(measurement=Distance)


class RollfedPress(Machine):
    min_sheet_width = MeasurementField(measurement=Distance)
    max_sheet_width = MeasurementField(measurement=Distance)

