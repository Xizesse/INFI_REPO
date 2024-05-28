from UDP.udp_receiver import udp_receive
from classes.order import parse_new_orders
from classes.ProductionPlan import ProductionPlan
from classes.PurchasingPlan import make_purchasing_plan
from erp_db import connect_to_db, insert_new_orders, insert_production_plan, get_current_date, check_dispatched_orders, get_order, insert_costs
from erp_db import clear_all_tables

if __name__ == "__main__":   

    clear_all_tables() # Clear all tables in the database

    while True:
        try:         
            print("-------------------------------\n")
            
            #! UPDATE CURRENT DATE
            current_date = get_current_date()   # Get the current date from the database, if there's no date it's 0
            print(f"Current Date: {current_date}")

            #! UPDATE DISPATCHED ORDERS COSTS
            dispatched_orders_id = check_dispatched_orders(current_date) # Check if there are any orders that have been dispatched
            dispatched_orders_id = [order[0] for order in dispatched_orders_id]    #Transform the list of tuples into a list of integers
            print(f"Dispatched Orders: {dispatched_orders_id}")
            for order_id in dispatched_orders_id:
                print(f"Order {order_id} has been dispatched.")
                dispatched_order = get_order(order_id)
                order_total_cost, order_unit_cost = dispatched_order.calculate_costs() # Calculate the costs of the dispatched order    
                print(f"Total Cost: {order_total_cost}, Unit Cost: {order_unit_cost}")

            print("Waiting for new orders...")

            new_orders_file = udp_receive() # Receive new orders from the UDP server
            if new_orders_file is None:
                print("No new orders received.")
                continue
                
            # Parse new orders file
            new_orders = parse_new_orders(new_orders_file)  # Parse the new orders
            
            #!PROCESS NEW ORDERS
            inserted_orders = insert_new_orders(new_orders)
        
            for new_order in inserted_orders:

                order_prod_plan = ProductionPlan.calculate_production_start(new_order, current_date)
                insert_production_plan(order_prod_plan)

                make_purchasing_plan(order_prod_plan, current_date) #Calculates and inserts purchasing plan (raw orders and plan for each order)

                print("\n")
    
        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)

