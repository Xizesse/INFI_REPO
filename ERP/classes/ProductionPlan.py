import math

class ProductionPlan:
    def __init__(self, order_id, start_date, workpiece, quantity):
        self.start_date = start_date
        self.order_id = order_id
        self.workpiece = workpiece
        self.quantity = quantity

    def __str__(self):
        return f"Order ID: {self.order_id}, Start Date: {self.start_date}, Workpiece: {self.workpiece}, Quantity: {self.quantity}"
    
    @classmethod
    def calculate_production_start(cls, new_order, current_date):

        available_lines = { # assuming u can make 3 of each type at the same time
            "P5": 3,
            "P6": 3,
            "P7": 3,
            "P9": 3
        }
            
        time_to_produce = new_order.quantity * avg_prod_times[new_order.piece] * 1.5    # 1.5 to account for the time waiting for next one to finish
        time_to_produce = time_to_produce / available_lines[new_order.piece]
        start_date = new_order.due_date - math.ceil(time_to_produce)

        if start_date <= current_date:    # if start date is in the past or today
            start_date = current_date + 1  

        prod_plan = ProductionPlan(new_order.number, start_date, new_order.piece, new_order.quantity)
        
        print(f"Production plan: {prod_plan}")

        return prod_plan


class Prod_Quantities:
    def __init__(self, start_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity):
        self.start_date = start_date
        self.p5_quantity = p5_quantity
        self.p6_quantity = p6_quantity
        self.p7_quantity = p7_quantity
        self.p9_quantity = p9_quantity

avg_prod_times = {   # average production time for each piece type
        "P5": 2.83,
        "P6": 2.83,
        "P7": 1.83,
        "P9": 2.33
        }
        
