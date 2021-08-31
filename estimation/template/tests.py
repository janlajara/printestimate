import pytest
from core.utils.measures import CostingMeasure
from inventory.models import BaseStockUnit, AlternateStockUnit
from estimation.metaproduct.models import MetaProduct, MetaComponent, MetaMaterialOption
from estimation.template.models import ProductTemplate, ComponentTemplate, MaterialTemplate
from inventory.models import Item


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
def meta_product(db, item_factory):
    def _create_paper_item(name, length, width, uom):
        item = item_factory(name=name, type=Item.PAPER)
        item.properties.length_value = length
        item.properties.width_value = width
        item.properties.size_uom = uom
        item.properties.save()
        return item
    white_carbonless = _create_paper_item('Carbonless Blue', 22, 18, 'inch')
    blue_carbonless = _create_paper_item('Carbonless Blue', 22, 18, 'inch')
    yellow_carbonless = _create_paper_item('Carbonless Blue', 22, 18, 'inch')

    meta_product = MetaProduct.objects.create(name='Forms',
        description='8.5x11" Form')
    meta_component = meta_product.add_meta_component(name='Sheets', type=Item.PAPER)
    meta_component.allow_multiple_materials = True
    meta_component.save()

    meta_component.add_meta_material_option(white_carbonless)
    meta_component.add_meta_material_option(blue_carbonless)
    meta_component.add_meta_material_option(yellow_carbonless)

    return meta_product


def test_product_template__add_component_template(db, meta_product):
    product_template = ProductTemplate.objects.create(meta_product=meta_product,
        name=meta_product.name, description=meta_product.description)
    sheet_component = meta_product.meta_product_datas.filter(name='Sheets').first()
    sheet_template = product_template.add_component_template(sheet_component, 100)

    for meta_material_option in sheet_component.meta_material_options.all():
        sheet_template.add_material_template(meta_material_option, 
            length_value=11, width_value=8.5, size_uom='inch')
    
    assert product_template.component_templates.count() == 1
    assert sheet_template.material_templates.count() == 3
    assert sheet_template.total_material_quantity == 300

    for material_template in sheet_template.material_templates.all():
        assert material_template.quantity == 100
    
