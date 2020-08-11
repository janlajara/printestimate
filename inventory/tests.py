import pytest
from django.test import TestCase
from .models import BaseStockUnit, AlternateStockUnit, Material, Stock, StockUnit, StockMovement
from .exceptions import DepositTooBig, InsufficientStock

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


def test_unit__sheet_plural_fullname(db, base_unit__sheet: BaseStockUnit):
    assert base_unit__sheet.plural_name == 'sheets'


def test_unit__sheet_plural_abbrev(db, base_unit__sheet: BaseStockUnit):
    assert base_unit__sheet.plural_abbrev == 'shts'


def test_unit__box_plural_fullname(db, alt_unit__ream: AlternateStockUnit):
    assert alt_unit__ream.plural_name == 'reams'


def test_unit__box_plural_abbrev(db, alt_unit__ream: AlternateStockUnit):
    assert alt_unit__ream.plural_abbrev == 'rms'


def test_material__available_stocks(db, material: Material, deposited_stock: Stock):
    assert len(material.available_stocks) == 1


def test_material__get_latest_price(db, material: Material, stock: Stock):
    assert material.latest_price_per_quantity.amount == 1


def test_material__deposit_stock_has_price(db, material: Material, deposited_stock: Stock):
    stock = deposited_stock
    assert stock is not None
    assert stock.price_per_quantity.amount == 2
    assert stock.in_stock_quantity == 500
    assert stock.is_in_stock_full == True
    assert material.total_in_stock == 500


def test_material__deposit_stock_has_stock_movement(db, deposited_stock: Stock):
    stock = deposited_stock
    stock_movement = StockMovement.objects.filter(stock__pk=stock.id)[0]
    assert stock_movement is not None
    assert stock_movement.action == StockMovement.DEPOSIT
    assert stock_movement.stock_unit is not None
    assert stock_movement.stock_unit.quantity == stock.base_quantity


def test_stock__price_per_quantity(db, stock: Stock):
    assert stock.price_per_quantity.amount == 1


def test_stock__deposit_too_big(db, stock: Stock):
    with pytest.raises(DepositTooBig):
        stock.deposit(501)


def test_stock__withdraw_insufficient_stock(db, deposited_stock: Stock):
    with pytest.raises(InsufficientStock):
        deposited_stock.withdraw(501)
