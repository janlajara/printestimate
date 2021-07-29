import pytest
from core.utils.measures import CostingMeasure
from inventory.models import Item
from inventory.tests import item_factory, base_unit__sheet, alt_unit__ream
from estimation.process.models import Workstation
from estimation.metaproduct.models import MetaProduct, MetaService, \
    MetaComponent, MetaMaterialOption, MetaProperty, MetaPropertyOption

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


def test_meta_component__add_meta_material_option(db, form_meta_component, carbonless_item):
    meta_material_option = form_meta_component.add_meta_material_option(
        'Carbonless Paper', carbonless_item)
    
    assert meta_material_option is not None
    assert meta_material_option.label == 'Carbonless Paper'
    assert meta_material_option.meta_component == form_meta_component
    assert len(form_meta_component.meta_material_options.all()) == 1
    assert form_meta_component.meta_material_options.first() == meta_material_option


def test_meta_component__add_meta_property(db, form_meta_component):
    meta_property = form_meta_component.add_meta_property('Padding', 
        MetaProperty.MULTIPLE_OPTIONS)

    assert meta_property is not None
    assert meta_property.name == 'Padding'
    assert meta_property.options_type == MetaProperty.MULTIPLE_OPTIONS


def test_meta_property__add_clear_option(db, form_meta_component, korse_printing_operation):
    meta_property = form_meta_component.add_meta_property('Padding', 
        MetaProperty.MULTIPLE_OPTIONS)
    
    option = meta_property.add_option('Color Print', korse_printing_operation)

    assert option is not None
    assert option.label == 'Color Print'
    assert len(meta_property.options) == 1
    assert meta_property.meta_property_options.first() == option

    meta_property.clear_options()
    assert len(meta_property.options) == 0


def test_meta_property__add_option_exception(db, form_meta_component, korse_printing_operation):
    meta_property = form_meta_component.add_meta_property('Padding', 
        MetaProperty.BOOLEAN_OPTION)

    option = meta_property.add_option('Color Print', korse_printing_operation)

    assert option is not None
    assert meta_property.options is not None
    assert meta_property.options[0] == option

    with pytest.raises(Exception):
        meta_property.add_option('Another operation', korse_printing_operation)