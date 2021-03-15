from django.db import models
from django.db.models import Q, Sum, Avg
from djmoney.models.fields import MoneyField
from .exceptions import DepositTooBig, InsufficientStock, InvalidExpireQuantity
import inflect

_inflect = inflect.engine()


# Create your models here.
class StokUnit(models.Model):
    name = models.CharField(max_length=10)
    abbrev = models.CharField(max_length=10)
    is_editable = models.BooleanField(default=True)

    @property
    def plural_name(self):
        if self.name is not None:
            return _inflect.plural(self.name)

    @property
    def plural_abbrev(self):
        if self.abbrev is not None:
            return _inflect.plural(self.abbrev)

    def __str__(self):
        return self.name


class BaseStockUnit(StokUnit):
    def add_alt_stock_unit(self, stock_unit_id):
        stock_unit = AlternateStockUnit.objects.get(pk=stock_unit_id)
        if (stock_unit is not None):
            stock_unit.add_base_stock_unit(self.pk)
            return stock_unit

    def remove_alt_stock_unit(self, stock_unit_id):
        stock_unit = AlternateStockUnit.objects.get(pk=stock_unit_id)
        if (stock_unit is not None):
            stock_unit.base_stock_units.remove(self)

    def update_alt_stock_units(self, stock_units):
        as_is_stock_unit_ids = list(
            map(lambda x: x.id, self.alternate_stock_units.all()))
        to_be_stock_unit_ids = list(
            map(lambda x: x.id, stock_units))
        to_remove = {*as_is_stock_unit_ids} - {*to_be_stock_unit_ids}
        to_add = {*to_be_stock_unit_ids} - {*as_is_stock_unit_ids}
        for rm_unit_id in to_remove:
            self.remove_alt_stock_unit(rm_unit_id)
        for add_unit_id in to_add:
            self.add_alt_stock_unit(add_unit_id)

    def clear_alt_stock_units(self):
        alt_stock_units = self.alternate_stock_units.all()
        for alt_stock_unit in alt_stock_units:
            alt_stock_unit.base_stock_units.remove(self)


class AlternateStockUnit(StokUnit):
    base_stock_units = models.ManyToManyField(BaseStockUnit, blank=True, related_name='alternate_stock_units')

    def add_base_stock_unit(self, stock_unit_id):
        stock_unit = BaseStockUnit.objects.get(pk=stock_unit_id)
        if (stock_unit is not None):
            self.base_stock_units.add(stock_unit)
            return stock_unit

    def remove_base_stock_unit(self, stock_unit_id):
        stock_unit = BaseStockUnit.objects.get(pk=stock_unit_id)
        if (stock_unit is not None):
            self.base_stock_units.remove(stock_unit)

    def update_base_stock_units(self, stock_units):
        as_is_stock_unit_ids = list(
            map(lambda x: x.id, self.base_stock_units.all()))
        to_be_stock_unit_ids = list(
            map(lambda x: x.id, stock_units))
        to_remove = {*as_is_stock_unit_ids} - {*to_be_stock_unit_ids}
        to_add = {*to_be_stock_unit_ids} - {*as_is_stock_unit_ids}
        for rm_unit_id in to_remove:
            self.remove_base_stock_unit(rm_unit_id)
        for add_unit_id in to_add:
            self.add_base_stock_unit(add_unit_id)

    def clear_base_stock_units(self):
        self.base_stock_units.clear()


class Item(models.Model):
    TAPE = 'tape'
    LINE = 'line'
    PAPER = 'paper'
    PANEL = 'panel'
    LIQUID = 'liquid'
    OTHER = 'others'
    TYPES = [
        (TAPE, 'Tape'),
        (LINE, 'Line'),
        (PAPER, 'Paper'),
        (PANEL, 'Panel'),
        (LIQUID, 'Liquid'),
        (OTHER, 'Other')
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPES, null=False, blank=False)
    override_price = MoneyField(null=True, max_digits=14, decimal_places=2, default_currency='PHP')
    is_override_price = models.BooleanField(default=False)
    is_raw_material = models.BooleanField(default=False)
    base_uom = models.ForeignKey(BaseStockUnit, on_delete=models.RESTRICT)
    alternate_uom = models.ForeignKey(AlternateStockUnit,
                                      on_delete=models.RESTRICT, null=True,
                                      blank=True)

    @property
    def full_name(self):
        properties = self.properties if self.properties is not None else ''
        return ('%s %s' % (self.name, properties)).strip()

    @property
    def price(self):
        if self.is_override_price and self.is_override_price is not None:
            return self.override_price
        elif self.latest_price_per_quantity is not None:
            return self.latest_price_per_quantity

    @property
    def latest_price_per_quantity(self):
        stocks = Stock.objects.filter(item__pk=self.id)
        if len(stocks) > 0:
            latest_stock = stocks.latest('created_at')
            if latest_stock is not None:
                return latest_stock.price_per_quantity

    @property
    def average_price_per_quantity(self):
        stocks = Stock.objects.filter(item__pk=self.id)
        stocks_len = len(stocks)
        if stocks_len > 0:
            total = 0
            for stock in stocks:
                total += stock.price_per_quantity
            return total / stocks_len

    @property
    def available_quantity(self):
        total = 0
        for stock in self.onhand_stocks:
            total += stock.available_quantity
        return total

    @property
    def onhand_quantity(self):
        total = 0
        for stock in self.onhand_stocks:
            total += stock.onhand_quantity
        return total

    @property
    def onhand_stocks(self):
        available_stocks = []
        related_stocks = Stock.objects.filter(item__pk=self.id)
        for stock in related_stocks:
            if stock.onhand_quantity > 0:
                available_stocks.append(stock)
        return available_stocks

    def deposit_stock(self, brand_name, base_quantity, price, alt_quantity=1):
        deposited = []
        for x in range(alt_quantity):
            stock = Stock.objects.create_stock(item=self, brand_name=brand_name,
                                               base_quantity=base_quantity, price=price)
            deposited.append(stock)
        return deposited

    def withdraw_stock(self, stock_request_id):
        stock_request = StockRequest.objects.get(pk=stock_request_id)
        stock = stock_request.stock
        quantity = stock_request.stock_unit.quantity
        stock.withdraw(quantity)
        stock_request.status = StockRequest.FULFILLED
        stock_request.save()

    def request_stock(self, quantity):
        stock_requests = []

        if self.available_quantity >= quantity:
            stocks = Stock.objects.filter(item=self)
            stocks_iter = stocks.iterator()
            qty_counter = 0

            while qty_counter < quantity:
                stock = next(stocks_iter)
                stock_qty = stock.available_quantity
                qty_remaining = quantity - qty_counter
                qty = qty_remaining % stock_qty if qty_remaining > stock_qty else qty_remaining
                stock_request = stock.request(qty)
                stock_requests.append(stock_request)
                qty_counter += qty

        return stock_requests

    def return_stock(self, stock_id, quantity):
        stock = Stock.objects.get(pk=stock_id)
        stock.returned(quantity)

    def expire_stock(self, stock_id, quantity):
        stock = Stock.objects.get(pk=stock_id)
        stock.expired(quantity)

    def __str__(self):
        return self.full_name


class StockManager(models.Manager):
    def create_stock(self, **data):
        stock = self.create(**data)
        stock.deposit(data['base_quantity'])
        return stock


class Stock(models.Model):
    objects = StockManager()
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, null=False)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    price = MoneyField(default=0, max_digits=14, decimal_places=2, default_currency='PHP')
    base_quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_quantity_full(self):
        return self.onhand_quantity == self.base_quantity

    @property
    def price_per_quantity(self):
        return self.price / self.base_quantity

    @property
    def available_quantity(self):
        def __get_sum(query_set):
            aggregate = query_set.aggregate(sum_stock=Sum('stock_unit__quantity'))
            aggr_sum = aggregate['sum_stock'] if aggregate['sum_stock'] is not None else 0
            return aggr_sum

        new_requests = StockRequest.objects.filter(stock=self, status=StockRequest.NEW)
        requested = __get_sum(new_requests)
        return self.onhand_quantity - requested

    @property
    def onhand_quantity(self):
        def __get_sum(query_set):
            aggregate = query_set.aggregate(sum_stock=Sum('stock_unit__quantity'))
            aggr_sum = aggregate['sum_stock'] if aggregate['sum_stock'] is not None else 0
            return aggr_sum

        added_stocks = StockMovement.objects.filter(Q(stock=self) &
                                                    (Q(action=StockMovement.DEPOSIT) |
                                                     Q(action=StockMovement.RETURN)))
        removed_stocks = StockMovement.objects.filter(Q(stock=self) &
                                                      (Q(action=StockMovement.WITHDRAW) |
                                                       Q(action=StockMovement.EXPIRED)))

        added = __get_sum(added_stocks)
        removed = __get_sum(removed_stocks)
        return added - removed

    def deposit(self, quantity):
        if quantity + self.onhand_quantity <= self.base_quantity:
            self._create_movement(quantity, StockMovement.DEPOSIT)
        else:
            raise DepositTooBig(quantity, self.onhand_quantity, self.base_quantity)

    def withdraw(self, quantity):
        if quantity <= self.onhand_quantity:
            self._create_movement(quantity, StockMovement.WITHDRAW)
        else:
            raise InsufficientStock(quantity, self.onhand_quantity, self.base_quantity)

    def request(self, quantity):
        if quantity <= self.available_quantity:
            return self._create_request(quantity)
        else:
            raise InsufficientStock(quantity, self.available_quantity, self.base_quantity)

    def returned(self, quantity):
        if quantity + self.onhand_quantity <= self.base_quantity:
            self._create_movement(quantity, StockMovement.RETURN)
        else:
            raise DepositTooBig(quantity, self.onhand_quantity, self.base_quantity)

    def expired(self, quantity):
        if quantity <= self.onhand_quantity:
            self._create_movement(quantity, StockMovement.EXPIRED)
        else:
            raise InvalidExpireQuantity(quantity, self.onhand_quantity)

    def _create_movement(self, quantity, action):
        stock_unit = StockUnit.objects.create(quantity=quantity)
        stock_movement = StockMovement.objects.create(action=action,
                                                      stock=self, stock_unit=stock_unit)
        return stock_movement

    def _create_request(self, quantity):
        stock_unit = StockUnit.objects.create(quantity=quantity)
        stock_request = StockRequest.objects.create(status=StockRequest.NEW,
                                                    stock=self, stock_unit=stock_unit)
        return stock_request


class StockUnit(models.Model):
    quantity = models.IntegerField(null=False, blank=False)


class StockLog(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    stock_unit = models.OneToOneField(StockUnit, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class StockRequest(StockLog):
    NEW = 'NEW'
    FULFILLED = 'FUL'
    CANCELLED = 'CNL'
    STATUS = [
        (NEW, 'New'),
        (FULFILLED, 'Fulfilled'),
        (CANCELLED, 'Cancelled'),
    ]
    status = models.CharField(max_length=3, choices=STATUS)
    last_modified = models.DateTimeField(auto_now=True)


class StockMovement(StockLog):
    DEPOSIT = 'DEP'
    WITHDRAW = 'WTH'
    RETURN = 'RET'
    EXPIRED = 'EXP'
    ACTIONS = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAW, 'Withdraw'),
        (RETURN, 'Return'),
        (EXPIRED, 'Expired'),
    ]
    action = models.CharField(max_length=3, choices=ACTIONS)
