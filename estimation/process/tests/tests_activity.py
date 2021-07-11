import pytest
from core.utils.measures import Quantity
from measurement.measures import Time, Distance
from estimation.process.models import Workstation, Operation, \
    Activity, Speed, ActivityExpense
from estimation.exceptions import MeasurementMismatch


@pytest.fixture
def activity_speed(db):
    speed = Speed.objects.create(measure_value=0.5,
                                        measure_unit='m', speed_unit='min')
    return speed


@pytest.fixture
def activity_speed_factory(db):
    def create_activity_speed(measure_value: float, measure_unit: str, speed_unit=str):
        activity_speed = Speed.objects.create(measure_value=measure_value,
                                                    measure_unit=measure_unit,
                                                    speed_unit=speed_unit)
        return activity_speed
    return create_activity_speed


@pytest.fixture
def activity_factory(db):
    def create_activity(**kwargs):
        
        return Activity.objects.create_activity(**kwargs)
    return create_activity


@pytest.fixture
def activity(db, activity_factory:Activity, activity_speed: Speed):
    return activity_factory(name='HP Latex Cutter',
                           speed=activity_speed,
                           set_up=1,
                           tear_down=1)


@pytest.fixture
def activity_offset_printing(db, activity_speed_factory):
    speed = activity_speed_factory(120, 'pc', 'min')
    activity = Activity.objects.create_activity(name='GTO Offset Printing',
                                     speed=speed, set_up=1, tear_down=1)
    activity.add_expense('Labor', ActivityExpense.HOUR_BASED, 75)
    activity.add_expense('Electricity', ActivityExpense.HOUR_BASED, 150)
    activity.add_expense('Ink', ActivityExpense.MEASURE_BASED, 0.5)
    return activity


@pytest.fixture
def speed_factory(db):
    def create(measure_value, measure_unit, speed_unit):
        return Speed.objects.create(
            measure_value=measure_value, measure_unit=measure_unit,
            speed_unit=speed_unit)
    return create


@pytest.fixture
def workstation_factory(db):
    def create(name):
        return Workstation.objects.create(name=name)
    return create


@pytest.fixture
def korse_workstation(db, workstation_factory, speed_factory):
    korse_ws = workstation_factory(name='Korse 1C')
    korse_ws.add_expense('Electricity', 'hour', 100)
    korse_ws.add_expense('Depreciation', 'hour', 200)
    korse_ws.add_activity('Spot Color Printing', 1, 1, 
        speed_factory(10000, 'sheet', 'hr'), True)
    korse_ws.add_activity('Numbering', 1, 1, 
        speed_factory(10000, 'sheet', 'hr'), True)
    return korse_ws


def test_workstation__get_activities(db, korse_workstation):
    activities = korse_workstation.get_activities('Distance')
    assert len(activities) == 0

    activities = korse_workstation.get_activities('Quantity')
    assert len(activities) == 2


def test_activity_speed__get_distance_rate(db, activity_speed_factory):
    activity_speed = activity_speed_factory(0.5, 'm', 'min')
    assert activity_speed.rate is not None
    assert activity_speed.rate.m__hr == 30


def test_activity_speed__get_area_rate(db, activity_speed_factory):
    activity_speed = activity_speed_factory(1, 'sq_m', 'min')
    assert activity_speed.rate.sq_m__min == 1


def test_activity_speed__get_quantity_rate(db, activity_speed_factory):
    activity_speed = activity_speed_factory(30, 'pc', 'min')
    assert activity_speed.rate.pc__min == 30


def test_activity_speed__get_volume_rate(db, activity_speed_factory):
    activity_speed = activity_speed_factory(1, 'l', 'min')
    assert activity_speed.rate.l__min == 1


def test_activity__get_duration_short(db, activity: Activity):
    duration = activity.get_duration(Distance(m=10))
    # ((setup + teardown) * days) + base duration = 2.33 hrs
    # where
    #   = days = 1
    #   - setup = 1
    #   - teardown = 1
    #   - base duration = 10 / 0.5
    assert duration.hr == 2.33


def test_activity__get_duration_long(db, activity: Activity):
    duration = activity.get_duration(Distance(m=1000))
    # ((setup + teardown) * days) + base duration = 43.33 hrs
    # where
    #   - days = 5
    #   - setup = 1
    #   - teardown = 1
    #   - base duration = 1000 / 0.5
    assert duration.hr == 43.33


def test_activity__get_duration_with_contingency(db, activity: Activity):
    duration = activity.get_duration(Distance(m=1000), contingency=50)
    assert duration.hr == 64


def test_activity__get_duration_quantity_based(db, activity_offset_printing: Activity):
    duration = activity_offset_printing.get_duration(Quantity(sheet=2000))
    assert duration.hr == 2.28


def test_activity__get_duration_mismatch_measure(db, activity: Activity):
    with pytest.raises(MeasurementMismatch):
        duration = activity.get_duration(Time(sec=10))


def test_activity__get_duration_null_param(db, activity: Activity):
    with pytest.raises(Exception):
        duration = activity.get_duration(None)


def test_activity__no_expense(db, activity: Activity):
    cost = activity.get_cost(Distance(m=1))
    assert cost == 0


def test_activity__get_cost_hourly(db, activity: Activity):
    activity.add_expense('Labor', ActivityExpense.HOUR_BASED, 75)
    cost = activity.get_cost(Distance(m=10))
    assert cost.amount == 174.75


def test_activity__get_cost_measure(db, activity: Activity):
    activity.add_expense('Blade', ActivityExpense.MEASURE_BASED, 90)
    cost = activity.get_cost(Distance(m=10))
    assert cost.amount == 900


def test_activity__get_cost_flat(db, activity: Activity):
    activity.add_expense('Some fee', ActivityExpense.FLAT, 100)
    cost = activity.get_cost(Distance(m=10))
    assert cost.amount == 100


def test_activity__get_cost_with_contingency(db, activity: Activity):
    activity.add_expense('Labor', ActivityExpense.HOUR_BASED, 90)
    cost = activity.get_cost(Distance(m=1000), 50)
    assert cost.amount == 5760


def test_activity__get_cost_multiple(db, activity: Activity):
    activity.add_expense('Labor', ActivityExpense.HOUR_BASED, 75)
    activity.add_expense('Electricity', ActivityExpense.HOUR_BASED, 110)
    activity.add_expense('Blade', ActivityExpense.MEASURE_BASED, 90)
    activity.add_expense('Some fee', ActivityExpense.FLAT, 100)
    cost = activity.get_cost(Distance(m=10))
    assert float(cost.amount) == 1431.05


def test_activity__get_cost_quantity_based(db, activity_offset_printing: Activity):
    cost = activity_offset_printing.get_cost(Quantity(sheet=2000))
    assert cost.amount == 1513


def test_activity__get_cost_mismatch_measure(db, activity: Activity):
    activity.add_expense('Labor', ActivityExpense.HOUR_BASED, 75)
    with pytest.raises(MeasurementMismatch):
        cost = activity.get_cost(Time(sec=10))
