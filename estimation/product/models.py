from django.db import models
from django_measurement.models import MeasurementField
from measurement.measures import Distance


class Product(models.Model):
    name = models.CharField(max_length=40)
    length = MeasurementField(measurement=Distance)
    width = MeasurementField(measurement=Distance)