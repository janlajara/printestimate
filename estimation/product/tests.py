import pytest
from measurement.measures import Distance
from inventory.models import BaseStockUnit, AlternateStockUnit, Item
from .models import Form, Paper, ProductProcessMapping
from ..process.models import ProcessExpense
from ..process.tests import process_factory, process_speed_factory
from ..exceptions import InvalidProductMeasure, MismatchProductMeasure, UnrecognizedProductMeasure


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
                               base_quantity=50,
                               width=Distance(inch=8.5),
                               length=Distance(inch=11))


@pytest.fixture
def form_with_ply(db, form, carbonless_white, carbonless_red, carbonless_blue):
    form.add_ply(item=carbonless_white, order=1)
    form.add_ply(item=carbonless_red, order=2)
    form.add_ply(item=carbonless_blue, order=3)
    return form


@pytest.fixture
def continuous_form(db):
    return Form.objects.create(name='Continuous Form',
                               type=Form.CONTINUOUS,
                               width=Distance(inch=8.5), length=Distance(inch=11))


@pytest.fixture
def gathering_process(db, form, process_factory, process_speed_factory):
    process = process_factory(name='Gathering', speed=process_speed_factory(20, 'set', 'min'))
    process.add_expense('Labor', ProcessExpense.HOUR_BASED, 100)
    return process


@pytest.fixture
def binding_process(db, form, process_factory, process_speed_factory):
    process = process_factory(name='Binding', speed=process_speed_factory(0.5, 'pad', 'min'))
    process.add_expense('Labor', ProcessExpense.FLAT, 100)
    return process


def test_paper__substrate_options(db, carbonless_white):
    paper = Paper.objects.create(name='Carbonless Paper',
                                 item=carbonless_white,
                                 width=Distance(inch=8.5),
                                 length=Distance(inch=11))
    assert len(paper.substrate_options) == 1


def test_form__ply_count(db, form_with_ply):
    assert form_with_ply.ply_count.sheet == 3


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


def test_form__process_options(db, form, gathering_process, binding_process):
    form.link_process(gathering_process)
    form.link_process(binding_process)
    assert len(form.process_options) == 2

    form.unlink_process(binding_process)
    assert len(form.process_options) == 1


def test_form__get_cost(db, form, gathering_process, binding_process):
    form.link_process(gathering_process)
    form.set_process_measure(gathering_process, 'base_quantity', ProductProcessMapping.DYNAMIC)
    form.link_process(binding_process)
    form.set_process_measure(binding_process, 'alternative_quantity', ProductProcessMapping.DYNAMIC)

    assert form.get_cost(100, [gathering_process, binding_process]).amount == 517


def test_product__measure_options(db, form):
    assert len(form.measure_options) == 6


def test_mapping__value_dynamic(db, form_with_ply, gathering_process):
    form_with_ply.link_process(gathering_process)
    mapping_value = form_with_ply.set_process_measure(gathering_process,
                                                      'total_ply_count',
                                                      ProductProcessMapping.DYNAMIC)
    assert mapping_value.value == 150


def test_mapping__value_alternative_quantity(db, form_with_ply, gathering_process):
    form_with_ply.link_process(gathering_process)
    mapping_value = form_with_ply.set_process_measure(gathering_process,
                                                      'alternative_quantity',
                                                      ProductProcessMapping.DYNAMIC)
    assert mapping_value.pc == 1


def test_mapping__value_static(db, form, gathering_process):
    form.link_process(gathering_process)
    mapping_value = form.set_process_measure(gathering_process, '100')
    assert mapping_value.value == 100


def test_mapping__value_static_zero_default(db, form, gathering_process):
    form.link_process(gathering_process)
    mapping_value = form.set_process_measure(gathering_process, '')
    assert mapping_value is None


def test_mapping__value_invalid_product_measure(db, form, gathering_process):
    form.link_process(gathering_process)
    with pytest.raises(InvalidProductMeasure):
        form.set_process_measure(gathering_process,
                                 'invalid_measure',
                                 ProductProcessMapping.DYNAMIC)


def test_mapping__value_mismatch_product_measure(db, form, gathering_process):
    form.link_process(gathering_process)
    with pytest.raises(MismatchProductMeasure):
        form.set_process_measure(gathering_process,
                                 'length',
                                 ProductProcessMapping.DYNAMIC)


def test_mapping__value_unrecognized_product_measure(db, form, gathering_process):
    form.link_process(gathering_process)
    with pytest.raises(UnrecognizedProductMeasure):
        form.set_process_measure(gathering_process,
                                 'flat_size', ProductProcessMapping.DYNAMIC)
