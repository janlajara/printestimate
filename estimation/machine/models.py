from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance


class Machine(models.Model):
    name = models.CharField(max_length=100)


class SheetfedPress(Machine):
    min_runsheet_length = MeasurementField(measurement=Distance)
    max_runsheet_length = MeasurementField(measurement=Distance)
    min_runsheet_width = MeasurementField(measurement=Distance)
    max_runsheet_width = MeasurementField(measurement=Distance)


class RollfedPress(Machine):
    min_runsheet_width = MeasurementField(measurement=Distance)
    max_runsheet_width = MeasurementField(measurement=Distance)

