class Order:
    def __init__(self, quantity, final_type, order_id, delivery_day, status=None, dispatch_conveyor=None):
        self.quantity = quantity
        self.final_type = final_type
        self.order_id = order_id
        self.delivery_day = delivery_day
        self.status= status
        self.dispatch_conveyor= dispatch_conveyor
        self.pieces_loaded = 0
    
    