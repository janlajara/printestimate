import pytest, math
from estimation.machine.models import Machine, ChildSheet, ParentSheet
from estimation.product.models import Material, Component, Product
from core.utils.shapes import Rectangle
from core.utils.measures import Measure
from inventory.models import Item
from inventory.tests import item_factory, base_unit__sheet, alt_unit__ream


@pytest.fixture
def create_sheetfed_machine(db):
    def create(name, min_width, max_width, min_length, max_length, uom):
        return Machine.objects.create_machine(name=name, 
            type=Machine.SHEET_FED_PRESS, uom=uom,
            min_sheet_width=min_width, max_sheet_width=max_width,
            min_sheet_length=min_length, max_sheet_length=max_length)
    return create


@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch',
        min_sheet_width=10, max_sheet_width=30,
        min_sheet_length=10, max_sheet_length=30)


@pytest.fixture
def carbonless_item(db, item_factory):
    item = item_factory(type=Item.PAPER, name='Carbonless')
    item.properties.length_value = 27
    item.properties.width_value = 32
    item.properties.size_uom = 'inch'
    return item


@pytest.fixture
def sheet_material(db, carbonless_item):
    product = Product.objects.create(name='Form', quantity=10)
    component = Component.objects.create(product=product, quantity=1)
    sheet_material = Material.objects.create_material(component=component,
        type=Item.PAPER, item=carbonless_item, name='Sheet', 
        length_value=10, width_value=8, size_uom='inch')
    return sheet_material


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


def test_parent_sheet__add_child_sheet_value_error(db, gto_machine):
    parent_sheet = gto_machine.add_parent_sheet(21, 26, 'inch', 1, 1, 1, 1)  

    with pytest.raises(ValueError):
        child_sheet = parent_sheet.add_child_sheet(1, 1, 'm', 0.5, 0.5, 0.5, 0.5)


def test_child_sheet__get_layout(db):
    parent_layout = ParentSheet.Layout(width=36, length=28, uom='inch',
        padding_top=2, padding_bottom=2, padding_right=0, padding_left=0)
    child_layout = ChildSheet.Layout(width=14, length=7, uom='inch',
        margin_top=1, margin_bottom=0, margin_right=0, margin_left=0)

    layout_meta = ChildSheet.get_layout(
        parent_layout, child_layout, True)

    assert layout_meta.count == 7
    assert layout_meta.usage == 90.74
    assert layout_meta.wastage == 9.26
    assert len(layout_meta.rotate) == 1
    assert layout_meta.rotate[0] == 2


def test_child_sheet__get_layout_test_cut(db):
    parent_layout = ParentSheet.Layout(width=32, length=27, uom='inch')
    child_layout = ChildSheet.Layout(width=27, length=16, uom='inch')

    layout_meta = ChildSheet.get_layout(
        parent_layout, child_layout, True)

    assert layout_meta.count == 2
    assert layout_meta.cut_count == 1


def test_filter_machines_by_material_type(db, gto_machine):
    machines = [x for x in Machine.objects.all() if x.material_type == Item.PAPER]

    assert len(machines) == 1
    assert machines[0] == gto_machine


def test_sheet_fed_press__get_sheet_layouts(db, create_sheetfed_machine):
    machine = create_sheetfed_machine(name='Some Machine', uom='inch',
        min_width=10, max_width=30, min_length=10, max_length=30)
    item = Rectangle.Layout(width=32, length=27, uom='inch')
    material = Rectangle.Layout(width=10, length=8, uom='inch')

    layouts = machine.get_sheet_layouts(material, item, True)

    assert layouts is not None
    assert len(layouts) == 2

    parent_runsheet = layouts[0]
    runsheet_cutsheet = layouts[1]

    assert parent_runsheet.rect.length == 27 and parent_runsheet.rect.width == 16
    assert parent_runsheet.count == 2
    assert parent_runsheet.cut_count == 1

    assert runsheet_cutsheet.count == 4
    assert runsheet_cutsheet.cut_count == 4
    

def test_sheet_fed_press__get_sheet_layouts__rotated_sheet(db, create_sheetfed_machine):
    machine = create_sheetfed_machine(name='Some Machine', uom='inch',
        min_width=2, max_width=5, min_length=2, max_length=5)
    item = Rectangle.Layout(width=4, length=6, uom='inch')
    material = Rectangle.Layout(width=2, length=2, uom='inch')

    layouts = machine.get_sheet_layouts(material, item, True)

    assert layouts is not None and len(layouts) == 2

    item_to_runsheet = layouts[0]
    runsheet_to_material = layouts[1]

    assert item_to_runsheet.rect.length == 4 and \
        item_to_runsheet.rect.width == 2 and item_to_runsheet.rect.uom == 'inch'
    assert item_to_runsheet.count == 3
    assert runsheet_to_material.count == 2


def test_sheet_fed_press__get_sheet_layouts__halved_length_less_than_machine_min(
        db, create_sheetfed_machine):
    machine = create_sheetfed_machine(name='Some Machine', uom='inch',
        min_width=4.1, max_width=4.4, min_length=4.1, max_length=4.4)
    item = Rectangle.Layout(width=9, length=9, uom='inch')
    material = Rectangle.Layout(width=2, length=2, uom='inch')

    layouts = machine.get_sheet_layouts(material, item, True)

    assert layouts is not None and len(layouts) == 2

    item_to_runsheet = layouts[0]
    runsheet_to_material = layouts[1]

    assert item_to_runsheet.rect.width == 4.1 and item_to_runsheet.rect.length == 4.1
    assert item_to_runsheet.count == 4
    assert runsheet_to_material.count == 4


def test_sheet_fed_press__get_sheet_layouts__big_layout(
        db, create_sheetfed_machine):
    machine = create_sheetfed_machine(name='Some Machine', uom='inch',
        min_width=11, max_width=25, min_length=11, max_length=25)
    item = Rectangle.Layout(width=32, length=28, uom='inch')
    material = Rectangle.Layout(width=17, length=14, uom='inch')

    layouts = machine.get_sheet_layouts(material, item, True)

    assert layouts is not None and len(layouts) == 2
    
    item_to_runsheet = layouts[0]
    runsheet_to_material = layouts[1]

    assert item_to_runsheet.count == 3
    assert runsheet_to_material.count == 1