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
def hplatex_machine(db):
    return Machine.objects.create_machine(name='HP Latex',
        type=Machine.ROLL_FED_PRESS, uom='inch',
        min_sheet_width=25, max_sheet_width=48,
        min_sheet_breakpoint_length=48,
        max_sheet_breakpoint_length=150)


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

    layouts = machine.get_sheet_layouts(item, material, True)

    assert layouts is not None
    assert len(layouts) == 2

    parent_runsheet = layouts[0]
    runsheet_cutsheet = layouts[1]

    assert parent_runsheet.rect.length == 27 and parent_runsheet.rect.width == 30
    assert parent_runsheet.count == 1
    assert parent_runsheet.cut_count == 1

    assert runsheet_cutsheet.count == 9
    assert runsheet_cutsheet.cut_count == 5
    

def test_sheet_fed_press__get_sheet_layouts__rotated_sheet(db, create_sheetfed_machine):
    machine = create_sheetfed_machine(name='Some Machine', uom='inch',
        min_width=2, max_width=5, min_length=2, max_length=5)
    item = Rectangle.Layout(width=4, length=6, uom='inch')
    material = Rectangle.Layout(width=2, length=2, uom='inch')

    layouts = machine.get_sheet_layouts(item, material, True)

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

    layouts = machine.get_sheet_layouts(item, material, True)

    assert layouts is not None and len(layouts) == 2

    item_to_runsheet = layouts[0]
    runsheet_to_material = layouts[1]

    assert item_to_runsheet.rect.width == 4.4 and item_to_runsheet.rect.length == 4.4
    assert item_to_runsheet.count == 4
    assert runsheet_to_material.count == 4


def test_sheet_fed_press__get_sheet_layouts__big_layout(
        db, create_sheetfed_machine):
    machine = create_sheetfed_machine(name='Some Machine', uom='inch',
        min_width=11, max_width=25, min_length=11, max_length=25)
    item = Rectangle.Layout(width=32, length=28, uom='inch')
    material = Rectangle.Layout(width=17, length=14, uom='inch')

    layouts = machine.get_sheet_layouts(item, material, True)

    assert layouts is not None and len(layouts) == 2
    
    item_to_runsheet = layouts[0]
    runsheet_to_material = layouts[1]

    assert item_to_runsheet.count == 3
    assert runsheet_to_material.count == 1


def test_roll_fed_press__get_sheet_layouts(db, hplatex_machine):
    item = Rectangle.Layout(width=48, length=2000, uom='inch')
    material = ChildSheet.Layout(width=3, length=3, uom='inch', 
        margin_top=1, margin_right=1, margin_bottom=1, margin_left=1)
    layouts = hplatex_machine.get_sheet_layouts(item, material, rotate=True, 
        order_quantity=5000, apply_breakpoint=True)
    assert layouts is not None and len(layouts) == 2

    layout1 = layouts[0]
    assert layout1.bin.width == 45 and layout1.bin.length == 150
    assert layout1.count == 270

    layout2 = layouts[1]
    assert layout2.bin.width == 45 and round(layout2.bin.length) == 100
    assert layout2.count == 180


def test_roll_fed_press__get_sheet_layouts__totallength_is_less_than_minbreakpoint(
        db, hplatex_machine):
    item = Rectangle.Layout(width=48, length=2000, uom='inch')
    material = ChildSheet.Layout(width=3, length=3, uom='inch', 
        margin_top=1, margin_right=1, margin_bottom=1, margin_left=1)
    layouts = hplatex_machine.get_sheet_layouts(item, material, rotate=True, 
        order_quantity=40, apply_breakpoint=True)
    assert layouts is not None and len(layouts) == 1

    layout1 = layouts[0]
    assert layout1.bin.width == 45 and layout1.bin.length == 48
    assert layout1.count == 81


def test_roll_fed_press__get_sheet_layouts__remainder_is_less_than_minbreakpoint(
        db, hplatex_machine):
    item = Rectangle.Layout(width=48, length=2000, uom='inch')
    material = ChildSheet.Layout(width=3, length=3, uom='inch', 
        margin_top=1, margin_right=1, margin_bottom=1, margin_left=1)
    layouts = hplatex_machine.get_sheet_layouts(item, material, rotate=True, 
        order_quantity=900.00, apply_breakpoint=True)
    assert layouts is not None and len(layouts) == 2

    layout1 = layouts[0]
    assert layout1.bin.width == 45 and layout1.bin.length == 150
    assert layout1.count == 270

    layout2 = layouts[1]
    assert layout2.bin.width == 45 and layout2.bin.length == 48
    assert layout2.count == 81


def test_roll_fed_press__get_sheet_layouts__machine_has_vertical_margin(
        db, hplatex_machine):
    hplatex_machine.horizontal_margin = 1.5
    hplatex_machine.save()

    assert hplatex_machine.horizontal_margin == 1.5
    assert hplatex_machine.max_printable_width == 45

    item = Rectangle.Layout(width=45, length=2000, uom='inch')
    material = ChildSheet.Layout(width=3, length=3, uom='inch')
    layouts = hplatex_machine.get_sheet_layouts(item, material, rotate=True, 
        order_quantity=100.00, apply_breakpoint=True)

    layout1 = layouts[0]
    assert len(layouts) == 1
    assert layout1.bin.width == 42 and layout1.bin.length == 48
    assert layout1.count == 224