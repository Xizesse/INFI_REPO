from classes.Raw_order import *
from db_interaction import *


leftover_P1 = 0
leftover_P2 = 0
    
def calculate_purchasing_plan(order_prod_plan, current_date):

    order_id = order_prod_plan.order_id
    start_date = order_prod_plan.start_date
    workpiece = order_prod_plan.workpiece
    quantity = order_prod_plan.quantity

    available_time = start_date - current_date  

    # Calculate the best supplier for the order
    workpiece = final_to_raw[workpiece]

    global leftover_P1
    global leftover_P2

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
        best_raw_order = Raw_order.choose_raw_order(raw_orders, workpiece, quantity, available_time)
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

        quantity = best_raw_order.min_quantity
        
    arrival_date = current_date + best_raw_order.delivery_days
    purchase_plan = (arrival_date, best_raw_order.supplier, workpiece, quantity)  

    print(f"Purchasing plan: {purchase_plan} with leftover P1: {leftover_P1} + P2: {leftover_P2}")
    return purchase_plan
