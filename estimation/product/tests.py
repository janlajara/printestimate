import pytest
from measurement.measures import Distance
from inventory.models import BaseStockUnit, AlternateStockUnit, Item
from .models import Form


@pytest.fixture
def base_unit__sheet(db):
    return BaseStockUnit.objects.create(name='sheet', abbrev='sht')


@pytest.fixture
def alt_unit__ream(db, base_unit__sheet):
    alt_stock_unit = AlternateStockUnit.objects.create(name='ream', abbrev='rm')
    alt_stock_unit.base_stock_units.add(base_unit__sheet)
    return alt_stock_unit


@pytest.fixture
def item_factory(db, base_unit__sheet: BaseStockUnit, alt_unit__ream: AlternateStockUnit):
    def create_item(**data):
        item = Item.objects.create_item(base_uom=base_unit__sheet,
                                        alternate_uom=alt_unit__ream,
                                        **data)
        return item
    return create_item


@pytest.fixture
def carbonless_white(db, item_factory):
    item = item_factory(name='Carbonless White', type=Item.PAPER_SHEET)
    item.properties.length = Distance(inch=34)
    item.properties.width = Distance(inch=22)
    item.properties.save()
    #item.properties.refresh_from_db()
    return item


@pytest.fixture
def carbonless_red(db, item_factory):
    item = item_factory(name='Carbonless Red', type=Item.PAPER_SHEET)
    item.properties.length = Distance(inch=34)
    item.properties.width = Distance(inch=22)
    return item


@pytest.fixture
def carbonless_blue(db, item_factory):
    item = item_factory(name='Carbonless Blue', type=Item.PAPER_SHEET)
    item.properties.length = Distance(inch=34)
    item.properties.width = Distance(inch=22)
    return item


@pytest.fixture
def form(db):
    return Form.objects.create(name='Carbonless Form',
                               type=Form.PADDED,
                               length=Distance(inch=8.5),
                               width=Distance(inch=11))


def test_form__ply_count(db, form, carbonless_white, carbonless_red, carbonless_blue):
    form.add_ply(item=carbonless_white, order=1)
    form.add_ply(item=carbonless_red, order=2)
    form.add_ply(item=carbonless_blue, order=3)

    print(carbonless_white)

    assert form.ply_count == 3
    assert len(form.substrate_options) == 3

    for item in form.substrate_options:
        assert item.properties is not None

    #for props in ItemProperties.objects.all():
    print(Item.objects.all())

    assert False