from django.db import models
from djmoney.models.fields import MoneyField
from django_measurement.models import MeasurementField
from measurement.base import BidimensionalMeasure
from measurement.measures import Time
from ..measure.models import Measure, StandardUnits


# Create your models here.
class Process(models.Model):
    name = models.CharField(max_length=40)
    measure = models.CharField(max_length=4, choices=Measure.TYPES)
    speed = MeasurementField(measurement=BidimensionalMeasure)

    @property
    def flat_rate(self):
        flat_rate = self._get_total_expenses(ProcessExpense.FLAT)
        return flat_rate

    @property
    def measure_rate(self):
        measure_rate = self._get_total_expenses(ProcessExpense.MEASURE_BASED)
        return measure_rate

    @property
    def hourly_rate(self):
        hourly_rate = self._get_total_expenses(ProcessExpense.HOUR_BASED)
        return hourly_rate

    def get_duration(self, measurement):
        duration = 0
        measure_uom = StandardUnits.Measure.UOMS[self.measure]
        speed_uom = StandardUnits.Speed.UOMS[self.measure]
        if measurement is not None and self.speed is not None:
            mval = getattr(measurement, measure_uom)
            sval = getattr(self.speed, speed_uom)
            if mval is not None and sval is not None:
                duration = mval / sval
        return Time(hr=duration)

    def get_cost(self, measurement):
        cost = 0
        duration = self.get_duration(measurement)
        time_cost = self.hourly_rate * duration.hr
        measure_cost = 0
        measure_uom = StandardUnits.Measure.UOMS[self.measure]
        if measurement is not None:
            mval = getattr(measurement, measure_uom)
            if mval is not None:
                measure_cost = mval * self.measure_rate
        cost = self.flat_rate + time_cost + measure_cost
        return cost

    def _get_total_expenses(self, expense_type):
        total_rate = 0
        expenses = ProcessExpense.objects.filter(process=self, type=expense_type)
        for expense in expenses:
            total_rate += expense.rate
        return total_rate


class ProcessExpense(models.Model):
    HOUR_BASED = 'hour'
    MEASURE_BASED = 'mesr'
    FLAT = 'flat'
    TYPES = [
        (HOUR_BASED, 'Hour-based'),
        (MEASURE_BASED, 'Measure-based'),
        (FLAT, 'Flat')
    ]
    name = models.CharField(max_length=40)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='process_expense')
    type = models.CharField(max_length=4, choices=TYPES)
    rate = MoneyField(default=0, max_digits=14, decimal_places=2, default_currency='PHP')
