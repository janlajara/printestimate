from django.db import models
from django.db.models import Q, Sum, Avg, Count
from djmoney.models.fields import MoneyField
from .exceptions import DepositTooBig, InsufficientStock, \
    InvalidExpireQuantity, IllegalUnboundedDeposit, IllegalWithdrawal
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
    override_price = MoneyField(null=True, max_digits=14, decimal_places=2, 
        default_currency='PHP')
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
        if self.is_override_price and self.override_price is not None:
            return self.override_price
        elif self.latest_price_per_quantity is not None:
            return self.latest_price_per_quantity

    @property
    def latest_stock(self):
        stocks = Stock.objects.filter(item__pk=self.id)
        if len(stocks) > 0:
            latest_stock = stocks.latest('created_at')
            if latest_stock is not None:
                return latest_stock

    @property
    def latest_price_per_quantity(self):
        latest_stock = self.latest_stock
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
        stock_ids = [stock.pk for stock in self.stocks.all()]
        sr_aggregate = StockRequest.objects.aggregate(
            requested_stocks=Sum('stock_unit__quantity',
                filter=Q(stock_id__in=stock_ids, 
                        status__in=[StockRequest.NEW, StockRequest.APPROVED])))
        requested = sr_aggregate.get('requested_stocks') or 0
        return self.onhand_quantity - requested

    @property
    def available_quantity_formatted(self):
        unit = self.base_uom.plural_abbrev
        qty = self.available_quantity
        if qty == 1:
            unit = self.base_uom.abbrev
        return '%s %s' % (f'{qty:,}', unit)

    @property
    def onhand_quantity(self):
        stock_ids = [stock.pk for stock in self.stocks.all()]
        sm_aggregate = StockMovement.objects.aggregate(
            added_stocks=Sum('stock_unit__quantity', 
                filter=Q(stock_id__in=stock_ids, 
                        action__in=[StockMovement.DEPOSIT, StockMovement.RETURN])),
            removed_stocks=Sum('stock_unit__quantity', 
                filter=Q(stock_id__in=stock_ids,
                        action__in=[StockMovement.WITHDRAW, StockMovement.EXPIRED]))
        )
        removed = sm_aggregate.get('removed_stocks') or 0
        added = sm_aggregate.get('added_stocks') or 0
        return added - removed

    @property
    def onhand_quantity_formatted(self):
        unit = self.base_uom.plural_abbrev
        qty = self.onhand_quantity
        if qty == 1:
            unit = self.base_uom.abbrev
        return '%s %s' % (f'{qty:,}', unit)

    @property
    def onhand_stocks(self):
        available_stocks = []
        related_stocks = Stock.objects.filter(item__pk=self.id)
        for stock in related_stocks:
            if stock.onhand_quantity > 0:
                available_stocks.append(stock)
        return available_stocks

    def deposit_stock(self, brand_name, base_quantity, price, alt_quantity=1, unbounded=False):
        deposited = []
        if unbounded and alt_quantity > 1:
            raise IllegalUnboundedDeposit(alt_quantity)

        for x in range(alt_quantity):
            stock = Stock.objects.create_stock(item=self, brand_name=brand_name,
                                               base_quantity=base_quantity, price=price,
                                               unbounded=unbounded)
            deposited.append(stock)
        return deposited

    def withdraw_stock(self, stock_request_id):
        stock_request = StockRequest.objects.get(pk=stock_request_id)
        if stock_request.status == StockRequest.APPROVED:
            stock = stock_request.stock
            quantity = stock_request.stock_unit.quantity
            stock.withdraw(quantity)
            stock_request.status = StockRequest.FULFILLED
            stock_request.save()
        else:
            raise IllegalWithdrawal(stock_request.status)

    def request_stock(self, quantity, reason=None):
        request_group = None

        if self.available_quantity >= quantity:
            stocks = Stock.objects.filter(item=self)
            stocks_iter = stocks.iterator()
            qty_counter = 0
            stock_requests = []

            while qty_counter < quantity:
                stock = next(stocks_iter)
                stock_qty = stock.available_quantity
                qty_remaining = quantity - qty_counter
                qty = qty_remaining % stock_qty if qty_remaining > stock_qty else qty_remaining
                stock_request = stock.request(qty)
                stock_requests.append(stock_request)
                qty_counter += qty
            request_group = StockRequestGroup.objects.create(reason=reason)
            request_group.stock_requests.set(stock_requests)

        return request_group

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
        deposit_quantity = data.get('base_quantity', 1)
        if data.get('unbounded', False):
            # Remove base_quantity from data so it defaults to 1
            data.pop('base_quantity')
        stock = self.create(**data)
        stock.deposit(deposit_quantity)
        return stock


class Stock(models.Model):
    objects = StockManager()
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, 
        null=False, related_name='stocks')
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    price = MoneyField(default=0, max_digits=14, decimal_places=2, 
        default_currency='PHP')
    base_quantity = models.IntegerField(default=1)
    unbounded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_quantity_full(self):
        if self.unbounded:
            return False
        else:
            return self.onhand_quantity == self.base_quantity

    @property
    def price_per_quantity(self):
        if self.unbounded:
            return self.price
        else:
            return self.price / self.base_quantity

    @property
    def base_quantity_formatted(self):
        unit = self.item.base_uom.plural_abbrev
        qty = self.base_quantity
        if qty == 1:
            unit = self.item.base_uom.abbrev
        return '%s %s' % (f'{qty:,}', unit)

    @property
    def available_quantity(self):
        aggregate = StockRequest.objects.aggregate(
            requested_quantity=Sum('stock_unit__quantity',
                filter=Q(stock=self, status__in=[StockRequest.NEW, StockRequest.APPROVED])))
        requested = aggregate.get('requested_quantity', 0) or 0
        return self.onhand_quantity - requested

    @property
    def available_quantity_formatted(self):
        unit = self.item.base_uom.plural_abbrev
        qty = self.available_quantity
        if qty == 1:
            unit = self.item.base_uom.abbrev
        return '%s %s' % (f'{qty:,}', unit)

    @property
    def onhand_quantity(self):
        aggregate = StockMovement.objects.aggregate(
            added_stocks=Sum('stock_unit__quantity', 
                filter=Q(stock=self, action__in=[StockMovement.DEPOSIT, StockMovement.RETURN])),
            removed_stocks=Sum('stock_unit__quantity', 
                filter=Q(stock=self, action__in=[StockMovement.WITHDRAW, StockMovement.EXPIRED])))

        added = aggregate.get('added_stocks', 0) or 0 
        removed = aggregate.get('removed_stocks', 0) or 0 

        return added - removed

    @property
    def onhand_quantity_formatted(self):
        unit = self.item.base_uom.plural_abbrev
        qty = self.onhand_quantity
        if qty == 1:
            unit = self.item.base_uom.abbrev
        return '%s %s' % (f'{qty:,}', unit)

    def deposit(self, quantity):
        if self.unbounded or (quantity + self.onhand_quantity <= self.base_quantity):
            self._create_movement(quantity, StockMovement.DEPOSIT)
        else:
            raise DepositTooBig(quantity, self.onhand_quantity, self.base_quantity)

    def withdraw(self, quantity):
        if self.unbounded or (quantity <= self.onhand_quantity):
            self._create_movement(quantity, StockMovement.WITHDRAW)
        else:
            raise InsufficientStock(quantity, self.onhand_quantity, self.base_quantity)

    def request(self, quantity):
        if quantity <= self.available_quantity:
            return self._create_request(quantity)
        else:
            raise InsufficientStock(quantity, self.available_quantity, self.base_quantity)

    def returned(self, quantity):
        if self.unbounded or (quantity + self.onhand_quantity <= self.base_quantity):
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
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="stock_log")
    stock_unit = models.OneToOneField(StockUnit, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class StockRequestGroup(models.Model):
    PENDING = 'Pending'
    FINISHED = 'Finished'

    reason = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status(self):
        status = StockRequestGroup.PENDING

        aggregate = StockRequest.objects.aggregate(
            pending=Count('status', 
                filter=Q(status__in=[StockRequest.NEW, StockRequest.APPROVED], 
                    stock_request_group=self)),
            finished=Count('status', 
                filter=Q(status__in=[StockRequest.FULFILLED, StockRequest.CANCELLED], 
                    stock_request_group=self))
        )
        pending = aggregate.get('pending') or 0
        finished = aggregate.get('finished') or 0
        if finished > 0 and pending == 0:
            status = StockRequestGroup.FINISHED

        return status


class StockRequest(StockLog):
    NEW = 'NEW'
    APPROVED = 'APP'
    FULFILLED = 'FUL'
    CANCELLED = 'CNL'
    STATUS = [
        (NEW, 'New'),
        (APPROVED, 'Approved'),
        (FULFILLED, 'Fulfilled'),
        (CANCELLED, 'Cancelled'),
    ]
    status = models.CharField(max_length=3, choices=STATUS, default='NEW')
    stock_request_group = models.ForeignKey(StockRequestGroup, null=True, blank=True,
        on_delete=models.RESTRICT, related_name='stock_requests')
    last_modified = models.DateTimeField(auto_now=True)

    def approve(self):
        self.status = StockRequest.APPROVED
        self.save()
    
    def cancel(self):
        self.status = StockRequest.CANCELLED
        self.save()


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

