import pytest
from measurement.measures import Distance, Volume
from .models import BaseStockUnit, AlternateStockUnit, Item, \
    Stock, StockRequest, StockRequestGroup, StockMovement
from .properties.models import ItemProperties, Paper
from .exceptions import DepositTooBig, InsufficientStock, InvalidExpireQuantity, \
    IllegalUnboundedDeposit, IllegalWithdrawal, IllegalStockRequestOperation, \
    IllegalStockRequestGroupOperation


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
        item = Item.objects.create(base_uom=base_unit__sheet,
                                        alternate_uom=alt_unit__ream,
                                        **data)
        type = data.get('type')
        clazz = ItemProperties.get_class(data.get('type'))
        args = {}
        if (type == Item.PAPER or type == Item.PANEL):
            args = {'length_value': 0, 'width_value': 0}
        props = clazz.objects.create(**args)
        item.properties = props
        return item
    return create_item


@pytest.fixture
def item(db, item_factory):
    item = item_factory(type=Item.PAPER, name='Carbonless')
    item.properties.length_value = 11
    item.properties.width_value = 8.5
    return item


@pytest.fixture
def stock(db, item: Item):
    return Stock.objects.create(brand_name='Cactus',
                                item=item, price=500, base_quantity=500)


@pytest.fixture
def deposited_stock(db, item: Item):
    return item.deposit_stock('Generic', 500, 1000)[0]


def test_unit__sheet_plural(db, base_unit__sheet: BaseStockUnit):
    assert base_unit__sheet.plural_name == 'sheets'
    assert base_unit__sheet.plural_abbrev == 'shts'


def test_unit__box_plural(db, alt_unit__ream: AlternateStockUnit):
    assert alt_unit__ream.plural_name == 'reams'
    assert alt_unit__ream.plural_abbrev == 'rms'


def test_base_unit__add_unit(db, base_unit__sheet:BaseStockUnit):
    alt_stock_unit = AlternateStockUnit.objects.create(name='box', abbrev='bx')
    obj = base_unit__sheet.add_alt_stock_unit(alt_stock_unit.pk)
    assert alt_stock_unit.pk == obj.pk
    assert alt_stock_unit.name == obj.name


def test_alt_unit__add_unit(db, alt_unit__ream:AlternateStockUnit):
    base_stock_unit = BaseStockUnit.objects.create(name='Leaf', abbrev='lf')
    obj = alt_unit__ream.add_base_stock_unit(base_stock_unit.pk)
    assert base_stock_unit.pk == obj.pk
    assert base_stock_unit.name == obj.name


def test_base_unit__remove(db, base_unit__sheet:BaseStockUnit, alt_unit__ream:AlternateStockUnit):
    base_unit__sheet.remove_alt_stock_unit(alt_unit__ream.pk)
    assert len(base_unit__sheet.alternate_stock_units.all()) == 0


def test_alt_unit__remove(db, base_unit__sheet:BaseStockUnit, alt_unit__ream:AlternateStockUnit):
    alt_unit__ream.remove_base_stock_unit(base_unit__sheet.pk)
    assert len(alt_unit__ream.base_stock_units.all()) == 0


def test_base_unit__update(db):
    base_stock_unit = BaseStockUnit.objects.create(name='Piece', abbrev='pc')
    box_stock_unit = AlternateStockUnit.objects.create(name='Box', abbrev='bx')
    pack_stock_unit = AlternateStockUnit.objects.create(name='Pack', abbrev='pk')
    base_stock_unit.add_alt_stock_unit(box_stock_unit.pk)
    base_stock_unit.add_alt_stock_unit(pack_stock_unit.pk)

    base_stock_unit.update_alt_stock_units([box_stock_unit])
    assert len(base_stock_unit.alternate_stock_units.all()) == 1
    assert base_stock_unit.alternate_stock_units.first().pk == box_stock_unit.pk


def test_alt_unit__update(db):
    piece_stock_unit = BaseStockUnit.objects.create(name='Piece', abbrev='pc')
    pack_stock_unit = BaseStockUnit.objects.create(name='Pack', abbrev='pk')
    box_stock_unit = AlternateStockUnit.objects.create(name='Box', abbrev='bx')
    box_stock_unit.add_base_stock_unit(piece_stock_unit.pk)
    box_stock_unit.add_base_stock_unit(pack_stock_unit.pk)

    box_stock_unit.update_base_stock_units([piece_stock_unit])
    assert len(box_stock_unit.base_stock_units.all()) == 1
    assert box_stock_unit.base_stock_units.first().pk == piece_stock_unit.pk


def test_base_unit__clear(db):
    base_stock_unit = BaseStockUnit.objects.create(name='Piece', abbrev='pc')
    box_stock_unit = AlternateStockUnit.objects.create(name='Box', abbrev='bx')
    pack_stock_unit = AlternateStockUnit.objects.create(name='Pack', abbrev='pk')
    base_stock_unit.add_alt_stock_unit(box_stock_unit.pk)
    base_stock_unit.add_alt_stock_unit(pack_stock_unit.pk)
    assert len(base_stock_unit.alternate_stock_units.all()) == 2

    base_stock_unit.clear_alt_stock_units()
    assert len(base_stock_unit.alternate_stock_units.all()) == 0


def test_alt_unit__clear(db):
    pc_stock_unit = BaseStockUnit.objects.create(name='Piece', abbrev='pc')
    pack_stock_unit = BaseStockUnit.objects.create(name='Pack', abbrev='pk')
    box_stock_unit = AlternateStockUnit.objects.create(name='Box', abbrev='bx')

    box_stock_unit.add_base_stock_unit(pc_stock_unit.pk)
    box_stock_unit.add_base_stock_unit(pack_stock_unit.pk)
    assert len(box_stock_unit.base_stock_units.all()) == 2

    box_stock_unit.clear_base_stock_units()
    assert len(box_stock_unit.base_stock_units.all()) == 0


def test_item__onhand_stocks(db, item: Item, deposited_stock: Stock):
    assert len(item.onhand_stocks) == 1


def test_item__get_override_price(db, item: Item):
    item.override_price = 10
    item.deposit_stock('Generic', 500, 500)
    assert item.price.amount == 1

    item.is_override_price = True
    assert item.price.amount == 10


def test_item__get_latest_price(db, item: Item):
    item.deposit_stock('Generic', 500, 500)
    assert item.latest_price_per_quantity.amount == 1


def test_item__get_average_price(db, item: Item):
    item.deposit_stock('Generic', 500, 1000)
    item.deposit_stock('Generic', 500, 1500)
    assert item.average_price_per_quantity.amount == 2.5


def test_item__deposit_stock_has_price(db, deposited_stock: Stock):
    stock = deposited_stock
    assert stock is not None
    assert stock.price_per_quantity.amount == 2
    assert stock.onhand_quantity == 500
    assert stock.is_quantity_full is True


def test_item__deposit_multiple_stocks(db, item: Item):
    item.deposit_stock('Generic', 500, 1000, 2)
    assert item.onhand_quantity == 1000


def test_item__request_stock_greater_quantity(db, item: Item):
    item.deposit_stock('Generic', 500, 1000, 2)
    stock_requests = item.request_stock(600).stock_requests.all()
    assert item.available_quantity == 400
    assert item.onhand_quantity == 1000
    assert len(stock_requests) == 2


def test_item__request_stock_lesser_quantity(db, item: Item):
    item.deposit_stock('Generic', 500, 1000, 2)
    stock_requests = item.request_stock(400).stock_requests.all()
    assert item.available_quantity == 600
    assert item.onhand_quantity == 1000
    assert len(stock_requests) == 1


def test_item__request_and_withdraw(db, item: Item):
    stock = item.deposit_stock('Generic', 500, 1000)[0]
    stock_request_group = item.request_stock(250)
    stock_request = stock_request_group.stock_requests.first()
    stock_request.for_approval()
    stock_request.approve()

    item.withdraw_stock(stock_request.id)
    stock_request.refresh_from_db()
    assert stock_request_group.status == StockRequestGroup.CLOSED
    assert stock_request.status == StockRequest.FULFILLED
    assert item.onhand_quantity == 250
    assert item.available_quantity == 250


def test_item__request_approve_disapprove(db, item: Item):
    def assert_status_choices(actual_choices, expected_choices):
        for choice in actual_choices:
            assert choice[0] in expected_choices

    stock = item.deposit_stock('Generic', 500, 1000)[0]
    stock_request_group = item.request_stock(250)
    stock_request = stock_request_group.stock_requests.first()
    assert stock_request.stock_request_logs.first().status == StockRequest.DRAFT
    
    stock_request.for_approval()
    assert stock_request.status == StockRequest.FOR_APPROVAL
    assert_status_choices(
        stock_request.status_choices,
        [StockRequest.APPROVED, StockRequest.DISAPPROVED, 
            StockRequest.CANCELLED])

    stock_request.disapprove()
    assert stock_request.status == StockRequest.DISAPPROVED
    assert_status_choices(
        stock_request.status_choices,
        [StockRequest.CANCELLED])

    stock_request.cancel()
    assert stock_request.status == StockRequest.CANCELLED
    assert_status_choices(
        stock_request.status_choices,
        [StockRequest.DRAFT])

    stock_request.draft()
    assert stock_request.status == StockRequest.DRAFT
    assert_status_choices(
        stock_request.status_choices,
        [StockRequest.FOR_APPROVAL, StockRequest.CANCELLED])

    stock_request.for_approval()
    stock_request.approve()
    assert stock_request.status == StockRequest.APPROVED
    assert_status_choices(
        stock_request.status_choices,
        [StockRequest.FULFILLED, StockRequest.CANCELLED])

    stock_request.fulfill()
    assert stock_request.status == StockRequest.FULFILLED
    assert len(stock_request.status_choices) == 0

    assert len(stock_request.stock_request_logs.all()) == 8
    

def test_item__request_illegal(db, item: Item):
    stock = item.deposit_stock('Generic', 500, 1000)[0]
    
    stock_request_group = item.request_stock(250)
    with pytest.raises(IllegalStockRequestGroupOperation):
        stock_request_group.finish()
    with pytest.raises(IllegalStockRequestGroupOperation):
        stock_request_group.unfinish()

    stock_request = stock_request_group.stock_requests.first()
    assert stock_request.status == StockRequest.DRAFT

    with pytest.raises(IllegalStockRequestOperation):
        stock_request.approve()
    with pytest.raises(IllegalStockRequestOperation):
        stock_request.fulfill()
    with pytest.raises(IllegalStockRequestOperation):
        stock_request.disapprove()

    stock_request.for_approval()
    stock_request.approve()
    stock_request.fulfill()

    with pytest.raises(IllegalStockRequestOperation):
        stock_request.draft()
    with pytest.raises(IllegalStockRequestOperation):
        stock_request.for_approval()
    with pytest.raises(IllegalStockRequestOperation):
        stock_request.cancel()

    stock_request_group.finish()
    assert stock_request_group.finished == True


def test_item_return_stock(db, item: Item):
    stock = item.deposit_stock('Generic', 500, 1000)[0]
    stock_request = item.request_stock(250).stock_requests.first()
    stock_request.for_approval()
    stock_request.approve()

    item.withdraw_stock(stock_request.id)
    item.return_stock(stock.id, 125)
    assert item.available_quantity == 375
    assert item.onhand_quantity == 375


def test_item_expire_stock(db, item: Item):
    stock = item.deposit_stock('Generic', 500, 1000)[0]
    item.expire_stock(stock.id, 250)
    assert item.available_quantity == 250
    assert item.onhand_quantity == 250


def test_stock__has_stock_movement(db, deposited_stock: Stock):
    stock = deposited_stock
    stock_movement = StockMovement.objects.filter(stock__pk=stock.id)[0]
    assert stock_movement is not None
    assert stock_movement.action == StockMovement.DEPOSIT
    assert stock_movement.stock_unit is not None
    assert stock_movement.stock_unit.quantity == stock.base_quantity


def test_stock__price_per_quantity(db, stock: Stock):
    assert stock.price_per_quantity.amount == 1


def test_stock__available_quantity(db, deposited_stock: Stock):
    deposited_stock.request(100)
    assert deposited_stock.available_quantity == 400


def test_stock__deposit_too_big(db, stock: Stock):
    with pytest.raises(DepositTooBig):
        stock.deposit(501)


def test_stock__withdraw(db, deposited_stock: Stock):
    deposited_stock.withdraw(499)
    assert deposited_stock.onhand_quantity == 1
    assert deposited_stock.available_quantity == 1


def test_stock__withdraw_insufficient_stock(db, deposited_stock: Stock):
    with pytest.raises(InsufficientStock):
        deposited_stock.withdraw(501)


def test_stock__request(db, deposited_stock: Stock):
    deposited_stock.request(100)
    assert deposited_stock.available_quantity == 400
    assert deposited_stock.onhand_quantity == 500


def test_stock__request_insufficient_stock(db, deposited_stock: Stock):
    deposited_stock.request(100)
    with pytest.raises(InsufficientStock):
        deposited_stock.request(500)


def test_stock__return_too_big(db, deposited_stock: Stock):
    deposited_stock.withdraw(100)
    with pytest.raises(DepositTooBig):
        deposited_stock.returned(101)


def test_stock__expired(db, deposited_stock: Stock):
    deposited_stock.expired(500)
    assert deposited_stock.onhand_quantity == 0
    assert deposited_stock.available_quantity == 0


def test_stock__expired_invalid_quantity(db, deposited_stock: Stock):
    with pytest.raises(InvalidExpireQuantity):
        deposited_stock.expired(501)


def test_item__stock_unbounded(db, item: Item):
    deposited = item.deposit_stock('Generic', 500, 1, 1, True)
    stock = deposited[0]
    assert stock.price_per_quantity.amount == 1

    stock.deposit(500)
    assert item.onhand_quantity == 1000

    stock.withdraw(600)
    assert item.onhand_quantity == 400

    stock.returned(600)
    assert item.onhand_quantity == 1000


def test_item_stock_unbounded__illegal_deposit(db, item: Item):
    with pytest.raises(IllegalUnboundedDeposit):
        deposited = item.deposit_stock('Generic', 500, 1, 5, True)


def test_item_stock__illegal_withdraw(db, item: Item):
    with pytest.raises(IllegalWithdrawal):
        item.deposit_stock('Generic', 500, 1, 1, True)
        stock_request = item.request_stock(10).stock_requests.first()
        stock_request.cancel()
        item.withdraw_stock(stock_request.id)


def test_item__tape(db, item_factory):
    item = item_factory(name='Adhesive Tape', type=Item.TAPE)
    item.properties.length_value = 50
    item.properties.length_uom = 'cm'
    item.properties.width_value = 3
    item.properties.width_uom = 'cm'
    assert str(item) == 'Adhesive Tape 50cm 3cm'


def test_item__wire(db, item_factory):
    item = item_factory(name='Copper Wire', type=Item.LINE)
    item.properties.length_value = 1
    item.properties.length_uom = 'm'
    assert str(item) == 'Copper Wire 1m'


def test_item__paper(db, item_factory):
    item = item_factory(name='Carbonless', type=Item.PAPER)
    item.properties.size_uom = 'inch'
    item.properties.length_value = 34
    item.properties.width_value = 22
    item.properties.gsm = 120
    item.properties.finish = Paper.Finish.MATTE

    assert str(item) == 'Carbonless 22x34inch matte 120gsm'
    assert round(item.properties.area.value) == 748
    assert round(item.properties.perimeter.value) == 112


def test_item__panel(db, item_factory):
    item = item_factory(name='Sintra Board', type=Item.PANEL)
    item.properties.size_uom = 'ft'
    item.properties.width_value = 4
    item.properties.length_value = 8
    item.properties.thickness_value = 3
    item.properties.thickness_uom = 'mm'
    assert str(item) == 'Sintra Board 4x8ft 3mm'


def test_item__liquid(db, item_factory):
    item = item_factory(name='Red Padding Cement', type=Item.LIQUID)
    item.properties.volume_value = 1
    item.properties.volume_uom = 'l'
    assert str(item) == 'Red Padding Cement 1l'
