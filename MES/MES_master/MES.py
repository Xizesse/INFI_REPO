import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
from GUI import OPCUAClientGUI 
from queue import Queue
import tkinter as tk
import time
import json
import os
from Line import Line
from Piece import Piece

#TODO Barbara: DataBases para as warehouses (upper e lower)

#TODO Xico: Fazer o loop por machines
#TODO Xico: Par top bottom

#TODO : Display das orders

class MES:
    def __init__(self):
        url = "opc.tcp://172.27.64.1:4840"
        self.client = Client(url)
        self.root = tk.Tk()
        self.app = OPCUAClientGUI(self.root, lambda: self.connect_to_server(self.app), lambda: self.disconnect_server(self.app))
        nodes = self.load_nodes_from_file('nodes.json')

        self.lines_machines = {
            1: {'top': 1, 'bot': 2, 'line': Line(self.client, nodes, "Line1", 1)},
            2: {'top': 1, 'bot': 2, 'line': Line(self.client, nodes, "Line2", 2)},
            3: {'top': 1, 'bot': 2, 'line': Line(self.client, nodes, "Line3", 3)},
            4: {'top': 3, 'bot': 4, 'line': Line(self.client, nodes, "Line4", 4)},
            5: {'top': 3, 'bot': 4, 'line': Line(self.client, nodes, "Line5", 5)},
            6: {'top': 3, 'bot': 4, 'line': Line(self.client, nodes, "Line6", 6)}
        }

        self.connected = False
        #TODO Passar para database de warehouse
        self.upperWarehouse = {
                1: 20,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                7: 0,
                8: 0,
                9: 0
            }
        #TODO Passar para database de warehouse
        self.bottomWarehouse = {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                7: 0,
                8: 0,
                9: 0
            }
        #TODO Passar para database de orders / encher esta queue com as orders
        self.orders = {
            3: 1,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            9: 0
        }


        self.order_queue = Queue()
        for piece, quantity in self.orders.items():
            if quantity > 0:
                for _ in range(quantity):
                    self.order_queue.put(piece)
        #Print this queue
        #print(self.order_queue.queue)

        self.app.set_queue(self.order_queue)

        self.transformations = {
        #    (start_piece, tool): {'result': final_piece}
            (1, 1): {'result': 3},
            (3, 2): {'result': 4},
            (3, 3): {'result': 4},
            (4, 2): {'result': 6},
            (4, 3): {'result': 7},
            (4, 4): {'result': 5},
            (2, 3): {'result': 7},
            (8, 1): {'result': 8},
            (8, 6): {'result': 7},
            (8, 5): {'result': 9},
        }
        #Tods os paths possíveis, em pares inicial e final
        self.transformation_paths = {
            (1, 3): [1, 3],
            (1, 4): [1, 3, 4],
            (1, 5): [1, 3, 4, 5],
            (1, 6): [1, 3, 4, 6],
            (1, 7): [1, 3, 4, 7],
            (3, 4): [3, 4],
            (3, 5): [3, 4, 5],
            (3, 6): [3, 4, 6],
            (3, 7): [3, 4, 7],
            (4, 5): [4, 5],
            (4, 6): [4, 6],
            (4, 7): [4, 7],
            (2, 8): [2, 8],
            (2, 7): [2, 8, 7],
            (2, 9): [2, 8, 9],
            (8, 7): [8, 7],
            (8, 9): [8, 9]
        }

        self.machines = {
            1: {1, 2, 3},
            2: {1, 2, 3},
            3: {1, 4, 5},
            4: {1, 4, 6},
        }


    #######################################################################################################

    def connect_to_server(self, gui):
        global connected

        if connected:
            return
        try:
            # OPC UA connect logic here
            self.client.connect()
            gui.status_label.config(text="Connected", fg="green")
            gui.start_blinking()
            connected = True
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
        
    def load_nodes_from_file(self, filename):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        full_path = os.path.join(dir_path, filename)
        with open(full_path, 'r') as file:
            data = json.load(file)
        return data

    def disconnect_server(self, gui):
        global connected
        if not connected:
            return
        try:
            # OPC UA disconnect logic here
            self.client.disconnect()
            gui.status_label.config(text="Disconnected", fg="red")
            gui.stop_blinking()
            connected = False
        except Exception as e:
            messagebox.showerror("Disconnection Error", str(e))
        
    #######################################################################################################



    def find_machine(self, start_type, final_type):
        #Returns the line, machine and tool needed for a transformation
        path = self.transformation_paths.get((start_type, final_type))
        if path and len(path) > 1:  
            current_type = start_type
            next_type = path[1]  
            # Find the transformation
            for (start_piece, tool), transformation in self.transformations.items():
                if start_piece == current_type and transformation['result'] == next_type:
                    for machine_id, machine_info in self.machines.items():
                        if tool in machine_info:
                            # Check if it is top or bottom machine
                            for line_id, machine_info in self.lines_machines.items():
                                line = machine_info['line']
                                if True: #!not line.is_Occupied(): 
                                    if machine_id == machine_info['top']:
                                        return line, 'top', tool
                                    elif machine_id == machine_info['bot']:
                                        return line, 'bot', tool
        return None, None, None
    

    def check_warehouse_top(self):
        # Check if there is a piece in the top warehouse that can be processed
        return 
    
    def check_warehouse_bottom(self):
        # Check if there is a piece in the bottom warehouse that can be processed

        #check if there is an order to release
        return

    def check_machine_can_process(line, position, warehouse):
        # Check if the machine can process a piece
        #returns the piece and the tool needed for the transformation if available
        if position == 'top':
            if line.isTopBusy():
                print("Top machine is busy.")
                return False
            else : 
                #check if there is a piece in the top warehouse that can be processed
                for piece in self.upperWarehouse:
                    #first I need to see what machines can turn this piece into a final piece
                    for machine in self.machines:
                        if piece in self.machines[machine]:
                            #then I need to see it line of the machine is free
                            #if so, I load the piece into the line and return
                            pass
                
        if position == 'bot':
            if line.isBotBusy():
                print("Bottom machine is busy.")
                return False
        

                
                

    def find_transformation_for_machine(self, piece_type, machine_position):
        # Mockup logic to find a suitable transformation for a given piece type and machine position
        # This function should return the piece and the tool needed for the transformation if available
        for (start_piece, tool), transformation in self.transformations.items():
            if start_piece == piece_type:  # Check if transformation starts with the piece type
                # Here, you might also want to check if the tool is suitable for the machine_position
                return start_piece, tool
        return None
                    

    def check_warehouse_bottom(self):
        for piece in self.bottomWarehouse:
            #first I need to see what machines can turn this piece into a final piece
            for machine in self.machines:
                if piece in self.machines[machine]:
                    #then I need to see it line of the machine is free
                    #if so, I load the piece into the line and return
                    pass

            #then I need to see it line of the machine is free
            #if so, I load the piece into the line and return

    def MES_loop(self):
        global connected
        global last_day
        while(True):
            print(self.app.day_count)
            if connected and self.app.day_count > 0:
                #update_client()
                try:

                    """if not order_queue.empty():
                        next_order = order_queue.queue[0]
                        print("Next process: ", next_order)
                        process_order(next_order)
                    else :
                        print("No orders in queue.")
                    """
                    if self.app.day_count == 1 and last_day != self.app.day_count:
                        print("Rise and shine, it's Day 1")
                    
                        last_day = self.app.day_count

                            
                    if self.app.day_count == 2 and last_day != self.app.day_count:
                        print("Good moning, it's Day 2")
                        


                        last_day = self.app.day_count
                
                
                except Exception as e:
                    messagebox.showerror("Set Value Error", str(e))
                self.app.update_queue()

        #root.after(1000, self.MES_loop)




#######################################################################################################
if __name__ == "__main__":
    #url = "opc.tcp://localhost:4840"

    mes = MES()
   
    last_day = 0
    mes.root.after(1, mes.MES_loop)
    mes.root.mainloop()


