from django.db import models
from django.db.models import Q, Sum
from djmoney.models.fields import MoneyField
from .exceptions import DepositTooBig, InsufficientStock
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


class Material(models.Model):
    name = models.CharField(max_length=100)
    base_uom = models.ForeignKey(BaseStockUnit,
                                 on_delete=models.RESTRICT, related_name='base_uom')
    alternate_uom = models.ForeignKey(AlternateStockUnit,
                                      on_delete=models.RESTRICT, null=True, blank=True, related_name='alternate_uom')

    @property
    def quantity_onhand(self):
        total = 0
        for stock in self.onhand_stocks:
            total += stock.onhand_quantity
        return total

    @property
    def latest_price_per_quantity(self):
        latest_stock = Stock.objects.filter(material__pk=self.id).latest('created_at')
        if latest_stock is not None:
            return latest_stock.price_per_quantity

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

    def withdraw_stock(self, stock_id, quantity):
        stock = Stock.objects.get(pk=stock_id)
        stock.withdraw(quantity)


class StockManager(models.Manager):
    def create_stock(self, **data):
        stock = self.create(**data)
        stock.deposit(data['base_quantity'])
        return stock


class Stock(models.Model):
    material = models.ForeignKey(Material, on_delete=models.RESTRICT, null=False)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    price = MoneyField(default=0, max_digits=14, decimal_places=2, default_currency='PHP')
    base_quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = StockManager()

    @property
    def is_quantity_full(self):
        return self.onhand_quantity == self.base_quantity

    @property
    def price_per_quantity(self):
        return self.price / self.base_quantity

    @property
    def onhand_quantity(self):
        added_stocks = StockMovement.objects.filter(Q(stock=self) &
                                                    (Q(action=StockMovement.DEPOSIT) |
                                                     Q(action=StockMovement.RETURN)))
        removed_stocks = StockMovement.objects.filter(Q(stock=self) &
                                                      (Q(action=StockMovement.WITHDRAW) |
                                                       Q(action=StockMovement.EXPIRED)))

        aggr_added = added_stocks.aggregate(sum_added=Sum('stock_unit__quantity'))
        aggr_removed = removed_stocks.aggregate(sum_removed=Sum('stock_unit__quantity'))

        added = aggr_added['sum_added'] if aggr_added['sum_added'] is not None else 0
        removed = aggr_removed['sum_removed'] if aggr_removed['sum_removed'] is not None else 0
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

    def _create_movement(self, quantity, action):
        stock_unit = StockUnit.objects.create(quantity=quantity)
        stock_movement = StockMovement.objects.create(action=action,
                                                      stock=self, stock_unit=stock_unit)
        return stock_movement


class StockUnit(models.Model):
    quantity = models.IntegerField(null=False, blank=False)


class StockMovement(models.Model):
    DEPOSIT = 'DEP'
    WITHDRAW = 'WTH'
    RETURN = 'RET'
    EXPIRED = 'EXP'
    ACTIONS = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAW, 'Withdraw'),
        (RETURN, 'Return'),
        (EXPIRED, 'Expired')
    ]
    action = models.CharField(max_length=3, choices=ACTIONS)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    stock_unit = models.OneToOneField(StockUnit, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
