from UDP.udp_receiver import udp_receive
from classes.Order import Order, parse_new_orders
from classes.ProductionPlan import ProductionPlan
from purchasing_plan import calculate_purchasing_plan
from db_interaction import *


if __name__ == "__main__":   
    
    while True: 
    
        connect_to_db() #connects to the database
        

        print("Waiting for new orders...")

        new_orders_file = udp_receive()

        new_orders = parse_new_orders(new_orders_file) #parses xml file and returns a list of orders 
        inserted_orders = insert_new_orders(new_orders)    #inserts orders into the database

        current_date = get_current_date() #gets the current date from the database
        if current_date is None:
            current_date = 0
        print(f"Current Date: {current_date}")
    
        for new_order in inserted_orders:    #for each order in the list of orders that was just received

            order_prod_plan = ProductionPlan.calculate_production_start(new_order, current_date) #calculates production start date for order
            insert_production_plan(order_prod_plan)

            order_purchase_plan = calculate_purchasing_plan(order_prod_plan, current_date) #calculates purchasing plan based on production plan  
            insert_purchasing_plan(order_purchase_plan)
            
        print("-------------------------------\n")
        close_db_connection()
        



