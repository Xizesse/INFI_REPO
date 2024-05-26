from UDP.udp_receiver import udp_receive
from classes.Order import Order, parse_new_orders
from classes.ProductionPlan import ProductionPlan
from classes.PurchasingPlan import calculate_purchasing_plan
from db import *


if __name__ == "__main__":   
    while True:
        try:         
            # Connect to the database
            connect_to_db() 
            
            print("Waiting for new orders...")

            new_orders_file = udp_receive() # Receive new orders from the UDP server
            new_orders = parse_new_orders(new_orders_file)  # Parse the new orders

            inserted_orders = insert_new_orders(new_orders)

            current_date = get_current_date()   # Get the current date from the database and if it is None, set it to 0
            if current_date is None:    
                current_date = 0
            print(f"Current Date: {current_date}")
        
            for new_order in inserted_orders:

                order_prod_plan = ProductionPlan.calculate_production_start(new_order, current_date)
                insert_production_plan(order_prod_plan)

                order_purchase_plan = calculate_purchasing_plan(order_prod_plan, current_date)
                insert_purchasing_plan(order_purchase_plan)
                
            print("-------------------------------\n")
            
            close_db_connection()
    
        except KeyboardInterrupt:
            print("Exiting...")
            close_db_connection()
            exit(0)

        except Exception as e:
            print(f"An error occurred: {e}")
            close_db_connection()
