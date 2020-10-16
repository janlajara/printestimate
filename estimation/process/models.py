import math
from decimal import Decimal
from django.db import models
from djmoney.models.fields import MoneyField
from django_measurement.models import MeasurementField
from measurement.measures import Time, Speed
from core.utils.measures import Measure, AreaSpeed, VolumeSpeed, QuantitySpeed
from ..exceptions import MeasurementMismatch


# Create your models here.
class ProcessSpeed(models.Model):
    measure_value = models.DecimalField(decimal_places=4, max_digits=12)
    measure_unit = models.CharField(max_length=20, choices=Measure.PRIMARY_UNITS)
    speed_unit = models.CharField(max_length=5, choices=Measure.TIME_UNITS)

    @property
    def measure(self):
        if self.measure_unit is not None:
            return Measure.get_measure(self.measure_unit)

    @property
    def rate(self):
        param = '%s__%s' % (self.measure_unit, self.speed_unit)
        data = {param: self.measure_value}
        rate = None
        if self.measure == Measure.AREA:
            rate = AreaSpeed(**data)
        elif self.measure == Measure.QUANTITY:
            rate = QuantitySpeed(**data)
        elif self.measure == Measure.VOLUME:
            rate = VolumeSpeed(**data)
        else:
            rate = Speed(**data)
        return rate


class Process(models.Model):
    name = models.CharField(max_length=40)
    speed = models.OneToOneField(ProcessSpeed, on_delete=models.RESTRICT)
    set_up = MeasurementField(measurement=Time, null=True, blank=False)
    tear_down = MeasurementField(measurement=Time, null=True, blank=False)

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

    def get_duration(self, measurement, contingency=0, hours_per_day=10):
        self._validate_measurement(measurement)

        # factor hours for setup and teardown, multiplied by estimate num of days
        def __compute_overall(base_duration):
            overall = base_duration
            if self.set_up is not None and self.tear_down is not None:
                misc_hrs = (self.set_up.hr + self.tear_down.hr)
                run_hours = hours_per_day - misc_hrs
                estimate_days = math.ceil(base_duration / run_hours)
                overall = base_duration + (misc_hrs * estimate_days)
            return round(overall, 2)

        duration = 0
        measure_uom = Measure.STANDARD_UNITS[self.speed.measure]
        speed_uom = Measure.STANDARD_SPEED_UNITS[self.speed.measure]

        if measure_uom is not None and speed_uom is not None and \
                measurement is not None and self.speed is not None:
            mval = getattr(measurement, measure_uom)
            sval = getattr(self.speed.rate, speed_uom)

            if mval is not None and sval is not None:
                base = mval / sval
                multiplier = (contingency / 100) + 1
                duration = __compute_overall(base * multiplier)

        return Time(hr=duration)

    def get_cost(self, measurement, contingency=0):
        self._validate_measurement(measurement)

        cost = 0
        duration = self.get_duration(measurement, contingency)
        time_cost = self.hourly_rate * Decimal(duration.hr)
        measure_cost = 0
        measure_uom = Measure.STANDARD_UNITS[self.speed.measure]

        if measure_uom is not None and measurement is not None:
            mval = getattr(measurement, measure_uom)
            if mval is not None:
                measure_cost = Decimal(mval) * self.measure_rate

        cost = self.flat_rate + time_cost + measure_cost
        return round(cost, 2)

    def add_expense(self, name, expense_type, rate):
        expense = ProcessExpense.objects.create(process=self,
                                                name=name,
                                                type=expense_type,
                                                rate=rate)
        return expense

    def _validate_measurement(self, measurement):
        try:
            if measurement is not None:
                uom = self.speed.measure_unit
                converted = getattr(measurement, uom)
                # if still successful at this point, then validation is done
                return
            else:
                raise Exception("Expected parameter 'measurement' is null")
        except AttributeError as e:
            uom = self.speed.measure_unit
            measure = Measure.get_measure(uom)
            raise MeasurementMismatch(measurement, measure)

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
