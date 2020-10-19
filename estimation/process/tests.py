import pytest
from measurement.measures import Time, Distance
from .models import Process, ProcessSpeed, ProcessExpense
from core.utils.measures import Quantity
from ..exceptions import MeasurementMismatch


@pytest.fixture
def process_speed(db):
    speed = ProcessSpeed.objects.create(measure_value=0.5,
                                        measure_unit='m', speed_unit='min')
    return speed


@pytest.fixture
def process_speed_factory(db):
    def create_process_speed(measure_value: float, measure_unit: str, speed_unit=str):
        process_speed = ProcessSpeed.objects.create(measure_value=measure_value,
                                                    measure_unit=measure_unit,
                                                    speed_unit=speed_unit)
        return process_speed
    return create_process_speed


@pytest.fixture
def process_factory(db):
    def create_process(**kwargs):
        return Process.objects.create(**kwargs)
    return create_process


@pytest.fixture
def process(db, process_factory:Process, process_speed: ProcessSpeed):
    return process_factory(name='HP Latex Cutter',
                           speed=process_speed,
                           set_up=Time(hr=1),
                           tear_down=Time(hr=1))


@pytest.fixture
def process_offset_printing(db, process_speed_factory):
    speed = process_speed_factory(120, 'pc', 'min')
    process = Process.objects.create(name='GTO Offset Printing',
                                     speed=speed,
                                     set_up=Time(hr=1),
                                     tear_down=Time(hr=1))
    process.add_expense('Labor', ProcessExpense.HOUR_BASED, 75)
    process.add_expense('Electricity', ProcessExpense.HOUR_BASED, 150)
    process.add_expense('Ink', ProcessExpense.MEASURE_BASED, 0.5)
    return process


def test_process_speed__get_distance_rate(db, process_speed_factory):
    process_speed = process_speed_factory(0.5, 'm', 'min')
    assert process_speed.rate is not None
    assert process_speed.rate.m__hr == 30


def test_process_speed__get_area_rate(db, process_speed_factory):
    process_speed = process_speed_factory(1, 'sq_m', 'min')
    assert process_speed.rate.sq_m__min == 1


def test_process_speed__get_quantity_rate(db, process_speed_factory):
    process_speed = process_speed_factory(30, 'pc', 'min')
    assert process_speed.rate.pc__min == 30


def test_process_speed__get_volume_rate(db, process_speed_factory):
    process_speed = process_speed_factory(1, 'l', 'min')
    assert process_speed.rate.l__min == 1


def test_process__get_duration_short(db, process: Process):
    duration = process.get_duration(Distance(m=10))
    # ((setup + teardown) * days) + base duration = 2.33 hrs
    # where
    #   = days = 1
    #   - setup = 1
    #   - teardown = 1
    #   - base duration = 10 / 0.5
    assert duration.hr == 2.33


def test_process__get_duration_long(db, process: Process):
    duration = process.get_duration(Distance(m=1000))
    # ((setup + teardown) * days) + base duration = 43.33 hrs
    # where
    #   - days = 5
    #   - setup = 1
    #   - teardown = 1
    #   - base duration = 1000 / 0.5
    assert duration.hr == 43.33


def test_process__get_duration_with_contingency(db, process: Process):
    duration = process.get_duration(Distance(m=1000), contingency=50)
    assert duration.hr == 64


def test_process__get_duration_quantity_based(db, process_offset_printing: Process):
    duration = process_offset_printing.get_duration(Quantity(sheet=2000))
    assert duration.hr == 2.28


def test_process__get_duration_mismatch_measure(db, process: Process):
    with pytest.raises(MeasurementMismatch):
        duration = process.get_duration(Time(sec=10))


def test_process__get_duration_null_param(db, process: Process):
    with pytest.raises(Exception):
        duration = process.get_duration(None)


def test_process__no_expense(db, process: Process):
    cost = process.get_cost(Distance(m=1))
    assert cost == 0


def test_process__get_cost_hourly(db, process: Process):
    process.add_expense('Labor', ProcessExpense.HOUR_BASED, 75)
    cost = process.get_cost(Distance(m=10))
    assert cost.amount == 174.75


def test_process__get_cost_measure(db, process: Process):
    process.add_expense('Blade', ProcessExpense.MEASURE_BASED, 90)
    cost = process.get_cost(Distance(m=10))
    assert cost.amount == 900


def test_process__get_cost_flat(db, process: Process):
    process.add_expense('Some fee', ProcessExpense.FLAT, 100)
    cost = process.get_cost(Distance(m=10))
    assert cost.amount == 100


def test_process__get_cost_with_contingency(db, process: Process):
    process.add_expense('Labor', ProcessExpense.HOUR_BASED, 90)
    cost = process.get_cost(Distance(m=1000), 50)
    assert cost.amount == 5760


def test_process__get_cost_multiple(db, process: Process):
    process.add_expense('Labor', ProcessExpense.HOUR_BASED, 75)
    process.add_expense('Electricity', ProcessExpense.HOUR_BASED, 110)
    process.add_expense('Blade', ProcessExpense.MEASURE_BASED, 90)
    process.add_expense('Some fee', ProcessExpense.FLAT, 100)
    cost = process.get_cost(Distance(m=10))
    assert float(cost.amount) == 1431.05


def test_process__get_cost_quantity_based(db, process_offset_printing: Process):
    cost = process_offset_printing.get_cost(Quantity(sheet=2000))
    assert cost.amount == 1513


def test_process__get_cost_mismatch_measure(db, process: Process):
    process.add_expense('Labor', ProcessExpense.HOUR_BASED, 75)
    with pytest.raises(MeasurementMismatch):
        cost = process.get_cost(Time(sec=10))
