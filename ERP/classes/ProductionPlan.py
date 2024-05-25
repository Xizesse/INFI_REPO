class ProductionPlan:
    def __init__(self, order_id, start_date):
        self.start_date = start_date
        self.order_id = order_id

class Prod_Quantities:
    def __init__(self, start_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity):
        self.start_date = start_date
        self.p5_quantity = p5_quantity
        self.p6_quantity = p6_quantity
        self.p7_quantity = p7_quantity
        self.p9_quantity = p9_quantity
        
