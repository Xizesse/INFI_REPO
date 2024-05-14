class Order:
    def __init__(self, client, quantity, final_type, order_id, delivery_day, late_pen, early_pen):
        self.client = client
        self.quantity = quantity
        self.final_type = final_type
        self.order_id = order_id
        self.delivery_day = delivery_day
        self.late_pen = late_pen
        self.early_pen = early_pen
    
    