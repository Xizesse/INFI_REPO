import csv
from UDP.udp_receiver import udp_receive
from delivery_plan import upload_delivery_plan
from new_order_processing import process_new_order


if __name__ == "__main__":   
    
    while True: 
        udp_receive()
        process_new_order() #parses xml file into database 
        upload_delivery_plan() #calculates and uploads delivery plan into database
    
        
        
        



