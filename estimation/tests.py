import pytest
from measurement.measures import Time, Distance
from .measure.models import Measure
from .process.models import Process, ProcessSpeed


@pytest.fixture
def process_speed(db):
    speed = ProcessSpeed.objects.create(measure_value=0.5,
                                        measure_unit='m', speed_unit='min')
    return speed


@pytest.fixture
def process(db, process_speed: ProcessSpeed):
    process = Process.objects.create(name='GTO Printing',
                                     speed=process_speed,
                                     set_up=Time(hr=1),
                                     tear_down=Time(hr=1))
    return process


@pytest.fixture
def process_speed_factory(db):
    def create_process_speed(measure_value: float, measure_unit: str, speed_unit=str):
        process_speed = ProcessSpeed.objects.create(measure_value=measure_value,
                                                    measure_unit=measure_unit,
                                                    speed_unit=speed_unit)
        return process_speed
    return create_process_speed


# Create your tests here.
def test_measure__get_measure_distance(db):
    measure = Measure.get_measure('m')
    assert measure == Measure.DISTANCE


def test_measure__get_measure_area(db):
    measure = Measure.get_measure('sq_m')
    assert measure == Measure.AREA


def test_measure__get_measure_quantity(db):
    measure = Measure.get_measure('pc')
    assert measure == Measure.QUANTITY


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


def test_process__no_expense(db, process: Process):
    cost = process.get_cost(Distance(m=1))
    assert cost == 0

