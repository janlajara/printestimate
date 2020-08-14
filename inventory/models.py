from django.db import models
from django.db.models import Q, Sum
from djmoney.models.fields import MoneyField
from .exceptions import DepositTooBig, InsufficientStock, InvalidExpireQuantity
from .material.models import MaterialProperties, Tape, Wire, Paper, Panel, Liquid
import inflect

_inflect = inflect.engine()


# Create your models here.
class MaterialType:
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
    MAPPING = {
        TAPE: Tape,
        WIRE: Wire,
        PAPER_SHEET: Paper,
        PAPER_ROLL: Paper,
        PANEL: Panel,
        LIQUID: Liquid,
        OTHER: None
    }


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
    type = models.CharField(max_length=15, choices=MaterialType.TYPES, null=False, blank=False)


class MaterialManager(models.Manager):

    def create_material(self, **data):
        # remove properties if supplied. to be overridden
        if data.get('properties') is not None:
            data.pop('properties')

        material = self.create(**data)
        type_key = data.get('type')

        if type_key is not None and MaterialType.MAPPING.get(type_key) is not None:
            properties = MaterialType.MAPPING[type_key].objects.create()
            material.properties = properties
            material.save()

        return material


class Material(models.Model):
    objects = MaterialManager()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=MaterialType.TYPES, null=False, blank=False)
    properties = models.OneToOneField(MaterialProperties, on_delete=models.RESTRICT, null=True)
    base_uom = models.ForeignKey(BaseStockUnit, on_delete=models.RESTRICT,
                                 related_name='base_uom')
    alternate_uom = models.ForeignKey(AlternateStockUnit,
                                      on_delete=models.RESTRICT, null=True,
                                      blank=True, related_name='alternate_uom')

    @property
    def latest_price_per_quantity(self):
        latest_stock = Stock.objects.filter(material__pk=self.id).latest('created_at')
        if latest_stock is not None:
            return latest_stock.price_per_quantity

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
        related_stocks = Stock.objects.filter(material__pk=self.id)
        for stock in related_stocks:
            if stock.onhand_quantity > 0:
                available_stocks.append(stock)
        return available_stocks

    def deposit_stock(self, brand_name, base_quantity, price, alt_quantity=1):
        deposited = []
        for x in range(alt_quantity):
            stock = Stock.objects.create_stock(material=self, brand_name=brand_name,
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
            stocks = Stock.objects.filter(material=self)
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


class StockManager(models.Manager):
    def create_stock(self, **data):
        stock = self.create(**data)
        stock.deposit(data['base_quantity'])
        return stock


class Stock(models.Model):
    objects = StockManager()
    material = models.ForeignKey(Material, on_delete=models.RESTRICT, null=False)
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
        new = __get_sum(new_requests)
        requested = new
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
