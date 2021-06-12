import math
from decimal import Decimal
from django.db import models
from djmoney.models.fields import MoneyField
from django_measurement.models import MeasurementField
from measurement.measures import Time, Speed as MeasureSpeed
from core.utils.measures import Quantity, Measure, AreaSpeed, VolumeSpeed, QuantitySpeed
from inventory.models import Item
from estimation.machine.models import Machine
from estimation.product.models import Material
from estimation.exceptions import MeasurementMismatch, MaterialTypeMismatch


# Create your models here.
class Process(models.Model):
    name = models.CharField(max_length=40)


class Workstation(models.Model):
    name = models.CharField(max_length=50)

    def add_operation(self, name, material_type, prerequisite=None, machine=None):
        operation = Operation.objects.create(
            workstation=self, name=name, 
            material_type=material_type,
            prerequisite=prerequisite,
            machine=machine)
        return operation

    def add_activity(self, name, set_up, tear_down, 
            speed, include_presets=False):
        activity = Activity.objects.create_activity(
            name=name, set_up=set_up, tear_down=tear_down,
            speed=speed, workstation=self)
        if (include_presets):
            activity.activity_expenses.set(self.activity_expenses.all())
        return activity

    def add_expense(self, name, type, rate):
        expense = ActivityExpense.objects.create(
            workstation=self, name=name, type=type, rate=rate)
        return expense


class Operation(models.Model):
    # TO DO: Rework these choices with more elegant code
    class CostingMeasure:
        LENGTH = 'length'
        AREA = 'area'
        VOLUME = 'volume'
        QUANTITY = 'quantity'
        PERIMETER = 'perimeter'
        TIME = 'time'
        TYPES = [
            (LENGTH, 'Length'),
            (AREA, 'Area'),
            (VOLUME, 'Volume'),
            (QUANTITY, 'Quantity'),
            (PERIMETER, 'Perimeter'),
            (TIME, 'Time'),
        ]
    name = models.CharField(max_length=50)
    process = models.ForeignKey(Process, on_delete=models.SET_NULL,
        related_name='operations', blank=True, null=True)
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE,
        related_name='operations')
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL,
        blank=True, null=True)
    costing_measure = models.CharField(max_length=15, choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)
    material_type = models.CharField(max_length=15, choices=Item.TYPES, 
        default=Item.OTHER)
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, 
        related_name='operations', blank=True, null=True)

    @property
    def costing_measure_choices(self):
        def __get(costing_measures):
            return [measure for measure in CostingMeasure.TYPES 
                if measure[0] in costing_measures]
        material_type = self.material_type
        mapping = {
            Item.TAPE: _get([
                CostingMeasure.LENGTH, 
                CostingMeasure.QUANTITY]),
            Item.LINE: _get([
                CostingMeasure.LENGTH, 
                CostingMeasure.QUANTITY]),
            Item.PAPER: _get([
                CostingMeasure.AREA, 
                CostingMeasure.PERIMETER, 
                CostingMeasure.QUANTITY]),
            Item.PANEL: _get([
                CostingMeasure.AREA, 
                CostingMeasure.PERIMETER, 
                CostingMeasure.QUANTITY]),
            Item.LIQUID: _get([
                CostingMeasure.VOLUME, 
                CostingMeasure.QUANTITY]),
            Item.OTHER: _get([CostingMeasure.QUANTITY])
        }
        return mapping.get(self.material_type, Item.OTHER)

    @property
    def measure(self):
        mapping = {
            Operation.CostingMeasure.LENGTH: Measure.DISTANCE,
            Operation.CostingMeasure.AREA: Measure.AREA,
            Operation.CostingMeasure.VOLUME: Measure.VOLUME,
            Operation.CostingMeasure.QUANTITY: Measure.QUANTITY,
            Operation.CostingMeasure.PERIMETER: Measure.DISTANCE,
            Operation.CostingMeasure.TIME: Measure.TIME}
        return mapping.get(self.costing_measure, None)

    @property
    def next_sequence(self):
        count = OperationStep.objects.filter(operation=self).count() + 1
        return count

    def add_step(self, activity, notes=None, sequence=None):
        if activity.measure != self.measure:
            raise MeasurementMismatch(activity.measure, self.measure)

        temp = sequence if sequence is not None else self.next_sequence
        if sequence is not None:
            steps_to_move = self.operation_steps.filter(sequence__gte=sequence)
            for step in steps_to_move:
                step.sequence += 1
                step.save()
        
        return OperationStep.objects.create(
            operation=self, activity=activity, notes=notes,
            sequence=temp)

    def move_step(self, step_to_move, sequence):
        if step_to_move.sequence < sequence:
            steps_to_move = self.operation_steps.filter(
                sequence__gt=step_to_move.sequence, 
                sequence__lte=sequence)
            for step in steps_to_move:
                step.sequence -= 1
                step.save()
        else:
            steps_to_move = self.operation_steps.filter(
                sequence__gte=sequence,
                sequence__lt=step_to_move.sequence)
            for step in steps_to_move:
                step.sequence += 1
                step.save()
        step_to_move.sequence = sequence
        step_to_move.save()

    def delete_step(self, step_to_delete):
        steps_to_move = self.operation_steps.filter(
            sequence__gt=step_to_delete.sequence)
        for step in steps_to_move:
            step.sequence -= 1
            step.save()
        step_to_delete.delete()

    def get_measurement(self, input:Item, output:Material, quantity):
        if self.material_type == input.type == output.type:
            
            if self.machine is not None:
                estimate = self.machine.estimate(input, output, quantity)
                return estimate.run_count

            materials_per_item = math.floor(input.properties.pack(output))
            item_count_needed = output.quantity * quantity / materials_per_item
            return Quantity(pc=item_count_needed)
        else:
            raise MaterialTypeMismatch(self.material.type, item.type, self.material_type)

    def get_duration(self, measurement, contingency=0):
        total_duration = 0
        for step in self.operation_steps.all():
            duration = step.activity.get_duration(
                measurement=measurement, contingency=contingency)
            total_duration += duration.hr
        return Time(hr=total_duration)

    def get_cost(self, measurement, contingency=0):
        total_cost = 0
        for step in self.operation_steps.all():
            cost = step.activity.get_cost(
                measurement=measurement, contingency=contingency)
            total_cost += cost
        return total_cost


class Speed(models.Model):
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
            rate = MeasureSpeed(**data)
        return rate


class ActivityManager(models.Manager):
    def create_activity(self, name, 
            set_up, tear_down, speed, workstation=None):
        activity = Activity.objects.create(
            name=name, workstation=workstation,
            speed=speed,
            set_up=Time(hr=set_up),
            tear_down=Time(hr=tear_down))
        return activity


class Activity(models.Model):
    objects = ActivityManager()
    name = models.CharField(max_length=40)
    workstation = models.ForeignKey(Workstation, on_delete=models.SET_NULL,
        related_name='activities', blank=True, null=True)
    speed = models.OneToOneField(Speed, on_delete=models.CASCADE)
    set_up = MeasurementField(measurement=Time, null=True, blank=False)
    tear_down = MeasurementField(measurement=Time, null=True, blank=False)

    @property
    def measure(self):
        return self.speed.measure

    @property
    def measure_unit(self):
        return self.speed.measure_unit

    @property
    def flat_rate(self):
        flat_rate = self._get_total_expenses(ActivityExpense.FLAT)
        return flat_rate

    @property
    def measure_rate(self):
        measure_rate = self._get_total_expenses(ActivityExpense.MEASURE_BASED)
        return measure_rate

    @property
    def hourly_rate(self):
        hourly_rate = self._get_total_expenses(ActivityExpense.HOUR_BASED)
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

        duration = self.get_duration(measurement, contingency)
        time_cost = self.hourly_rate * Decimal(duration.hr)
        measure_cost = 0
        measure_uom = Measure.STANDARD_UNITS[self.speed.measure]

        # convert input measurement to standard measurement
        # and multiply it by the measure rate
        if measure_uom is not None and measurement is not None:
            mval = getattr(measurement, measure_uom)
            if mval is not None:
                measure_cost = Decimal(mval) * self.measure_rate

        cost = self.flat_rate + time_cost + measure_cost
        return round(cost, 2)

    def add_expense(self, name, expense_type, rate):
        expense = ActivityExpense.objects.create(name=name,
                                                type=expense_type,
                                                rate=rate)
        expense.activities.add(self)
        expense.save()
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
        expenses = ActivityExpense.objects.filter(activities=self, type=expense_type)
        for expense in expenses:
            total_rate += expense.rate
        return total_rate


class ActivityExpense(models.Model):
    HOUR_BASED = 'hour'
    MEASURE_BASED = 'measure'
    FLAT = 'flat'
    TYPES = [
        (HOUR_BASED, 'Hour-based'),
        (MEASURE_BASED, 'Measure-based'),
        (FLAT, 'Flat')
    ]
    name = models.CharField(max_length=40)
    activities = models.ManyToManyField(Activity, 
        related_name='activity_expenses', blank=True)
    workstation = models.ForeignKey(Workstation, on_delete=models.SET_NULL,
        related_name='activity_expenses', blank=True, null=True)
    type = models.CharField(max_length=7, choices=TYPES)
    rate = MoneyField(default=0, max_digits=14, decimal_places=2, 
        default_currency='PHP')


class OperationStep(models.Model):
    sequence = models.IntegerField(default=0)
    operation = models.ForeignKey(Operation, related_name='operation_steps',
        on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='operation_steps',
        on_delete=models.CASCADE)
    notes = models.CharField(max_length=20, blank=True, null=True)