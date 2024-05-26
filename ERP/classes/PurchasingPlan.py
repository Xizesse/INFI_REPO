from classes.Raw_order import Raw_order, final_to_raw

class PurchasingPlan:
    def __init__(self, raw_order, arrival_date, quantity):
        self.raw_order = raw_order
        self.arrival_date = arrival_date
        self.quantity = quantity
        
    def __str__(self):
        return f"Arrival Date: {self.arrival_date}, Piece: {self.raw_order.piece}, Quantity: {self.quantity}"
    
    
class Raw_material_arrivals:
    def __init__(self, arrival_date, p1_quantity, p2_quantity):
        self.arrival_date = arrival_date
        self.p1_quantity = p1_quantity
        self.p2_quantity = p2_quantity


class Raw_order_plan: 
    def __init__(self, order_id, raw_order_id, used_quantity):
        self.order_id = order_id
        self.raw_order_id = raw_order_id
        self.used_quantity = used_quantity
    
    def __str__(self):
        return f"Order ID: {self.order_id}, Raw Order ID: {self.raw_order_id}, Used Quantity: {self.used_quantity}"

leftover_P1 = 0
leftover_P2 = 0

def calculate_purchasing_plan(order_prod_plan, current_date):

    from db import get_raw_order_leftovers
    #leftover_P1, leftover_P2 = get_raw_order_leftovers()
    
    global leftover_P1
    global leftover_P2

    order_id = order_prod_plan.order_id
    start_date = order_prod_plan.start_date
    workpiece = order_prod_plan.workpiece
    quantity = order_prod_plan.quantity

    available_time = start_date - current_date  

    # Calculate the best supplier for the order
    workpiece = final_to_raw[workpiece]

    #!HANDLE LEFTOVERS
    if workpiece == 'P1' and leftover_P1 > 0:   # If there is leftover P1 

        if leftover_P1 >= quantity: # If there is more leftover than needed
            leftover_P1 = leftover_P1 - quantity
            quantity = 0
        else:   # If there is less leftover than needed
            quantity = quantity - leftover_P1
            leftover_P1 = 0
    
    elif workpiece == 'P2' and leftover_P2 > 0:   # If there is leftover P2
        
        if leftover_P2 >= quantity: # If there is more leftover than needed
            leftover_P2 = leftover_P2 - quantity
            quantity = 0
        else:   # If there is less leftover than needed
            quantity = quantity - leftover_P2
            leftover_P2 = 0

    if quantity > 0:
        best_raw_order = Raw_order.choose_raw_order(workpiece, quantity, available_time)
    else:
        best_raw_order = None

    if best_raw_order is None:
        print("No purchase plan set.")
        return None
    
    if quantity < best_raw_order.min_quantity:
        
        if workpiece == 'P1':
            leftover_P1 += best_raw_order.min_quantity - quantity
        elif workpiece == 'P2':
            leftover_P2 += best_raw_order.min_quantity - quantity

        order_quantity = best_raw_order.min_quantity
    else:
        order_quantity = quantity
        
    arrival_date = current_date + best_raw_order.delivery_days
    
    purchase_plan = PurchasingPlan(best_raw_order, arrival_date, order_quantity)
    
    print(f"Purchase Plan: {purchase_plan}")

    return purchase_plan, order_id, quantity    # Quantity is the used

def make_purchasing_plan(order_prod_plan, current_date):

    from db import insert_purchasing_plan, insert_raw_order_plan

    order_purchase_plan, order_id, used_quantity = calculate_purchasing_plan(order_prod_plan, current_date)
    print(f"Order Purchase Plan: {order_purchase_plan} Order ID: {order_id} Used Quantity: {used_quantity}")

    raw_order_id = insert_purchasing_plan(order_purchase_plan)
    print(f"Raw Order ID: {raw_order_id}")

    raw_order_plan = Raw_order_plan(order_id, raw_order_id, used_quantity)
    print(f"Raw Order Plan: {raw_order_plan}")
    insert_raw_order_plan(raw_order_plan)
    print("Purchasing plan inserted.")

    
