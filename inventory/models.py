from django.db import models
from django.db.models import Q, Sum, Avg, Count
from djmoney.models.fields import MoneyField
from .exceptions import DepositTooBig, InsufficientStock, \
    InvalidExpireQuantity, IllegalUnboundedDeposit, \
        IllegalItemRequestOperation, IllegalItemRequestGroupOperation
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
    OTHER = 'other'
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
                        item_request__status__in=[ItemRequest.DRAFT, 
                            ItemRequest.FOR_APPROVAL,
                            ItemRequest.APPROVED])))
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

    def request(self, quantity, auto_assign=False):
        request = ItemRequest.objects.create_request(item=self, 
            quantity_needed=quantity)

        if auto_assign and self.available_quantity > 0:
            stock_requests = self.request_stock(quantity)
            request.allocate_stocks(stock_requests)

        return request

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

    # TO DELETE. Might not be necessary.
    #def withdraw_stock(self, stock_request_id):
    #    stock_request = StockRequest.objects.get(pk=stock_request_id)
    #    item_request = stock_request.item_request
    #    if item_request.status == ItemRequest.APPROVED:
    #        stock = stock_request.stock
    #        quantity = stock_request.stock_unit.quantity
    #        stock.withdraw(quantity)
    #    else:
    #        raise IllegalWithdrawal(item_request.status)

    def request_stock(self, quantity):
        stock_requests = []
        target_quantity = min(self.available_quantity, quantity)

        stocks = Stock.objects.filter(item=self)
        stocks_iter = stocks.iterator()
        qty_counter = 0

        while qty_counter < target_quantity:
            stock = next(stocks_iter)
            stock_qty = stock.available_quantity
            qty_remaining = target_quantity - qty_counter
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


class ItemRequestGroup(models.Model):
    OPEN = 'Open'
    CLOSED = 'Closed'

    finished = models.BooleanField(blank=True, default=False)
    reason = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status(self):
        status = ItemRequestGroup.OPEN
        aggregate = self._get_item_request_aggregate()
        if aggregate.get('closed') > 0 and aggregate.get('open') == 0:
            status = ItemRequestGroup.CLOSED

        return status

    @property
    def progress_rate(self):
        aggregate = self._get_item_request_aggregate()
        total = aggregate.get('open') + aggregate.get('closed')
        if total > 0:
            return aggregate.get('closed') / total
        else:
            return 0

    def _get_item_request_aggregate(self):
        aggregate = ItemRequest.objects.aggregate(
            open=Count('status', 
                filter=Q(status__in=[ItemRequest.DRAFT, ItemRequest.FOR_APPROVAL,
                    ItemRequest.APPROVED, ItemRequest.PARTIALLY_FULFILLED], 
                    item_request_group=self)),
            closed=Count('status', 
                filter=Q(status__in=[ItemRequest.FULFILLED, ItemRequest.CANCELLED], 
                    item_request_group=self))
        )
        open = aggregate.get('open') or 0
        closed = aggregate.get('closed') or 0
        return {
            "open": open, 
            "closed": closed
        }

    def finish(self):
        if self.status == ItemRequestGroup.CLOSED:
            self.finished = True
        else:
            raise IllegalItemRequestGroupOperation(True, 
                ItemRequestGroup.CLOSED)
    
    def unfinish(self):
        if self.status == ItemRequestGroup.CLOSED:
            self.finished = False
        else:
            raise IllegalItemRequestGroupOperation(False, 
                ItemRequestGroup.CLOSED)


class ItemRequestManager(models.Manager):
    def create_request(self, **data):
        item_request = self.create(**data)
        request_log = ItemRequestLog.objects.create(
                item_request=item_request, 
                status=ItemRequest.DRAFT,
                comments='New item request.')
        return item_request


class ItemRequest(models.Model):
    DRAFT = 'DFT'
    FOR_APPROVAL = 'FAP'
    APPROVED = 'APP'
    DISAPPROVED = 'DAP'
    PARTIALLY_FULFILLED = 'PFL'
    FULFILLED = 'FUL'
    CANCELLED = 'CNL'
    STATUS = [
        (DRAFT, 'Draft'),
        (FOR_APPROVAL, 'For Approval'),
        (APPROVED, 'Approved'),
        (DISAPPROVED, 'Disapproved'),
        (PARTIALLY_FULFILLED, 'Partially Fulfilled'),
        (FULFILLED, 'Fulfilled'),
        (CANCELLED, 'Cancelled'),
    ]
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (FOR_APPROVAL, 'For Approval'),
        (APPROVED, 'Approve'),
        (DISAPPROVED, 'Disapprove'),
        (PARTIALLY_FULFILLED, 'Partially Fulfill'),
        (FULFILLED, 'Fulfill'),
        (CANCELLED, 'Cancel'),
    ]

    objects = ItemRequestManager()
    item = models.ForeignKey(Item, on_delete=models.CASCADE, 
        null=False, related_name='item_request')
    status = models.CharField(max_length=3, choices=STATUS, default='DFT')
    item_request_group = models.ForeignKey(ItemRequestGroup, null=True, blank=True,
        on_delete=models.RESTRICT, related_name='item_requests')
    quantity_needed = models.IntegerField(null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def is_fully_allocated(self):
        return self.missing_allocation == 0

    @property
    def missing_allocation(self):
        return max(self.quantity_needed - self.quantity_stocked, 0)

    @property
    def missing_allocation_formatted(self):
        return self._format_quantity(self.missing_allocation)

    @property
    def stock_requests(self):
        return StockRequest.objects.filter(item_request=self)

    @property
    def unfulfilled_stock_requests(self):
        return StockRequest.objects.filter(item_request=self, is_fulfilled=False)

    @property
    def allocation_rate(self):
        allocated = (self.quantity_needed - self.missing_allocation)
        return allocated / self.quantity_needed

    @property
    def quantity_needed_formatted(self):
        return self._format_quantity(self.quantity_needed)

    @property
    def quantity_stocked(self):
        aggregated = StockRequest.objects.aggregate(
            quantity_stocked=Sum('stock_unit__quantity',
                filter=Q(item_request=self)))
        stocked = aggregated.get('quantity_stocked') or 0
        return stocked

    @property
    def quantity_stocked_formatted(self):
        return self._format_quantity(self.quantity_stocked)

    @property
    def status_choices(self):
        def __get(status_codes):
            return [status for status in ItemRequest.STATUS_CHOICES 
                if status[0] in status_codes]
        def __get_partially_fulfilled_choices():
            if self.is_fully_allocated:
                return __get([ItemRequest.FULFILLED])
            elif len(self.unfulfilled_stock_requests.all()) > 0:
                return __get([ItemRequest.PARTIALLY_FULFILLED])
            else:
                return []
        def __get_approved_choices():
            if self.is_fully_allocated:
                return __get([ItemRequest.FULFILLED, ItemRequest.CANCELLED])
            elif self.missing_allocation > 0 and self.quantity_stocked > 0:
                return __get([ItemRequest.PARTIALLY_FULFILLED, ItemRequest.CANCELLED])
            else:
                return __get([ItemRequest.CANCELLED])

        choices_map = {
            ItemRequest.DRAFT: 
                __get([ItemRequest.FOR_APPROVAL, ItemRequest.CANCELLED]),
            ItemRequest.FOR_APPROVAL: 
                __get([ItemRequest.APPROVED, ItemRequest.DISAPPROVED, 
                    ItemRequest.CANCELLED]),
            ItemRequest.DISAPPROVED: 
                __get([ItemRequest.CANCELLED]),
            ItemRequest.CANCELLED: 
                __get([ItemRequest.DRAFT]),
            ItemRequest.FULFILLED: []
        }
        choices_map[ItemRequest.PARTIALLY_FULFILLED] = __get_partially_fulfilled_choices()
        choices_map[ItemRequest.APPROVED] = __get_approved_choices()

        return choices_map[self.status]

    def allocate_stocks(self, stock_requests):
        if not self.is_fully_allocated:
            for stock_request in stock_requests:
                self.stock_requests.add(stock_request)
        else:
            raise IllegalItemRequestOperation(
                message="Cannot allocate more stocks. %s are already allocated"
                    % self.quantity_stocked_formatted)

    def draft(self, comments=None):
        if self.status == ItemRequest.CANCELLED:
            self.status = ItemRequest.DRAFT
            self.save()
            self._create_log(self.status, comments)
        else:
            raise IllegalItemRequestOperation(
                ItemRequest.CANCELLED, self.status, 
                ItemRequest.DRAFT)

    def for_approval(self, comments=None):
        if self.status == ItemRequest.DRAFT:
            self.status = ItemRequest.FOR_APPROVAL
            self.save()
            self._create_log(self.status, comments)
        else:
            raise IllegalItemRequestOperation(
                ItemRequest.DRAFT, self.status, 
                ItemRequest.FOR_APPROVAL)

    def approve(self, comments=None):
        if self.status == ItemRequest.FOR_APPROVAL:
            self.status = ItemRequest.APPROVED
            self.save()
            self._create_log(self.status, comments)
        else:
            raise IllegalItemRequestOperation(
                ItemRequest.FOR_APPROVAL, self.status, 
                ItemRequest.APPROVED)
    
    def disapprove(self, comments=None):
        if self.status == ItemRequest.FOR_APPROVAL:
            self.status = ItemRequest.DISAPPROVED
            self.save()
            self._create_log(self.status, comments)
        else:  
            raise IllegalItemRequestOperation(
                ItemRequest.FOR_APPROVAL, self.status,
                ItemRequest.DISAPPROVED)

    def cancel(self, comments=None):
        expected_statuses = [ItemRequest.DRAFT, 
            ItemRequest.FOR_APPROVAL, 
            ItemRequest.APPROVED, ItemRequest.DISAPPROVED]
        if self.status in expected_statuses:
            self.status = ItemRequest.CANCELLED
            self.save()
            self._create_log(self.status, comments)
        else:
            raise IllegalItemRequestOperation(
                expected_statuses, self.status,
                ItemRequest.CANCELLED) 

    def partially_fulfill(self, comments=None):
        if self.status in [ItemRequest.APPROVED, ItemRequest.PARTIALLY_FULFILLED]:
            if len(self.unfulfilled_stock_requests) == 0:
                raise IllegalItemRequestOperation(
                    message="There are no stock requests to fulfill.")

            if self.missing_allocation > 0 and self.quantity_stocked > 0:
                fulfilled = []
                for stock_request in self.unfulfilled_stock_requests:
                    stock_request.fulfill()
                    fulfilled.append(stock_request)

                self.status = ItemRequest.PARTIALLY_FULFILLED
                self.save()
                self._create_log(self.status, comments)

                return fulfilled
            else:
                raise IllegalItemRequestOperation(
                    message="Cannot proceed. Item request must only be partially allocated.")
        else:
            raise IllegalItemRequestOperation(
                ItemRequest.APPROVED, self.status,
                ItemRequest.PARTIALLY_FULFILLED) 

    def fulfill(self, comments=None):
        if self.status in [ItemRequest.APPROVED, ItemRequest.PARTIALLY_FULFILLED]:
            if len(self.unfulfilled_stock_requests) == 0:
                raise IllegalItemRequestOperation(
                    message="There are no stock requests to fulfill.")

            if self.is_fully_allocated:
                fulfilled = []
                for stock_request in self.unfulfilled_stock_requests:
                    stock_request.fulfill()
                    fulfilled.append(stock_request)

                self.status = ItemRequest.FULFILLED
                self.save()
                self._create_log(self.status, comments)

                return fulfilled
            else:
                raise IllegalItemRequestOperation(
                    message="Cannot fulfill request when stock is not fully allocated. Missing %s." \
                        % self.missing_allocation_formatted)
        else:
            raise IllegalItemRequestOperation(
                ItemRequest.APPROVED, self.status,
                ItemRequest.FULFILLED) 

    def _create_log(self, status, comments=None):
        if status is not None:
            request_log = ItemRequestLog.objects.create(
                item_request=self, status=status,
                comments=comments)
            return request_log

    def _format_quantity(self, quantity):
        base_uom = self.item.base_uom
        unit = base_uom.plural_abbrev
        if quantity == 1:
            unit = base_uom.abbrev
        return '%s %s' % (f'{quantity:,}', unit)


class ItemRequestLog(models.Model):
    item_request = models.ForeignKey(ItemRequest, 
        on_delete=models.CASCADE, related_name='item_request_logs')
    status = models.CharField(max_length=3, 
        choices=ItemRequest.STATUS, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(null=True, blank=True)


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
                filter=Q(stock=self, item_request__status__in=[
                    ItemRequest.DRAFT,
                    ItemRequest.FOR_APPROVAL, 
                    ItemRequest.APPROVED])))
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
        stock_request = StockRequest.objects.create(stock=self, stock_unit=stock_unit)
        return stock_request


class StockUnit(models.Model):
    quantity = models.IntegerField(null=False, blank=False)

    @property
    def quantity_formatted(self):
        base_uom = self.stock_log.stock.item.base_uom
        unit = base_uom.plural_abbrev
        qty = self.quantity
        if qty == 1:
            unit = base_uom.abbrev
        return '%s %s' % (f'{qty:,}', unit)


class StockLog(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, 
        related_name="stock_log")
    stock_unit = models.OneToOneField(StockUnit, on_delete=models.CASCADE, 
        related_name='stock_log')
    created = models.DateTimeField(auto_now_add=True)


class StockRequest(StockLog):
    item_request = models.ForeignKey(ItemRequest, on_delete=models.RESTRICT, 
        blank=True, null=True, related_name='stock_requests')
    is_fulfilled = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)

    def fulfill(self):
        if not self.is_fulfilled:
            self.is_fulfilled = True
            quantity = self.stock_unit.quantity
            self.stock.withdraw(quantity)
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

