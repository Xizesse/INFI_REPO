from pieces import P1, P2

class Supplier:

    def __init__(self, orders):
        self.orders = orders

    class Raw_order:
        def __init__(self, piece, min_quantity, price_pp, delivery_days):
            self.piece = piece
            self.min_quantity = min_quantity
            self.price_pp = price_pp
            self.delivery_days = delivery_days
        

order1 = Supplier.Raw_order(piece="P1", min_quantity=16, price_pp=30, delivery_days=4)
order2 = Supplier.Raw_order(piece="P2", min_quantity=16, price_pp=10, delivery_days=4)
SupllierA = Supplier(orders=[order1, order2])

order1 = Supplier.Raw_order(piece="P1", min_quantity=8, price_pp=45, delivery_days=2)
order2 = Supplier.Raw_order(piece="P2", min_quantity=8, price_pp=15, delivery_days=2)
SupllierB = Supplier(orders=[order1, order2])

order1 = Supplier.Raw_order(piece="P1", min_quantity=4, price_pp=55, delivery_days=1)
order2 = Supplier.Raw_order(piece="P2", min_quantity=4, price_pp=18, delivery_days=1)
SupllierC = Supplier(orders=[order1, order2])