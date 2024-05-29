from classes.raw_order import Raw_order, final_to_raw

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

def calculate_purchasing_plan(order_prod_plan, current_date):

    from erp_db import get_raw_order_leftovers, insert_raw_order_plan

    order_id = order_prod_plan.order_id
    start_date = order_prod_plan.start_date
    workpiece = order_prod_plan.workpiece
    needed_quantity = order_prod_plan.quantity

    available_time = start_date - current_date  

    workpiece = final_to_raw[workpiece]   # Know what raw material to order

    #!HANDLE LEFTOVERS
    
    raw_order_leftovers = get_raw_order_leftovers(workpiece)
    
    print(f"Raw Order Leftovers: {raw_order_leftovers}")
    
    if len(raw_order_leftovers) > 0:    # If we have leftovers
        for row in raw_order_leftovers:
                
            raw_order_id = int(row['raw_order_id'])
            leftover = int(row['leftover'])
            
            print(f"Raw Order ID: {raw_order_id} Leftover: {leftover}")
            used_raw_orders = []    # (raw_order_id, used_quantity)

            if leftover <= 0:
                continue
            if leftover >= needed_quantity:
                used_raw_orders.append((raw_order_id, needed_quantity))
                needed_quantity = 0
                break 
            else:
                used_raw_orders.append((raw_order_id, leftover))
                needed_quantity = needed_quantity - leftover
                continue
            
        print(f"Needed Quantity: {needed_quantity} Used Raw Orders: {used_raw_orders} Number of used raw orders: {len(used_raw_orders)}")

        # Update the used raw order plan in the database
        if len(used_raw_orders) > 0:    # If we used leftovers
            for raw_order_id, used_quantity in used_raw_orders:
                new_raw_order_plan = Raw_order_plan(order_id, raw_order_id, used_quantity)
                insert_raw_order_plan(new_raw_order_plan)

    #! NEW RAW ORDER
    #If we need extra orders pick the best raw order
    if needed_quantity > 0:
        best_raw_order = Raw_order.choose_raw_order(workpiece, needed_quantity, available_time)
    else:
        print("No purchase plan set.")
        return None
    
    if needed_quantity < best_raw_order.min_quantity:   #If we need less than the minimum
        order_quantity = best_raw_order.min_quantity    #Order the min
    else:
        order_quantity = needed_quantity    
        
    arrival_date = current_date + best_raw_order.delivery_days  # Calculate the arrival date of the order
    
    purchase_plan = PurchasingPlan(best_raw_order, arrival_date, order_quantity)
    
    print(f"Purchase Plan: {purchase_plan}")

    return purchase_plan, order_id, needed_quantity    # Needed quantity is not including what we have in leftovers

def make_purchasing_plan(order_prod_plan, current_date):

    from erp_db import insert_purchasing_plan, insert_raw_order_plan

    purch_plan_result = calculate_purchasing_plan(order_prod_plan, current_date)
    if purch_plan_result is not None:
        order_purchase_plan, order_id, used_quantity = purch_plan_result
    else:
        return

    raw_order_id = insert_purchasing_plan(order_purchase_plan)
    print(f"Purchase plan inserted")
    
    raw_order_plan = Raw_order_plan(order_id, raw_order_id, used_quantity)
    print(f"Raw Order Plan: {raw_order_plan}")
    insert_raw_order_plan(raw_order_plan)

    
