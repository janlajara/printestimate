import pytest
from estimation.machine.models import Machine
from core.utils.measures import CostingMeasure
from inventory.models import Item
from inventory.tests import item_factory, base_unit__sheet, alt_unit__ream
from estimation.process.models import Workstation
from estimation.metaproduct.models import MetaProduct, MetaService, \
    MetaComponent, MetaMaterialOption, MetaOperation, MetaOperationOption


@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch',
        min_sheet_width=10, max_sheet_width=30,
        min_sheet_length=10, max_sheet_length=30)


@pytest.fixture
def meta_component_factory(db):
    def create_component(**kwargs):
        meta_product = MetaProduct.objects.create(name='product')
        return MetaComponent.objects.create(meta_product=meta_product, **kwargs)
    return create_component

@pytest.fixture
def form_meta_component(db, meta_component_factory):
    component = meta_component_factory(name='Form', type=Item.PAPER)
    return component

@pytest.fixture
def carbonless_item(db, item_factory):
    item = item_factory(type=Item.PAPER, name='Carbonless')
    item.properties.length_value = 11
    item.properties.width_value = 8.5
    item.properties.size_uom = 'inch'
    return item

@pytest.fixture
def korse_printing_operation(db):
    ws = Workstation.objects.create(name='Korse', description='')
    op = ws.add_operation('Korse Printing', Item.PAPER)
    return op

def test_meta_product__add_meta_component(db):
    meta_product = MetaProduct.objects.create(name='Form')
    meta_component = meta_product.add_meta_component(name='Sheets', type=Item.PAPER)

    assert meta_component is not None
    assert meta_component.name == 'Sheets'
    assert meta_component.type == Item.PAPER

def test_meta_product__add_meta_service(db):
    meta_product = MetaProduct.objects.create(name='Form')
    meta_service = meta_product.add_meta_service(name='Padding', 
        type=Item.PAPER, costing_measure=CostingMeasure.QUANTITY)
    
    assert meta_service is not None
    assert meta_service.name == 'Padding'
    assert meta_service.type == Item.PAPER
    assert meta_service.costing_measure == CostingMeasure.QUANTITY


def test_meta_component__add_machine_option(db, form_meta_component, gto_machine):
    meta_machine_option = form_meta_component.add_meta_machine_option(gto_machine)

    assert meta_machine_option is not None
    assert meta_machine_option.label == 'GTO Press'
    assert meta_machine_option.machine == gto_machine
    assert len(form_meta_component.meta_estimate_variables) == 3


def test_meta_component__add_meta_material_option(db, form_meta_component, carbonless_item):
    meta_material_option = form_meta_component.add_meta_material_option(carbonless_item)

    assert meta_material_option is not None
    assert meta_material_option.label == 'Carbonless 8.5x11inch'
    assert meta_material_option.meta_component == form_meta_component
    assert meta_material_option.item == carbonless_item
    assert len(form_meta_component.meta_material_options.all()) == 1
    assert form_meta_component.meta_material_options.first() == meta_material_option
    assert len(form_meta_component.meta_estimate_variables) == 9


def test_meta_component__add_meta_operation(db, form_meta_component):
    meta_operation = form_meta_component.add_meta_operation('Padding', 
        MetaOperation.MULTIPLE_OPTIONS)

    assert meta_operation is not None
    assert meta_operation.name == 'Padding'
    assert meta_operation.options_type == MetaOperation.MULTIPLE_OPTIONS
    assert meta_operation.costing_measure == 'quantity'


def test_meta_operation__add_clear_option(db, form_meta_component, korse_printing_operation):
    meta_operation = form_meta_component.add_meta_operation('Padding', 
        MetaOperation.MULTIPLE_OPTIONS)
    
    option = meta_operation.add_option(korse_printing_operation)

    assert option is not None
    assert len(meta_operation.options) == 1
    assert meta_operation.meta_operation_options.first() == option

    meta_operation.clear_options()
    assert len(meta_operation.options) == 0


def test_meta_operation__add_option_exception(db, form_meta_component, korse_printing_operation):
    meta_operation = form_meta_component.add_meta_operation('Padding', 
        MetaOperation.BOOLEAN_OPTION)

    option = meta_operation.add_option(korse_printing_operation)

    assert option is not None
    assert meta_operation.options is not None
    assert meta_operation.options[0] == option

    with pytest.raises(Exception):
        meta_operation.add_option(korse_printing_operation)