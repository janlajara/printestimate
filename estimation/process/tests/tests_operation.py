import pytest
from core.utils.measures import Quantity
from estimation.process.models import Workstation, Speed


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
    speed = speed_factory(10000, 'sheet', 'hr')

    korse_ws = workstation_factory(name='Korse 1C')
    korse_ws.add_expense('Electricity', 'hour', 100)
    korse_ws.add_expense('Depreciation', 'hour', 200)
    korse_ws.add_activity('Spot Color Printing', 1, 1, 
        speed_factory(10000, 'sheet', 'hr'), True)
    korse_ws.add_activity('Numbering', 1, 1, 
        speed_factory(10000, 'sheet', 'hr'), True)
    return korse_ws


def test_workstation__add_activity(db, workstation_factory, speed_factory):
    speed = speed_factory(10000, 'sheet', 'hr')
    korse_ws = workstation_factory(name='Korse 1C')
    activity = korse_ws.add_activity('Spot Color Printing', 1, 1, speed)

    assert activity in korse_ws.activities.all() 


def test_workstation__add_activity_with_preset_expense(db, workstation_factory, speed_factory):
    korse_ws = workstation_factory(name='Korse 1C')
    elec_expense = korse_ws.add_expense('Electricity', 'hour', 100)
    dep_expense = korse_ws.add_expense('Depreciation', 'hour', 200)
    
    assert len(korse_ws.activity_expenses.all()) == 2

    activity1 = korse_ws.add_activity('Spot Color Printing', 1, 1, 
        speed_factory(10000, 'sheet', 'hr'), True)
    activity2 = korse_ws.add_activity('Numbering', 1, 1, 
        speed_factory(10000, 'sheet', 'hr'), True)

    assert len(activity1.activity_expenses.all()) == 2 and \
        len(activity2.activity_expenses.all()) == 2
    assert len(korse_ws.activities.all()) == 2


def test_workstation__add_operation(db, workstation_factory, speed_factory):
    korse_ws = workstation_factory(name='Korse 1C')
    speed = speed_factory(10000, 'sheet', 'hr')

    operation = korse_ws.add_operation('CMYK Printing', speed)
    assert operation.workstation == korse_ws


def test_operation__add_delete_step(db, korse_workstation, speed_factory):
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')

    speed = speed_factory(10000, 'sheet', 'hr')
    operation = korse_workstation.add_operation('2-Color Printing', speed)
    step1 = operation.add_step(spot_printing, '1st color')
    step2 = operation.add_step(spot_printing, '2nd color')

    assert len(operation.operation_steps.all()) == 2
    assert step1.sequence == 1
    assert step2.sequence == 2

    operation.delete_step(step1)
    step2.refresh_from_db()
    assert len(operation.operation_steps.all()) == 1
    assert step2.sequence == 1


def test_operation__add_step_inbetween(db, korse_workstation, speed_factory):
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')

    speed = speed_factory(10000, 'sheet', 'hr')
    operation = korse_workstation.add_operation('3-Color Printing', speed)
    step2 = operation.add_step(spot_printing, '2nd color')
    step3 = operation.add_step(spot_printing, '3rd color')
    assert step2.sequence == 1 and step3.sequence == 2

    step1 = operation.add_step(spot_printing, '1st color', 1)
    step2.refresh_from_db()
    step3.refresh_from_db()
    assert step1.sequence == 1
    assert step2.sequence == 2
    assert step3.sequence == 3


def test_operation__move_step(db, korse_workstation, speed_factory):
    def refresh_from_db(steps):
        for step in steps:
            step.refresh_from_db()
        
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')

    speed = speed_factory(10000, 'sheet', 'hr')
    operation = korse_workstation.add_operation('5-Color Printing', speed)
    steps = []
    for num in range(5):
        step = operation.add_step(spot_printing, 'color ' + str(num+1))
        steps.append(step)
        
    operation.move_step(steps[2], 1)
    refresh_from_db(steps)
    assert steps[2].sequence == 1 and steps[0].sequence == 2 and \
        steps[1].sequence == 3 and steps[3].sequence == 4 and steps[4].sequence == 5

    operation.move_step(steps[1], 5)
    refresh_from_db(steps)
    assert steps[2].sequence == 1 and steps[0].sequence == 2 and \
        steps[3].sequence == 3 and steps[4].sequence == 4 and steps[1].sequence == 5


def test_operation__get_duration_and_rate(db, korse_workstation, speed_factory):
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')
    speed = speed_factory(10000, 'sheet', 'hr')
    operation = korse_workstation.add_operation('2-Color Printing', speed)
    operation.add_step(spot_printing, '1st Color')
    operation.add_step(spot_printing, '2nd Color')
    
    duration = operation.get_duration(Quantity(sheet=10000))
    assert duration.hr == 6

    cost = operation.get_cost(Quantity(sheet=10000))
    assert cost.amount == 1800