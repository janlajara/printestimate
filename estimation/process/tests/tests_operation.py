import pytest, math
from core.utils.measures import Quantity
from estimation.machine.models import Machine
from estimation.process.models import Workstation, Operation, Speed
from estimation.product.models import Component
from inventory.models import BaseStockUnit, AlternateStockUnit, Item


@pytest.fixture
def item_factory(db):
    def create_item(**kwargs):
        buom = BaseStockUnit.objects.create(name='sheet', abbrev='sht')
        auom = AlternateStockUnit.objects.create(name='ream', abbrev='rm')
        auom.base_stock_units.add(buom)
        item = Item.objects.create_item(base_uom=buom,
                                        alternate_uom=auom, 
                                        **kwargs)
        return item
    return create_item


@pytest.fixture
def component_factory(db):
    def create_component(**kwargs):
        return Component.objects.create(**kwargs)
    return create_component


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


@pytest.fixture
def korse_machine(db):
    return Machine.objects.create_machine(name='KORSE Press', 
        type=Machine.PRESS, uom='inch')

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


def test_workstation__add_operation(db, workstation_factory):
    korse_ws = workstation_factory(name='Korse 1C')
    operation = korse_ws.add_operation(
        name='CMYK Printing', material_type=Item.PAPER)
    assert operation.workstation == korse_ws


def test_operation__add_delete_step(db, korse_workstation):
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')

    operation = korse_workstation.add_operation(
        name='2-Color Printing', material_type=Item.PAPER) 
    step1 = operation.add_step(spot_printing, '1st color')
    step2 = operation.add_step(spot_printing, '2nd color')

    assert len(operation.operation_steps.all()) == 2
    assert step1.sequence == 1
    assert step2.sequence == 2

    operation.delete_step(step1)
    step2.refresh_from_db()
    assert len(operation.operation_steps.all()) == 1
    assert step2.sequence == 1


def test_operation__add_step_inbetween(db, korse_workstation):
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')

    operation = korse_workstation.add_operation(
        name='3-Color Printing', material_type=Item.PAPER)
    step2 = operation.add_step(spot_printing, '2nd color')
    step3 = operation.add_step(spot_printing, '3rd color')
    assert step2.sequence == 1 and step3.sequence == 2

    step1 = operation.add_step(spot_printing, '1st color', 1)
    step2.refresh_from_db()
    step3.refresh_from_db()
    assert step1.sequence == 1
    assert step2.sequence == 2
    assert step3.sequence == 3


def test_operation__move_step(db, korse_workstation):
    def refresh_from_db(steps):
        for step in steps:
            step.refresh_from_db()
        
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')

    operation = korse_workstation.add_operation(
        name='5-Color Printing', material_type=Item.PAPER)
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


def test_operation__get_duration_and_rate(db, korse_workstation):
    spot_printing = korse_workstation.activities.get(name='Spot Color Printing')
    operation = korse_workstation.add_operation(
        name='2-Color Printing', material_type=Item.PAPER)
    operation.add_step(spot_printing, '1st Color')
    operation.add_step(spot_printing, '2nd Color')
    
    duration = operation.get_duration(Quantity(sheet=10000))
    assert duration.hr == 6

    cost = operation.get_cost(Quantity(sheet=10000))
    assert cost.amount == 1800


def test_operation__get_measurement_machine_based(db, korse_workstation, korse_machine,
        item_factory, component_factory):
    item = item_factory(name='Carbonless White', type=Item.PAPER)
    item.properties.length_value = 37
    item.properties.width_value = 25.5
    item.properties.size_uom = 'inch'
    item.properties.save()
    component = component_factory(
        name='Form', type=Item.PAPER)
    material = component.add_material(
        name='ply', quantity=100,
        width_value=8.25, length_value=5.875,
        size_uom='inch')
    
    parent_sheet = korse_machine.add_parent_sheet(12.75, 18.5, 'inch')
    child_sheet = parent_sheet.add_child_sheet(8.25, 11.75, 'inch', 0.5, 0.5, 0.5, 0.5)
    estimate = korse_machine.estimate(item, material, 100)

    assert estimate is not None
    assert estimate.item_count.sheet == 625
    assert estimate.run_count.sheet == 2500
    assert math.floor(estimate.area.sq_inch) == 589687

    operation = korse_workstation.add_operation(
        name='2-Color Printing', material_type=Item.PAPER, 
        machine=korse_machine)
    measurement = operation.get_measurement(item, material, 100)

    assert measurement.pc == 2500


def test_operation__get_costing_measure_choices(db, korse_workstation):
    def __validate(actual, expected):
        expected_choices = [measure[0] for measure in expected]
        
        if not len(actual) == len(expected_choices):
            return False

        for measure in actual:
            if not measure in expected_choices:
                return False
        return True

    operation = korse_workstation.add_operation(
        name='3-Color Printing', material_type=Item.PAPER)
    assert __validate(
        [Operation.CostingMeasure.AREA,
        Operation.CostingMeasure.PERIMETER,
        Operation.CostingMeasure.QUANTITY],
        operation.costing_measure_choices) == True

    operation.material_type = Item.PANEL
    operation.save()
    assert __validate(
        [Operation.CostingMeasure.AREA,
        Operation.CostingMeasure.PERIMETER,
        Operation.CostingMeasure.QUANTITY],
        operation.costing_measure_choices) == True

    operation.material_type = Item.TAPE
    operation.save()
    assert __validate(
        [Operation.CostingMeasure.LENGTH,
        Operation.CostingMeasure.QUANTITY],
        operation.costing_measure_choices) == True

    operation.material_type = Item.LINE
    operation.save()
    assert __validate(
        [Operation.CostingMeasure.LENGTH,
        Operation.CostingMeasure.QUANTITY],
        operation.costing_measure_choices) == True

    operation.material_type = Item.LIQUID
    operation.save()
    assert __validate(
        [Operation.CostingMeasure.VOLUME,
        Operation.CostingMeasure.QUANTITY],
        operation.costing_measure_choices) == True
    

    operation.material_type = Item.OTHER
    operation.save()
    assert __validate(
        [Operation.CostingMeasure.QUANTITY],
        operation.costing_measure_choices) == True