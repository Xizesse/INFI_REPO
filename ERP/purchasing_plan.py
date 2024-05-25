from classes.Raw_order import *

leftover_P1 = 0
leftover_P2 = 0

def calculate_purchasing_plan(order_prod_plan, current_date):

    order_id, start_date, workpiece, quantity = order_prod_plan

    available_time = start_date - current_date  

    # Calculate the best supplier for the order
    workpiece = final_to_raw[workpiece]

    global leftover_P1
    global leftover_P2

    if workpiece == 'P1':
        quantity = quantity - leftover_P1
    elif workpiece == 'P2':
        quantity = quantity - leftover_P2

    leftover_P1 = 0
    leftover_P2 = 0

    best_raw_order = Raw_order.choose_raw_order(raw_orders, workpiece, quantity, available_time)

    if quantity < best_raw_order.min_quantity:
        
        if workpiece == 'P1':
            leftover_P1 += best_raw_order.min_quantity - quantity
        elif workpiece == 'P2':
            leftover_P2 += best_raw_order.min_quantity - quantity

        quantity = best_raw_order.min_quantity

    if best_raw_order is None:
        print("No suitable raw order found.")
        return None
    
    arrival_date = current_date + best_raw_order.delivery_days
    purchase_plan = (arrival_date, best_raw_order.supplier, workpiece, quantity)  

    print(f"Purchasing plan: {purchase_plan}")
    return purchase_plan


def insert_purchasing_plan(conn, purchase_plan):

    if purchase_plan is None:
        return
    
    arrival_date, supplier, workpiece, quantity = purchase_plan

    cur = conn.cursor()

    # Create the production_plan table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS infi.purchasing_plan (
            arrival_date INTEGER PRIMARY KEY,
            p1_quantity INTEGER,
            p2_quantity INTEGER
        );
    """)

    # Initialize quantities for each piece type
    quantities = {
        'P1': 0,
        'P2': 0
    }

    quantities[workpiece] = quantity

    cur.execute("""
        INSERT INTO infi.purchasing_plan (arrival_date, p1_quantity, p2_quantity) 
        VALUES (%s, %s, %s)
        ON CONFLICT (arrival_date) DO UPDATE
        SET p1_quantity = purchasing_plan.p1_quantity + excluded.p1_quantity,
            p2_quantity = purchasing_plan.p2_quantity + excluded.p2_quantity;
        """, (arrival_date, quantities['P1'], quantities['P2']))

    # Commit changes
    conn.commit()

    #print("Purchasing schedule inserted into purchasing_plan table.")
