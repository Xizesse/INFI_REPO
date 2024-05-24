from UDP.udp_receiver import udp_receive
from new_orders_processing import parse_new_orders, insert_new_orders
from production_plan import calculate_production_start, insert_production_plan
from purchasing_plan import calculate_purchasing_plan, insert_purchasing_plan
from db_config import connect_to_db, close_db_connection, get_current_date
from classes.order import Order


if __name__ == "__main__":   
    
    while True: 
    
        db_connection = connect_to_db() #connects to the database

        print("Waiting for new orders...")

        new_orders_file = udp_receive()

        new_orders = parse_new_orders(new_orders_file) #parses xml file and returns a list of orders 
        inserted_orders = insert_new_orders(db_connection, new_orders)    #inserts orders into the database

        current_date = get_current_date(db_connection) #gets the current date from the database
    
        for new_order in inserted_orders:    #for each order in the list of orders that was just received

            order_prod_plan = calculate_production_start(new_order, current_date) #calculates production start date for order
            try :
                insert_production_plan(db_connection, order_prod_plan)
            except Exception as e:
                print("Error:", e)
                continue

            order_purchase_plan = calculate_purchasing_plan(order_prod_plan, current_date) #calculates purchasing plan based on production plan  

            try:
                insert_purchasing_plan(db_connection, order_purchase_plan)
            except Exception as e:
                print("Error:", e)
                continue
            
        print("-------------------------------\n")
        close_db_connection(db_connection)
        



