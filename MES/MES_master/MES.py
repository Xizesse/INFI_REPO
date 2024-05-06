import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
from GUI import OPCUAClientGUI 
#from queue import Queue
import tkinter as tk
import time
import json
import os
from Line import Line
from Piece import Piece
from Warehouse import Warehouse

#TODO Barbara: DataBases para as warehouses (upper e lower)

#TODO Xico: Fazer o loop por machines
#TODO Xico: Par top bottom

#hmmm o loop vai ser tipo 
"""
    Check all machines
    If the machine can take the piece
    Process the piece
    """


#TODO : Display das orders

class MES:
    def __init__(self):
        #! CLIENTE OPC UA e GUI
        url = "opc.tcp://172.27.64.1:4840"
        self.client = Client(url)
        self.root = tk.Tk()
        self.app = OPCUAClientGUI(self, lambda: self.connect_to_server(self.app), lambda: self.disconnect_server(self.app))
        nodes = self.load_nodes_from_file('nodes.json')
        self.connected = False

        #!WAREHOUSES
        self.TopWarehouse = Warehouse(self.client)
        self.TopWarehouse.set_simulation_warehouse()
        self.BotWarehouse = Warehouse(self.client)
        self.BotWarehouse.set_simulation_warehouse()


        #! ORDERS
        #TODO Passar para database de orders / encher esta queue com as orders
        """ self.order_queue = Queue()
        for piece, quantity in self.orders_queu.items():
            if quantity > 0:
                for _ in range(quantity):
                    self.order_queue.put(piece) 
        self.app.set_queue(self.order_queue)"""

        #! LINES AND MACHINES
        self.lines_machines = {
    1: Line(self.client, nodes, "Line1", 1, {1, 2, 3}, {1, 2, 3}),
    2: Line(self.client, nodes, "Line2", 2, {1, 2, 3}, {1, 2, 3}),
    3: Line(self.client, nodes, "Line3", 3, {1, 2, 3}, {1, 2, 3}),
    4: Line(self.client, nodes, "Line4", 4, {1, 4, 5}, {1, 4, 6}),
    5: Line(self.client, nodes, "Line5", 5, {1, 4, 5}, {1, 4, 6}),
    6: Line(self.client, nodes, "Line6", 6, {1, 4, 5}, {1, 4, 6})
}
        #! TRANSFORMATIONS
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
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!OPC UA Client Functions

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
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1MES Functions for logic 
    def find_next_transformation(self, start_type, final_type): 
        #Returns the next transformation to be done to get to the final type
        if start_type == final_type:
            print("Piece is already at the final type.")
            return None
        path = self.transformation_paths.get((start_type, final_type))
        if not path:
            print("Transformation is not possible.")
            return None
        current_type = start_type
        for next_type in path[1:]:  
            
            for (start_piece, tool), transformation in self.transformations.items():
                if start_piece == current_type and transformation['result'] == next_type:
                    return tool  
        print("Error. No tool found for the transformation.")
        return None

    def check_machine_can_process(self, line, position, piece):
        current_type = piece.type
        final_type = piece.final_type
        if (position == 'top' and line.isTopBusy()) or (position == 'bot' and line.isBotBusy()):
            print(f"{position} machine on line {line.id} is currently busy.")
            return False

        next_tool = self.find_next_transformation(current_type, final_type)
        if next_tool is None:
            print(f"No next tool found for transformation from {current_type} to {final_type}.")
            return False

        if line.has_tool(next_tool, position):
            print(f"{position} machine on line {line.id} can process the piece with tool {next_tool}.")
            return True
        else:
            print(f"{position} machine on line {line.id} does not have the required tool {next_tool}.")
            return False

    def update_machine(self, line, position, piece):
        if not self.check_machine_can_process(line, position, piece):
            return
        elif position == 'top':
            #take the piece out of the warehouse
            line.setTopBusy(True)
            piece.machinetop = True
            piece.tooltop = self.find_next_transformation(piece.type, piece.final_type)
            line.load_piece(piece)
        elif position == 'bot':
            #take the piece out of the warehouse
            line.setBotBusy(True)
            piece.machinebot = True
            piece.toolbot = self.find_next_transformation(piece.type, piece.final_type)
            line.load_piece(piece)

    def update_all_machines(self):
        #first update all bottom machines
        for _, line in self.lines_machines.items():
            self.update_machine(line, 'bot', self.BotWarehouse.get_piece_queue())
        #then update all top machines
        for _, line in self.lines_machines.items():
            self.update_machine(line, 'top', self.TopWarehouse.get_piece_queue())
        

#######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! MES Loop !!!!!!!!!!!!!!
    def MES_loop(self):
        global connected
        global last_day
        print("Starting day: ", self.app.day_count)
        self.app.update_orders_display()
        if self.connected and self.app.day_count > 0:
            #update_client()

            try:
                if self.app.day_count == 1 and last_day != self.app.day_count:
                    print("Rise and shine, it's Day 1")
                    
                    last_day = self.app.day_count

                if self.app.day_count == 2 and last_day != self.app.day_count:
                    print("Good moning, it's Day 2")
                        
                    last_day = self.app.day_count
                
            except Exception as e:
                    messagebox.showerror("Set Value Error", str(e))
            

        self.root.after(1000, self.MES_loop)


#######################################################################################################
if __name__ == "__main__":
    #url = "opc.tcp://localhost:4840"

    mes = MES()
   
    last_day = 0
    mes.root.after(1, mes.MES_loop)
    mes.root.mainloop()


