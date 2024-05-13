import csv
from UDP.udp_receiver import udp_receive
from delivery_plan import upload_delivery_plan
from new_order_processing import process_new_order
from production_plan import calculate_production_start, insert_production_plan
from purchasing_plan import calculate_purchasing_plan, insert_purchasing_plan


if __name__ == "__main__":   
    
    while True: 
        print("Waiting for new orders...")
        udp_receive()
        order_number = process_new_order() #parses xml file into database 
        upload_delivery_plan() #calculates and uploads delivery plan into database
    
        order_prod_plan = calculate_production_start(order_number) #calculates production start date
        print(f"Production plan: {order_prod_plan}")
        insert_production_plan(order_prod_plan)

        order_purchase_plan = calculate_purchasing_plan(order_prod_plan) #calculates purchasing plan based on production plan
        if order_purchase_plan is not None:
            print(f"Purchasing plan: {order_purchase_plan}")
            insert_purchasing_plan(order_purchase_plan)
        



