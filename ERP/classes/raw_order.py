class Raw_order:
    def __init__(self, supplier ,piece, min_quantity, price_pp, delivery_days):
            self.supplier = supplier
            self.piece = piece
            self.min_quantity = min_quantity
            self.price_pp = price_pp
            self.delivery_days = delivery_days
    
    def __str__(self):
        return f"Supplier: {self.supplier}, Piece: {self.piece}, Min Quantity: {self.min_quantity}, Price per piece: {self.price_pp}, Delivery days: {self.delivery_days}"
        
    @staticmethod
    def choose_raw_order(piece_type, quantity, available_time):
        best_raw_order = None
        fastest_raw_order = None

        min_delivery_time = float('inf')
        min_cost = float('inf')

        for order in raw_orders:

            #print(f"Order: {order.supplier}, {order.piece}, {order.min_quantity}, {order.price_pp}, {order.delivery_days}")
            #print(f"Piece type: {piece_type}, Quantity: {quantity}, Available time: {available_time}")
            if order.piece == piece_type:
                delivery_time = order.delivery_days
                cost = order.price_pp * quantity
                #print(f"Delivery time: {delivery_time}, Cost: {cost}")
                if (delivery_time <= available_time and cost < min_cost) and (quantity >= order.min_quantity):
                    best_raw_order = order
                    min_cost = cost
                if (delivery_time < min_delivery_time):
                    min_delivery_time = delivery_time
                    fastest_raw_order = order

        if best_raw_order is None:
            best_raw_order = fastest_raw_order
 
        return best_raw_order
    
orderA1 = Raw_order(supplier="A",piece="P1", min_quantity=16, price_pp=30, delivery_days=4)
orderA2 = Raw_order(supplier="A",piece="P2", min_quantity=16, price_pp=10, delivery_days=4)

orderB1 = Raw_order(supplier="B", piece="P1", min_quantity=8, price_pp=45, delivery_days=2)
orderB2 = Raw_order(supplier="B",piece="P2", min_quantity=8, price_pp=15, delivery_days=2)

orderC1 = Raw_order(supplier="C",piece="P1", min_quantity=4, price_pp=55, delivery_days=1)
orderC2 = Raw_order(supplier="C",piece="P2", min_quantity=4, price_pp=18, delivery_days=1)

raw_orders = [orderA1, orderA2, orderB1, orderB2, orderC1, orderC2]

final_to_raw = {
    "P5":"P1",
    "P6":"P1",
    "P7":"P2",
    "P9":"P2"
}

