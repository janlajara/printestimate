from django.db import models
from django.db.models import Q, Sum, Avg
from djmoney.models.fields import MoneyField
from .exceptions import DepositTooBig, InsufficientStock, InvalidExpireQuantity
from .properties.models import ItemProperties, Tape, Wire, Paper, Panel, Liquid
import inflect

_inflect = inflect.engine()


# Create your models here.
class BaseStockUnit(models.Model):
    name = models.CharField(max_length=10)
    abbrev = models.CharField(max_length=10)

    @property
    def plural_name(self):
        if self.name is not None:
            return _inflect.plural(self.name)

    @property
    def plural_abbrev(self):
        if self.abbrev is not None:
            return _inflect.plural(self.abbrev)


class AlternateStockUnit(BaseStockUnit):
    base_stock_units = models.ManyToManyField(BaseStockUnit, related_name='base_stock_units')
    # type = models.CharField(max_length=15, choices=Item.TYPES, null=False, blank=False)


class ItemManager(models.Manager):

    def create_item(self, **data):
        # remove properties if supplied. to be overridden
        if data.get('properties') is not None:
            data.pop('properties')

        item = self.create(**data)
        type_key = data.get('type')
        if type_key is not None:
            clazz = ItemManager._get_properties_class(type_key)
            if clazz is not None:
                properties = clazz.objects.create()
                item.properties = properties
                item.save()

        return item

    @staticmethod
    def _get_properties_class(item_type):
        mapping = {
            Item.TAPE: Tape,
            Item.WIRE: Wire,
            Item.PAPER_SHEET: Paper,
            Item.PAPER_ROLL: Paper,
            Item.PANEL: Panel,
            Item.LIQUID: Liquid,
            Item.OTHER: None
        }
        if mapping.get(item_type) is not None:
            return mapping[item_type]


class Item(models.Model):
    TAPE = 'tape'
    WIRE = 'wire'
    PAPER_SHEET = 'papersheet'
    PAPER_ROLL = 'paperroll'
    PANEL = 'panel'
    LIQUID = 'liquid'
    OTHER = 'other'
    TYPES = [
        (TAPE, 'Tape'),
        (WIRE, 'Wire'),
        (PAPER_SHEET, 'Paper - Sheet'),
        (PAPER_ROLL, 'Paper - Roll'),
        (PANEL, 'Panel'),
        (LIQUID, 'Liquid'),
        (OTHER, 'Other')
    ]

    objects = ItemManager()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPES, null=False, blank=False)
    properties = models.OneToOneField(ItemProperties, on_delete=models.RESTRICT, null=True)
    override_price = MoneyField(null=True, blank=False, max_digits=14, decimal_places=2, default_currency='PHP')
    is_override_price = models.BooleanField(default=False)
    is_raw_material = models.BooleanField(default=False)
    base_uom = models.ForeignKey(BaseStockUnit, on_delete=models.RESTRICT,
                                 related_name='base_uom')
    alternate_uom = models.ForeignKey(AlternateStockUnit,
                                      on_delete=models.RESTRICT, null=True,
                                      blank=True, related_name='alternate_uom')

    @property
    def full_name(self):
        return ('%s %s' % (self.name, self.properties)).strip()

    @property
    def price(self):
        if self.is_override_price and self.is_override_price is not None:
            return self.is_override_price
        else:
            return self.latest_price_per_quantity

    @property
    def latest_price_per_quantity(self):
        latest_stock = Stock.objects.filter(item__pk=self.id).latest('created_at')
        if latest_stock is not None:
            return latest_stock.price_per_quantity

    @property
    def average_price_per_quantity(self):
        stocks = Stock.objects.filter(item__pk=self.id)
        stocks_len = len(stocks)
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
