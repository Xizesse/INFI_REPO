import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
from PiecesGUI import PiecesGUI 
from StatisticsGUI import ShopFloorStatisticsWindow
#from queue import Queue
import tkinter as tk
import time 
import json
import os
from Line import Line
from Piece import Piece
from Warehouse import Warehouse
import DB

#!TODO

#Small Things
#TODO modo manual e automatico para a contagem de dias
#TODO IDs 



class MES:
    def __init__(self):
        #! CLIENTE OPC UA e GUI
        url = "opc.tcp://172.27.64.1:4840"
        self.client = Client(url)
        self.root = tk.Tk() 
        self.app = PiecesGUI(self, lambda: self.connect_to_server(self.app), lambda: self.disconnect_server(self.app)) 
        self.stats = ShopFloorStatisticsWindow(self.root)
        nodes = self.load_nodes_from_file('nodes.json')
        self.connected = False
    
        #! PURCHASES - Array of (type)
        self.purchases = []

        #! PRODUCTION ORDERS - Array of (final_type) - Working :)
        self.production_orders = []
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        

        #! DELIVERIES - Array of (orders) 
        self.deliveries = []
        
        #!WAREHOUSES
        self.TopWarehouse = Warehouse(self.client)
        self.BotWarehouse = Warehouse(self.client)
        #O warehouse de cima começa com 20 peças 1
        for _ in range(20):
            piece = Piece(self.client, 0, 1, 0, 0, 0, False, False, 0, 0)
            self.TopWarehouse.put_piece_queue(piece)
        piece = Piece(self.client, 999, 1, 1, 0, 0, False, False, 0, 0)
        self.TopWarehouse.put_piece_queue(piece)
        piece = Piece(self.client, 998, 1, 1, 0, 0, False, False, 0, 0)
        piece.on_the_floor = True
        self.TopWarehouse.put_piece_queue(piece)
        #self.TopWarehouse.set_simulation_warehouse()
        #self.BotWarehouse.set_simulation_warehouse()
        #self.SFS = Warehouse(self.client)

        self.IDcount = 1

        #! LINES AND MACHINES
        self.lines_machines = {
            1: Line(self.client, nodes, "Line1", 1, {1, 2, 3}, {1, 2, 3}),
            #2: Line(self.client, nodes, "Line2", 2, {1, 2, 3}, {1, 2, 3}),
            #3: Line(self.client, nodes, "Line3", 3, {1, 2, 3}, {1, 2, 3}),
            #4: Line(self.client, nodes, "Line4", 4, {1, 4, 5}, {1, 4, 6}),
            #5: Line(self.client, nodes, "Line5", 5, {1, 4, 5}, {1, 4, 6}),
            #6: Line(self.client, nodes, "Line6", 6, {1, 4, 5}, {1, 4, 6})
        }
        self.ReverseConveyor = Line(self.client, nodes, "ReverseConveyor", 0, {}, {})

        #! LOADING DOCKS
        self.loading_docks = {
            1: Line(self.client, nodes, "LoadingDock1", 11, {}, {}),
            2: Line(self.client, nodes, "LoadingDock2", 12, {}, {}),
            3: Line(self.client, nodes, "LoadingDock3", 13, {}, {}),
            4: Line(self.client, nodes, "LoadingDock4", 14, {}, {})
        }

        #! UNLOADING DOCKS
        self.unloading_docks = {
            1: Line(self.client, nodes, "UnloadingDock1", 21, {0}, {0}),
            2: Line(self.client, nodes, "UnloadingDock2", 22, {0}, {0}),
            3: Line(self.client, nodes, "UnloadingDock3", 23, {0}, {0}),
            4: Line(self.client, nodes, "UnloadingDock4", 24, {0}, {0})
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

        print("\nMES initialized\n\n")

#######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! MES Loop !!!!!!!!!!!!!!
    def MES_loop(self):
        global last_day
        #print("Starting day: ", self.app.day_count)
        self.app.update_orders_display()
        

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   Beggining of the day actions !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
        if last_day != self.app.day_count:
            print("New day, good morning")

            

            #! Get the prod sched for the day
            daily_prod = DB.get_production_queue(self.app.day_count)
            self.production_orders += daily_prod
            #! Get the purchases for the day
            #self.purchases = DB.get_purchases(self.app.day_count)
            #! Get the deliveries for the day
            #self.deliveries = DB.get_deliveries(self.app.day_count)
            #if self.connected:
                #pieceTest = Piece(self.client, 999, 1, 2, 0, 0, False, True, 0, 1)
                #self.lines_machines[1].load_piece(pieceTest)
            
            last_day = self.app.day_count

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Permanent actions !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

        if self.connected:
        
            #! Purchase actions
            #TODO
            #self.update_loading_docks()

            #!check if there are pieces in the loading dock that can be put in the top warehouse
            #TODO 
            #for dock in self.loading_docks: ...
                #Piece = unload ...
                #add to top warehouse
            
            #!Turn self.production_orders into pieces in the top warehouse
            self.update_pieces()
            #!update all machines (Simpler algorith : Bottom machines then top machines)
            self.update_all_machines()
            #!Get the piece in each line output
            #TODO
            self.remove_all_output_piece()
            #!Send back up the unfinished pieces - Xico
            #self.send_unfinished_back_up()
        

            #! Delivery actions - Barbara
            #TODO
            
        self.root.after(1000, self.MES_loop)

    #######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!OPC UA Client Functions

    def connect_to_server(self, gui):


        if self.connected:
            return
        try:
            # OPC UA connect logic here
            self.client.connect()
            gui.status_label.config(text="Connected", fg="green")
            gui.start_blinking()
            self.connected = True
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
        
    def load_nodes_from_file(self, filename):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        full_path = os.path.join(dir_path, filename)
        with open(full_path, 'r') as file:
            data = json.load(file)
        return data

    def disconnect_server(self, gui):
        if not self.connected:
            return
        try:
            # OPC UA disconnect logic here
            self.client.disconnect()
            gui.status_label.config(text="Disconnected", fg="red")
            gui.stop_blinking()
            self.connected = False
        except Exception as e:
            messagebox.showerror("Disconnection Error", str(e))
        
    #######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!MES Functions for logic 
    def find_next_transformation(self, start_type, final_type): 
        #Returns the next transformation to be done to get to the final type
        if start_type == final_type:
            return None
        path = self.transformation_paths.get((start_type, final_type))
        if not path:
            return None
        current_type = start_type
        for next_type in path[1:]:  
            
            for (start_piece, tool), transformation in self.transformations.items():
                if start_piece == current_type and transformation['result'] == next_type:
                    return tool  
        return None

    def check_machine_can_process(self, line, position, piece):
        current_type = piece.type
        final_type = piece.final_type
        if (position == 'top' and line.isTopBusy()) or (position == 'bot' and line.isBotBusy()):
            return False

        next_tool = self.find_next_transformation(current_type, final_type)
        if next_tool is None:
            return False

        if line.has_tool(next_tool, position):
            return True
        else:
            print(f"{position} machine on line {line.id} does not have the required tool {next_tool}.")
            return False

    def get_raw_material(self, final):
        if final in [1, 3, 4, 5, 6, 7]:
            return 1
        elif final in [9]:
            return 2
        else :
            return None
        
    def update_machine(self, line, position, piece):
        if not self.check_machine_can_process(line, position, piece):
            return
        elif position == 'top':
            #take the piece out of the warehouse
            line.setTopBusy(True)
            piece.line_id = line.id
            piece.machinetop = True
            piece.tooltop = self.find_next_transformation(piece.type, piece.final_type)
            line.load_piece(piece)
        elif position == 'bot':
            #take the piece out of the warehouse
            line.setBotBusy(True)
            piece.line_id = line.id
            piece.machinebot = True
            piece.toolbot = self.find_next_transformation(piece.type, piece.final_type)
            #remove the piece from the warehouse
            #piece.toolbot = self.find_next_transformation(piece.type, piece.final_type)
            line.load_piece(piece)

    def update_all_machines(self):
        #first update all bottom machines
        print("Updating all machines.")
        for _, line in self.lines_machines.items():
            if line.is_Occupied():
                print(f"Line {line.id} is occupied.")
                continue
            else:
                print(f"Line {line.id} is not occupied.")
            for piece in list(self.TopWarehouse.pieces.queue):
                if piece.machinetop == False and piece.machinebot == False:
                    self.update_machine(line, 'bot', piece)

        #then update all top machines
        for _, line in self.lines_machines.items():
            if line.is_Occupied():
                continue
            for piece in list(self.TopWarehouse.pieces.queue):
                if piece.machinetop == False and piece.machinebot == False:
                    self.update_machine(line, 'top', piece)

    def update_pieces(self):
        i = 0
        while i < len(self.production_orders):
            order = self.production_orders[i]
            processed = False
            for piece in list(self.TopWarehouse.pieces.queue):
                if self.transformation_paths.get((piece.type, order)) and piece.id == 0:
                    print(f"Creating piece for {piece.type}->{piece.final_type}")
                    piece.final_type = order
                    piece.order_id = 27
                    piece.id = self.IDcount
                    self.IDcount += 1
                    piece.delivery_day = self.app.day_count + 5
                    processed = True
                    break
            if processed:
                self.production_orders.remove(order)
            else :
                i += 1

    def remove_all_output_piece(self):
        for _, line in self.lines_machines.items():
            self.remove_output_piece(line)

    def remove_output_piece(self, line):
        removed_piece = line.remove_output_piece()
        ##remove from the warehouse a piece with the same values
        if removed_piece:
            print("Removing piece from the line output.")
            print(f"Piece type: {removed_piece.type}, machinetop: {removed_piece.machinetop}, machinebot: {removed_piece.machinebot}, tooltop: {removed_piece.tooltop}, toolbot: {removed_piece.toolbot}.")
            for similar_piece in list(self.TopWarehouse.pieces.queue):
                #hmm maneira horrivel de fazer isto
                if similar_piece.line_id == line.id:
                    if similar_piece.on_the_floor:
                        if similar_piece.tooltop == removed_piece.tooltop and similar_piece.toolbot == removed_piece.toolbot:
                            self.TopWarehouse.pieces.queue.remove(similar_piece)
                            updated_type = self.find_next_transformation(removed_piece.type, removed_piece.final_type)
                            new_piece = Piece(self.client, 27, updated_type, removed_piece.final_type, 0, 0, False, False, 0, 0)
        
                            self.BotWarehouse.put_piece_queue()
                            break
            #add the piece to the bot warehouse, with the type of the next transformation
        

    def send_unfinished_back_up(self):
        #Send back up the unfinished pieces
        #for piece in list(self.BotWarehouse.pieces.queue):
            #if piece.type != piece.final_type:
            #    print("Sending unfinished piece back up.")
        return



    def update_loading_docks(self):
        # Iterate over each dock using items() to get both key (dock id) and value (dock object)
        for dock_id, dock in self.loading_docks.items():
            if not dock.is_Occupied():
                # Check for which dock it is and load the appropriate piece type
                if dock_id in [1, 2]:  # For docks 1 and 2, we look for a piece of type 1
                    for piece in self.purchases:
                        if piece == 1:
                            #dock.load_piece(piece)  # Assuming this function sets the dock's status to occupied
                            break  # Stop searching once a piece is loaded
                elif dock_id in [3, 4]:  # For docks 3 and 4, we look for a piece of type 2
                    for piece in self.purchases:
                        if piece == 2:
                            #dock.load_piece(piece) 
                            break  # Stop searching once a piece is loaded
                

                

               
               
#######################################################################################################
if __name__ == "__main__":
    #url = "opc.tcp://localhost:4840"

    mes = MES()
   
    last_day = 0
    mes.root.after(1, mes.MES_loop)
    mes.root.mainloop()
