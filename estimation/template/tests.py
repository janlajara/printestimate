import pytest
from core.utils.measures import CostingMeasure
from estimation.machine.models import Machine
from estimation.process.models import Workstation
from inventory.models import BaseStockUnit, AlternateStockUnit
from estimation.metaproduct.models import MetaProduct, MetaComponent, \
    MetaMaterialOption, MetaService, MetaEstimateVariable, MetaOperation
from estimation.template.models import ProductTemplate, ComponentTemplate, \
    MaterialTemplate, PaperComponentTemplate
from inventory.models import Item


@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch',
        min_sheet_width=10, max_sheet_width=30,
        min_sheet_length=10, max_sheet_length=30)


@pytest.fixture
def gto_workstation(db, gto_machine):
    korse_ws = Workstation.objects.create(name='GTO', 
        description='', machine=gto_machine)
    korse_ws.add_expense('Electricity', 'hour', 100)
    korse_ws.add_expense('Depreciation', 'hour', 200)
    spot_printing = korse_ws.add_activity('Spot Color Printing', 1, 1, 
        (10000, 'sheet', 'hr'), True)

    operation = korse_ws.add_operation('GTO 2-color Printing', Item.PAPER)
    operation.add_step(spot_printing, '1st color')
    operation.add_step(spot_printing, '2nd color')

    return korse_ws


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
def meta_product(db, gto_machine, gto_workstation, item_factory):
    def _create_paper_item(name, length, width, uom):
        item = item_factory(name=name, type=Item.PAPER)
        item.properties.length_value = length
        item.properties.width_value = width
        item.properties.size_uom = uom
        item.properties.save()
        return item
    white_carbonless = _create_paper_item('Carbonless White', 22, 18, 'inch')
    blue_carbonless = _create_paper_item('Carbonless Blue', 22, 18, 'inch')
    yellow_carbonless = _create_paper_item('Carbonless Yellow', 22, 18, 'inch')

    meta_product = MetaProduct.objects.create(name='Forms',
        description='8.5x11" Form')
    meta_component = meta_product.add_meta_component(name='Sheets', type=Item.PAPER)
    meta_component.allow_multiple_materials = True
    meta_component.save()

    meta_component.add_meta_machine_option(gto_machine)
    meta_component.add_meta_material_option(white_carbonless)
    meta_component.add_meta_material_option(blue_carbonless)
    meta_component.add_meta_material_option(yellow_carbonless)

    meta_service = meta_product.add_meta_service(
        name='Printing', type=Item.PAPER, 
        costing_measure=CostingMeasure.QUANTITY, 
        meta_component=meta_component,
        estimate_variable_type=MetaEstimateVariable.RAW_TO_RUNNING_CUT)
    gto_2color_printing_operation = gto_workstation.operations.filter(name='GTO 2-color Printing').first()
    front_print_operation = meta_service.add_meta_operation('Front Print', 
        MetaOperation.SINGLE_OPTION)
    meta_operation_option = front_print_operation.add_option(gto_2color_printing_operation)

    return meta_product


def test_product_template__add_component_template(db, meta_product):
    product_template = ProductTemplate.objects.create(meta_product=meta_product,
        name=meta_product.name, description=meta_product.description)
    sheet_component = meta_product.meta_product_datas.filter(name='Sheets').first()
    sheet_template = product_template.add_component_template(
        sheet_component, 100, length_value=11, width_value=8.5, size_uom='inch')

    for meta_material_option in sheet_component.meta_material_options.all():
        sheet_template.add_material_template(meta_material_option)
    
    assert product_template.component_templates.count() == 1
    assert sheet_template.material_templates.count() == 3
    assert sheet_template.total_material_quantity == 300

    for material_template in sheet_template.material_templates.all():
        assert material_template.quantity == 100


def test_product_template__add_service_template(db, meta_product):
    product_template = ProductTemplate.objects.create(meta_product=meta_product,
        name=meta_product.name, description=meta_product.description)

    sheet_component = meta_product.meta_product_datas.filter(name='Sheets').first()
    sheet_template = product_template.add_component_template(
        sheet_component, 100, length_value=11, width_value=8.5, size_uom='inch')
    for meta_material_option in sheet_component.meta_material_options.all():
        sheet_template.add_material_template(meta_material_option)

    meta_service = meta_product.meta_product_datas.filter(name='Printing').first()
    service_template = product_template.add_service_template(meta_service=meta_service)

    assert service_template is not None
    assert service_template.sequence == 1
    assert service_template.component_template == sheet_template


def test_delete_product_template(db, meta_product):
    product_template = ProductTemplate.objects.create(meta_product=meta_product,
        name=meta_product.name, description=meta_product.description)
    sheet_component = meta_product.meta_product_datas.filter(name='Sheets').first()
    sheet_template = product_template.add_component_template(
        sheet_component, 100, length_value=11, width_value=8.5, size_uom='inch')

    product_template.delete()
    assert ComponentTemplate.objects.count() == 0
    
