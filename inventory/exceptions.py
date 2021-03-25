class DepositTooBig(Exception):
    def __init__(self, deposit_quantity, onhand_quantity, limit_quantity):
        self.message = 'Cannot deposit or return %s more units. Stock has %s/%s units on-hand already.' % \
                       (deposit_quantity, onhand_quantity, limit_quantity)
        super().__init__(self.message)


class InsufficientStock(Exception):
    def __init__(self, withdraw_quantity, available_quantity, limit_quantity):
        self.message = 'Cannot withdraw or request %s units. Stock has insufficient quantity of %s/%s.' % \
                       (withdraw_quantity, available_quantity, limit_quantity)
        super().__init__(self.message)


class InvalidExpireQuantity(Exception):
    def __init__(self, expire_quantity, onhand_quantity):
        self.message = 'Cannot expire %s units. Stock only has %s units on-hand.' % \
                       (expire_quantity, onhand_quantity)
        super().__init__(self.message)


class IllegalUnboundedDeposit(Exception):
    def __init__(self, alt_quantity):
        self.message = 'Cannot deposit unbounded stock when alternate quantity of % units is greater than 1' % \
            alt_quantity
        super().__init__(self.message)
