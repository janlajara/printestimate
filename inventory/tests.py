import pytest
from measurement.measures import Distance, Volume
from .models import BaseStockUnit, AlternateStockUnit, Item, Stock, StockRequest, StockMovement
from .item.models import ItemProperties, Paper, Wire
from .exceptions import DepositTooBig, InsufficientStock, InvalidExpireQuantity


@pytest.fixture
def base_unit__sheet(db):
    return BaseStockUnit.objects.create(name='sheet', abbrev='sht')


@pytest.fixture
def alt_unit__ream(db, base_unit__sheet):
    alt_stock_unit = AlternateStockUnit.objects.create(name='ream', abbrev='rm')
    alt_stock_unit.base_stock_units.add(base_unit__sheet)
    return alt_stock_unit


@pytest.fixture
def item(db, base_unit__sheet: BaseStockUnit, alt_unit__ream: AlternateStockUnit):
    return Item.objects.create_item(name='Bond Paper',
                                   type=Item.PAPER_SHEET,
                                   base_uom=base_unit__sheet,
                                   alternate_uom=alt_unit__ream,
                                   properties=ItemProperties.objects.create())
                                   #supplying properties with a dummy value to test a branch. see code


@pytest.fixture
def item_factory(db, base_unit__sheet: BaseStockUnit, alt_unit__ream: AlternateStockUnit):
    def create_item(**data):
        item = Item.objects.create_item(base_uom=base_unit__sheet,
                                        alternate_uom=alt_unit__ream,
                                        **data)
        return item
    return create_item


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


def test_item__create(db, item: Item):
    assert item.properties is not None
    assert isinstance(item.properties, Paper)


def test_item__onhand_stocks(db, item: Item, deposited_stock: Stock):
    assert len(item.onhand_stocks) == 1


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
    stock_requests = item.request_stock(600)
    assert item.available_quantity == 400
    assert item.onhand_quantity == 1000
    assert len(stock_requests) == 2


def test_item__request_stock_lesser_quantity(db, item: Item):
    item.deposit_stock('Generic', 500, 1000, 2)
    stock_requests = item.request_stock(400)
    assert item.available_quantity == 600
    assert item.onhand_quantity == 1000
    assert len(stock_requests) == 1


def test_item__request_and_withdraw(db, item: Item):
    stock = item.deposit_stock('Generic', 500, 1000)[0]
    stock_request = item.request_stock(250)[0]
    item.withdraw_stock(stock_request.id)
    stock_request.refresh_from_db()
    assert stock_request.status == StockRequest.FULFILLED
    assert item.onhand_quantity == 250
    assert item.available_quantity == 250


def test_item_return_stock(db, item: Item):
    stock = item.deposit_stock('Generic', 500, 1000)[0]
    stock_request = item.request_stock(250)[0]
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


def test_item__tape(db, item_factory):
    item = item_factory(name='Adhesive Tape', type=Item.TAPE)
    item.properties.length = Distance(cm=50)
    assert str(item) == 'Adhesive Tape 50.0 cm'


def test_item__wire(db, item_factory):
    item = item_factory(name='Copper Wire', type=Item.WIRE)
    item.properties.length = Distance(m=1)
    assert str(item) == 'Copper Wire 1.0 m'


def test_item__paper(db, item_factory):
    item = item_factory(name='Carbonless', type=Item.PAPER_SHEET)
    item.properties.length = Distance(inch=34)
    item.properties.width = Distance(inch=22)
    assert str(item) == 'Carbonless 22.0 x 34.0 inch'


def test_item__panel(db, item_factory):
    item = item_factory(name='Sintra Board', type=Item.PANEL)
    item.properties.width = Distance(ft=4)
    item.properties.length = Distance(ft=8)
    item.properties.thickness = Distance(mm=3.0)
    assert str(item) == 'Sintra Board 4.0 x 8.0 ft 3.0 mm'


