import pytest
from estimation.machine.models import Machine, ChildSheet
from estimation.product.models import Material
from core.utils.measures import Measure
from inventory.models import Item


@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch',
        min_sheet_width=10, max_sheet_width=30,
        min_sheet_length=10, max_sheet_length=30)


def test_machine__add_parent_sheet(db, gto_machine):
    parent_sheet = gto_machine.add_parent_sheet(17, 22, 'inch', 1, 1, 1, 1)
    assert parent_sheet.width.inch == 17
    assert parent_sheet.length.inch == 22
    assert parent_sheet.padding == (1, 1, 1, 1)
    assert parent_sheet.padding_x == 2
    assert parent_sheet.padding_y == 2


def test_machine_add_parent_sheet_value_error(db, gto_machine):
    with pytest.raises(ValueError):
        parent_sheet = gto_machine.add_parent_sheet(1, 1, 'm', 1, 1, 1, 1)


def test_parent_sheet__add_child_sheet(db, gto_machine):
    parent_sheet = gto_machine.add_parent_sheet(21, 26, 'inch', 1, 1, 1, 1)
    child_sheet = parent_sheet.add_child_sheet(8.5, 11, 'inch', 0.5, 0.5, 0.5, 0.5)
    assert child_sheet.width.inch == 8.5
    assert child_sheet.length.inch == 11
    assert child_sheet.margin == (0.5, 0.5, 0.5, 0.5)
    assert child_sheet.count == 4
    assert child_sheet.usage == 1
    assert child_sheet.wastage == 0


def test_parent_sheet__add_child_sheet_value_error(db, gto_machine):
    parent_sheet = gto_machine.add_parent_sheet(21, 26, 'inch', 1, 1, 1, 1)  

    with pytest.raises(ValueError):
        child_sheet = parent_sheet.add_child_sheet(1, 1, 'm', 0.5, 0.5, 0.5, 0.5)


def test_child_sheet__get_layout(db):
    args = {
        "parent_width": 36, 
        "parent_length": 28, 
        "parent_uom": 'inch', 
        "parent_padding_top": 2, 
        "parent_padding_bottom": 2,
        "parent_padding_right": 0, 
        "parent_padding_left": 0,
        "child_width": 14, 
        "child_length": 7, 
        "child_uom": 'inch', 
        "child_margin_top": 1, 
        "child_margin_bottom": 0,
        "child_margin_right": 0, 
        "child_margin_left": 0,
        "rotate": True}

    layout, count, usage, wastage, rotated = ChildSheet.get_layout(**args)

    assert count == 7
    assert usage == 90.74
    assert wastage == 9.26
    assert len(rotated) == 1
    assert rotated[0] == 2