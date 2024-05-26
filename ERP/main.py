from UDP.udp_receiver import udp_receive
from classes.order import parse_new_orders
from classes.ProductionPlan import ProductionPlan
from classes.PurchasingPlan import make_purchasing_plan
from db import connect_to_db, close_db_connection, insert_new_orders, insert_production_plan, get_current_date, check_dispatched_orders, get_order, insert_costs


if __name__ == "__main__":   
    while True:
        try:         
            print("-------------------------------\n")
            # Connect to the database
            connect_to_db() 
            
            #! UPDATE CURRENT DATE
            current_date = get_current_date()   # Get the current date from the database and if it is None, set it to 0
            if current_date is None:    
                current_date = 0
            print(f"Current Date: {current_date}")

            #!UPDATE DISPATCHED ORDERS COSTS
            dispatched_orders_id = check_dispatched_orders(current_date) # Check if there are any orders that have been dispatched
            print(f"Dispatched Orders: {dispatched_orders_id}")
            for order_id in dispatched_orders_id:
                print(f"Order {order_id} has been dispatched.")
                dispatched_order = get_order(order_id)
                order_total_cost, order_unit_cost = dispatched_order.calculate_costs() # Calculate the costs of the dispatched order
                insert_costs(order_id, order_total_cost, order_unit_cost) # Insert the costs into the database

            close_db_connection() # Close the database connection
            
            connect_to_db() # Connect to the database

            print("Waiting for new orders...")

            new_orders_file = udp_receive() # Receive new orders from the UDP server
            if new_orders_file is None:
                print("No new orders received.")
                continue

            new_orders = parse_new_orders(new_orders_file)  # Parse the new orders

            inserted_orders = insert_new_orders(new_orders)
        
            for new_order in inserted_orders:

                order_prod_plan = ProductionPlan.calculate_production_start(new_order, current_date)
                insert_production_plan(order_prod_plan)

                make_purchasing_plan(order_prod_plan, current_date) #Calculates and inserts purchasing plan (raw orders and plan for each order)

                print("\n")
            close_db_connection()
    
        except KeyboardInterrupt:
            print("Exiting...")
            close_db_connection()
            exit(0)

        except Exception as e:
            print(f"An error occurred: {e}")
            close_db_connection()
