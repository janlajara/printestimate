import pytest
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

def test_component__add_material(db, component_factory):
    component = component_factory(
        name='Form', type=Item.PAPER)
    ply = component.add_material(
        name='ply', quantity=400,
        width_value=8.5, length_value=11,
        size_uom='inch')

    assert ply.width.inch == 8.5 and ply.length.inch == 11    