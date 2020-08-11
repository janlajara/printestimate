class DepositTooBig(Exception):
    def __init__(self, deposit_quantity, in_stock_quantity, limit_quantity):
        self.message = 'Cannot deposit %s more units to %s/%s stock' % \
                       (deposit_quantity, in_stock_quantity, limit_quantity)
        super().__init__(self.message)


class InsufficientStock(Exception):
    def __init__(self, withdraw_quantity, in_stock_quantity, limit_quantity):
        self.message = 'Cannot withdraw %s units from %s/%s stock' % \
                       (withdraw_quantity, in_stock_quantity, limit_quantity)
        super().__init__(self.message)