import pytest
from estimation.machine.models import Machine
from estimation.product.models import Material
from core.utils.measures import Measure
from inventory.models import Item

@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch')

def test_machine__add_parent_sheet(db, gto_machine):
    parent_sheet = gto_machine.add_parent_sheet(17, 22, 'inch', 1, 1, 1, 1)
    assert parent_sheet.width.inch == 17
    assert parent_sheet.length.inch == 22
    assert parent_sheet.padding == (1, 1, 1, 1)
    assert parent_sheet.padding_x == 2
    assert parent_sheet.padding_y == 2

def test_parent_sheet__add_child_sheet(db, gto_machine):
    parent_sheet = gto_machine.add_parent_sheet(21, 26, 'inch', 1, 1, 1, 1)
    child_sheet = parent_sheet.add_child_sheet(8.5, 11, 'inch', 0.5, 0.5, 0.5, 0.5)
    assert child_sheet.width.inch == 8.5
    assert child_sheet.length.inch == 11
    assert child_sheet.margin == (0.5, 0.5, 0.5, 0.5)
    assert child_sheet.count == 4
    assert child_sheet.usage == 1
    assert child_sheet.wastage == 0
