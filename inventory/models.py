from django.db import models
from djmoney.models.fields import MoneyField
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
    def latest_price_per_quantity(self):
        latest_stock = Stock.objects.filter(material__pk=self.id).latest('created_at')
        if latest_stock is not None:
            return latest_stock.price_per_quantity

    def deposit_stock(self, brand_name, base_quantity, price):
        stock = Stock.objects.create(material=self, brand_name=brand_name,
            base_quantity=base_quantity, price=price)
        return stock

class Stock(models.Model):
    material = models.ForeignKey(Material,
        on_delete=models.RESTRICT, null=False)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    price = MoneyField(default=0, max_digits=14, decimal_places=2, default_currency='PHP')
    base_quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def price_per_quantity(self):
        return self.price / self.base_quantity

class StockMovement(models.Model):
    CREATE = 'create'
    DEPOSIT = 'deposit'