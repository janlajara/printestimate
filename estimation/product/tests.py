import pytest, math
from core.utils.measures import CostingMeasure
from inventory.models import Item
from inventory.tests import item_factory, base_unit__sheet, alt_unit__ream
from estimation.template.tests import meta_product
from estimation.template.models import ProductTemplate
from estimation.product.models import ProductEstimate, Product, Component, Material
from estimation.machine.models import Machine


@pytest.fixture
def carbonless_item(db, item_factory):
    item = item_factory(type=Item.PAPER, name='Carbonless')
    item.properties.length_value = 28
    item.properties.width_value = 34
    item.properties.size_uom = 'inch'
    return item


@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch',
        min_sheet_width=11, max_sheet_width=25,
        min_sheet_length=11, max_sheet_length=25)


@pytest.fixture
def product_template(db, item_factory, meta_product):
    product_template = ProductTemplate.objects.create(meta_product=meta_product,
        name=meta_product.name, description=meta_product.description)
    meta_component = meta_product.meta_product_datas.filter(name='Sheets').first()
    gto_machine_option = meta_component.meta_machine_options.filter(machine__name='GTO Press').first()
    component_template = product_template.add_component_template(
        meta_component, 100, machine_option=gto_machine_option, 
        length_value=11, width_value=8.5, size_uom='inch')

    for meta_material_option in meta_component.meta_material_options.all():
        component_template.add_material_template(meta_material_option)

    meta_service = meta_product.meta_product_datas.filter(name='Printing').first()
    service_template = product_template.add_service_template(meta_service=meta_service)

    return product_template


def test_product_estimate__create_product_by_template(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100, 200, 300])
    product = product_estimate.product

    assert product is not None
    product_components = product.components.all()
    assert product_components is not None and \
        len(product_components) == 1
    
    sheet_component = product_components.first()
    assert sheet_component.name == 'Sheets'
    assert sheet_component.machine is not None and sheet_component.machine.name == 'GTO Press'
    assert sheet_component.materials is not None and \
        len(sheet_component.materials.all()) == 3
    
    for material in sheet_component.materials.all():
        assert material.label in ['Carbonless White 8.5x11inch', 
            'Carbonless Blue 8.5x11inch', 'Carbonless Yellow 8.5x11inch']
        assert material.quantity == 100

    product_services = product.services.all()
    assert product_services is not None and \
        len(product_services) == 1


def test_material_estimate__with_machine(db, carbonless_item, gto_machine):
    product = Product.objects.create(name='Carbonless Form')
    component = Component.objects.create(name='Sheets', 
        product=product, machine=gto_machine, quantity=100)
    sheet_material = Material.objects.create_material(
        component=component, type=Item.PAPER, item=carbonless_item,
        width_value=4, length_value=5, size_uom='inch')

    estimate = sheet_material.estimate(75, 30, True)

    assert estimate is not None
    assert estimate.total_material_measures is not None

    assert estimate.output_per_item == 44
    assert estimate.estimated_stock_quantity == 171
    assert estimate.estimated_spoilage_quantity == 52
    assert estimate.estimated_total_quantity == 223

    raw_material_quantity = estimate.raw_material_measures.get(CostingMeasure.QUANTITY)
    raw_material_area = estimate.raw_material_measures.get(CostingMeasure.AREA)
    raw_material_perimeter = estimate.raw_material_measures.get(CostingMeasure.PERIMETER)
    assert raw_material_quantity is not None and \
        raw_material_area is not None and \
        raw_material_perimeter is not None
    assert raw_material_quantity.pc == 223
    assert math.isclose(raw_material_area.sq_inch, 212296)
    assert raw_material_perimeter.inch == 13826

    total_material_quantity = estimate.total_material_measures.get(CostingMeasure.QUANTITY)
    total_material_area = estimate.total_material_measures.get(CostingMeasure.AREA)
    total_material_perimeter = estimate.total_material_measures.get(CostingMeasure.PERIMETER)
    assert total_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert total_material_quantity.pc == 7500
    assert math.isclose(total_material_area.sq_inch, 150000)
    assert total_material_perimeter.inch == 67500

    set_material_quantity = estimate.set_material_measures.get(CostingMeasure.QUANTITY)
    set_material_area = estimate.set_material_measures.get(CostingMeasure.AREA)
    set_material_perimeter = estimate.set_material_measures.get(CostingMeasure.PERIMETER)
    assert set_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert set_material_quantity.pc == 100
    assert math.isclose(set_material_area.sq_inch, 2000)
    assert set_material_perimeter.inch == 900

    machine_run_quantity = estimate.machine_run_measures.get(CostingMeasure.QUANTITY)
    machine_run_area = estimate.machine_run_measures.get(CostingMeasure.AREA)
    machine_run_perimeter = estimate.machine_run_measures.get(CostingMeasure.PERIMETER)
    assert machine_run_quantity is not None and \
        machine_run_area is not None and \
        machine_run_perimeter is not None
    assert machine_run_quantity.pc == 892
    assert math.isclose(machine_run_area.sq_inch, 212296)
    assert machine_run_perimeter.inch == 27652

    assert estimate.raw_to_running_cut == 2
    assert estimate.running_to_final_cut == 9


def test_material_estimate__without_machine(db, carbonless_item):
    product = Product.objects.create(name='Carbonless Form')
    component = Component.objects.create(name='Sheets', 
        product=product, quantity=100)
    sheet_material = Material.objects.create_material(
        component=component, type=Item.PAPER, item=carbonless_item,
        width_value=4, length_value=5, size_uom='inch')
    estimate = sheet_material.estimate(75, 30, True)

    assert estimate is not None

    raw_material_quantity = estimate.raw_material_measures.get(CostingMeasure.QUANTITY)
    raw_material_area = estimate.raw_material_measures.get(CostingMeasure.AREA)
    raw_material_perimeter = estimate.raw_material_measures.get(CostingMeasure.PERIMETER)
    assert raw_material_quantity is not None and \
        raw_material_area is not None and \
        raw_material_perimeter is not None
    assert raw_material_quantity.pc == 208
    assert math.isclose(raw_material_area.sq_inch, 198016)
    assert math.isclose(raw_material_perimeter.inch, 12896)

    total_material_quantity = estimate.total_material_measures.get(CostingMeasure.QUANTITY)
    total_material_area = estimate.total_material_measures.get(CostingMeasure.AREA)
    total_material_perimeter = estimate.total_material_measures.get(CostingMeasure.PERIMETER)
    assert total_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert total_material_quantity.pc == 7500
    assert math.isclose(total_material_area.sq_inch, 150000)
    assert total_material_perimeter.inch == 67500

    set_material_quantity = estimate.set_material_measures.get(CostingMeasure.QUANTITY)
    set_material_area = estimate.set_material_measures.get(CostingMeasure.AREA)
    set_material_perimeter = estimate.set_material_measures.get(CostingMeasure.PERIMETER)
    assert set_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert set_material_quantity.pc == 100
    assert math.isclose(set_material_area.sq_inch, 2000)
    assert set_material_perimeter.inch == 900

    machine_run_quantity = estimate.machine_run_measures.get(CostingMeasure.QUANTITY)
    machine_run_area = estimate.machine_run_measures.get(CostingMeasure.AREA)
    machine_run_perimeter = estimate.machine_run_measures.get(CostingMeasure.PERIMETER)
    assert machine_run_quantity is not None and \
        machine_run_area is not None and \
        machine_run_perimeter is not None
    assert machine_run_quantity.pc == 9776
    assert math.isclose(machine_run_area.sq_inch, 195520)
    assert machine_run_perimeter.inch == 87984

    assert estimate.output_per_item == 47
    assert estimate.estimated_stock_quantity == 160
    assert estimate.estimated_spoilage_quantity == 48
    assert estimate.estimated_total_quantity == 208

    assert estimate.raw_to_running_cut == 0
    assert estimate.running_to_final_cut == 0
    assert estimate.raw_to_final_cut == 15

