import csv
from UDP.udp_receiver import udp_receive
from delivery_plan import upload_delivery_plan

order_backlog = []


if __name__ == "__main__":

    udp_receive()
    upload_delivery_plan()
    
    #while True:
        
        






