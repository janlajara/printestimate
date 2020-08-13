import pytest
from django.test import TestCase
from .models import BaseStockUnit, AlternateStockUnit, Material, Stock, StockRequest, StockMovement
from .exceptions import DepositTooBig, InsufficientStock, InvalidExpireQuantity


@pytest.fixture
def base_unit__sheet(db):
    return BaseStockUnit.objects.create(name='sheet', abbrev='sht')


@pytest.fixture
def alt_unit__ream(db):
    return AlternateStockUnit.objects.create(name='ream', abbrev='rm')


@pytest.fixture
def material(db, base_unit__sheet: BaseStockUnit, alt_unit__ream: AlternateStockUnit):
    return Material.objects.create(name='Bond Paper 8.5 x 11',
                                   base_uom=base_unit__sheet, alternate_uom=alt_unit__ream)


@pytest.fixture
def stock(db, material: Material):
    return Stock.objects.create(brand_name='Cactus',
                                material=material, price=500, base_quantity=500)


@pytest.fixture
def deposited_stock(db, material: Material):
    return material.deposit_stock('Generic', 500, 1000)[0]


def test_unit__sheet_plural(db, base_unit__sheet: BaseStockUnit):
    assert base_unit__sheet.plural_name == 'sheets'
    assert base_unit__sheet.plural_abbrev == 'shts'


def test_unit__box_plural(db, alt_unit__ream: AlternateStockUnit):
    assert alt_unit__ream.plural_name == 'reams'
    assert alt_unit__ream.plural_abbrev == 'rms'


def test_material__onhand_stocks(db, material: Material, deposited_stock: Stock):
    assert len(material.onhand_stocks) == 1


def test_material__get_latest_price(db, material: Material, stock: Stock):
    assert material.latest_price_per_quantity.amount == 1


def test_material__deposit_stock_has_price(db, deposited_stock: Stock):
    stock = deposited_stock
    assert stock is not None
    assert stock.price_per_quantity.amount == 2
    assert stock.onhand_quantity == 500
    assert stock.is_quantity_full is True


def test_material__deposit_multiple_stocks(db, material: Material):
    material.deposit_stock('Generic', 500, 1000, 2)
    assert material.onhand_quantity == 1000


def test_material__request_stock_greater_quantity(db, material: Material):
    material.deposit_stock('Generic', 500, 1000, 2)
    stock_requests = material.request_stock(600)
    assert material.available_quantity == 400
    assert material.onhand_quantity == 1000
    assert len(stock_requests) == 2


def test_material__request_stock_lesser_quantity(db, material: Material):
    material.deposit_stock('Generic', 500, 1000, 2)
    stock_requests = material.request_stock(400)
    assert material.available_quantity == 600
    assert material.onhand_quantity == 1000
    assert len(stock_requests) == 1


def test_material_request_and_withdraw(db, material: Material):
    stock = material.deposit_stock('Generic', 500, 1000)[0]
    stock_request = material.request_stock(250)[0]
    material.withdraw_stock(stock_request.id)
    stock_request.refresh_from_db()
    assert stock_request.status == StockRequest.FULFILLED
    assert material.onhand_quantity == 250
    assert material.available_quantity == 250


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


def test_stock__expired(db, deposited_stock: Stock):
    deposited_stock.expired(500)
    assert deposited_stock.onhand_quantity == 0
    assert deposited_stock.available_quantity == 0


def test_stock__expired_invalid_quantity(db, deposited_stock: Stock):
    with pytest.raises(InvalidExpireQuantity):
        deposited_stock.expired(501)
