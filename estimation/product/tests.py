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
    item.properties.size_uom = 'inch'
    item.properties.save()
    return item


@pytest.fixture
def carbonless_red(db, item_factory):
    item = item_factory(name='Carbonless Red', type=Item.PAPER_SHEET)
    item.properties.length = Distance(inch=34)
    item.properties.width = Distance(inch=22)
    item.properties.size_uom = 'inch'
    item.properties.save()
    return item


@pytest.fixture
def carbonless_blue(db, item_factory):
    item = item_factory(name='Carbonless Blue', type=Item.PAPER_SHEET)
    item.properties.length = Distance(inch=34)
    item.properties.width = Distance(inch=22)
    item.properties.size_uom = 'inch'
    item.properties.save()
    return item


@pytest.fixture
def carbonless_roll(db, item_factory):
    item = item_factory(name='Carbonless Roll', type=Item.PAPER_ROLL)
    item.properties.length = Distance(meter=50)
    item.properties.width = Distance(ft=4)
    item.properties.size_uom = 'meter'
    item.properties.save()


@pytest.fixture
def form(db):
    return Form.objects.create(name='Carbonless Form',
                               type=Form.PADDED,
                               width=Distance(inch=8.5),
                               length=Distance(inch=11))


@pytest.fixture
def continuous_form(db):
    return Form.objects.create(name='Continuous Form',
                               type=Form.CONTINUOUS,
                               width=Distance(inch=8.5), length=Distance(inch=11))


def test_form__ply_count(db, form, carbonless_white, carbonless_red, carbonless_blue):
    form.add_ply(item=carbonless_white, order=1)
    form.add_ply(item=carbonless_red, order=2)
    form.add_ply(item=carbonless_blue, order=3)
    assert form.ply_count == 3


def test_form__get_substrate_options_sheet(db, form, carbonless_white, carbonless_red):
    assert len(form.substrate_options) == 2


def test_form__get_substrate_options_roll(db, continuous_form, carbonless_roll):
    assert len(continuous_form.substrate_options) == 1


def test_form__finished_size(db, form):
    assert form.finished_size['width'].value == 8.5
    assert form.finished_size['length'].value == 11


def test_form__flat_size(db, form):
    assert form.flat_size['width'].value == 8.5
    assert form.flat_size['length'].value == 11
