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
from warehouse import Warehouse
import DB
from Orders import Order
from Piece_to_produce import Piece_to_produce

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
        nodes = self.load_nodes_from_file('nodes.json')
        self.connected = False
    
        #! PURCHASES - Array of (type)
        self.purchases = []

        #! PRODUCTION ORDERS - Array of (final_type) - Working :)
        self.production_orders = []

        test_piece5 = Piece_to_produce(500, 5, 10) 
        test_piece9 = Piece_to_produce(501, 9, 10)

        #add 5 pieces of type 5 to the production orders and 3 pieces of type 9
        for _ in range(5):
            self.production_orders.append(test_piece5)
        for _ in range(3):
            self.production_orders.append(test_piece9)


        #! DELIVERIES - Array of (orders) 
        self.deliveries = []
        
        #!WAREHOUSES
        self.TopWarehouse = Warehouse(self.client)
        self.BotWarehouse = Warehouse(self.client)
        #O warehouse de cima começa com 20 peças 1
        for _ in range(20):
            piece = Piece(self.client, 0, 1, 0, 0, 0, False, False, 0, 0)
            self.TopWarehouse.put_piece_queue(piece)
        piece = Piece(self.client, 0, 2, 0, 0, 0, False, False, 0, 0)
        self.TopWarehouse.put_piece_queue(piece)

        #for _ in range(8):
         #   piece = Piece(self.client, 0, 9, 0, 0, 0, False, False, 0, 0)
          #  self.BotWarehouse.put_piece_queue(piece)

        piece = Piece(self.client, 999, 1, 1, 0, 0, False, False, 0, 0)
        self.TopWarehouse.put_piece_queue(piece)
        piece = Piece(self.client, 998, 1, 1, 0, 0, False, False, 0, 0)
        piece.on_the_floor = True
        self.TopWarehouse.put_piece_queue(piece)
        


        #self.TopWarehouse.set_simulation_warehouse()
        #self.BotWarehouse.set_simulation_warehouse()
        #self.SFS = Warehouse(self.client)

        self.IDcount = 1

        #EXEMPLO: O warehouse de baixo começa com 4 peças 5
        for _ in range(20):
            piece = Piece(self.client, 0, 5, 5, 5, 8, False, False, 0, 0)
            self.BotWarehouse.put_piece_queue(piece)

         #! LINES AND MACHINES
        self.lines_machines = {
            1: Line(self.client, nodes, "Line1", 1, {1, 2, 3}, {1, 2, 3}),
            2: Line(self.client, nodes, "Line2", 2, {1, 2, 3}, {1, 2, 3}),
            3: Line(self.client, nodes, "Line3", 3, {1, 2, 3}, {1, 2, 3}),
            4: Line(self.client, nodes, "Line4", 4, {1, 4, 5}, {1, 4, 6}),
            5: Line(self.client, nodes, "Line5", 5, {1, 4, 5}, {1, 4, 6}),
            6: Line(self.client, nodes, "Line6", 6, {1, 4, 5}, {1, 4, 6})
        }

        #! LOADING DOCKS
        self.loading_docks = {
            1: Line(self.client, nodes, "LoadingDock1", 7, {}, {}),
            2: Line(self.client, nodes, "LoadingDock2", 8, {}, {}),
            3: Line(self.client, nodes, "LoadingDock3", 9, {}, {}),
            4: Line(self.client, nodes, "LoadingDock4", 10, {}, {})
        }

        #! UNLOADING DOCKS
        self.unloading_docks = {
            1: Line(self.client, nodes, "UnloadingDock1", 11, {}, {}),
            2: Line(self.client, nodes, "UnloadingDock2", 12, {}, {}),
            3: Line(self.client, nodes, "UnloadingDock3", 13, {}, {}),
            4: Line(self.client, nodes, "UnloadingDock4", 14, {}, {})
        }

        self.ReverseConveyor = Line(self.client, nodes, "ReverseConveyor", 15, {}, {})

        self.stats = ShopFloorStatisticsWindow(self.root, self)


        #! PURCHASES - Array of (type)
        self.purchases = []
        self.purchases.append(1)
        self.purchases.append(1)
        self.purchases.append(1)
        self.purchases.append(2)
        self.purchases.append(2)
        self.purchases.append(2)

        #! PRODUCTION ORDERS - Array of (final_type) - Working :)
        self.production_orders = []
        self.production_orders.append(5)
        self.production_orders.append(9)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)
        self.production_orders.append(5)

        #! DELIVERIES - Array of (orders) 
        self.deliveries = []
        self.deliveries.append(Order(quantity=8, final_type=9, order_id=27, delivery_day=1, status="Ready", dispatch_conveyor=""))
        
        #!WAREHOUSES
        self.TopWarehouse = Warehouse(self.client)
        self.BotWarehouse = Warehouse(self.client)
        #O warehouse de cima começa com 20 peças 1
        for _ in range(20):
            piece = Piece(self.client, 0, 1, 0, 0, 0, False, False, 0, 0)
            self.TopWarehouse.put_piece_queue(piece)

        for _ in range(8):
            piece = Piece(self.client, 0, 9, 9, 0, 0, False, False, 0, 0)
            self.BotWarehouse.put_piece_queue(piece)

        #piece = Piece(self.client, 999, 1, 1, 0, 0, False, False, 0, 0)
        #self.TopWarehouse.put_piece_queue(piece)
        #piece = Piece(self.client, 998, 1, 1, 0, 0, False, False, 0, 0)
        #piece.on_the_floor = True
        #self.TopWarehouse.put_piece_queue(piece)
        


        

        self.IDcount = 1

       

       

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

        #! Get the deliveries for the day
        #self.deliveries = DB.get_deliveries()
        #TODO 
        self.update_deliveries()
        
        if self.app.day_count == 0:
            self.root.after(1000, self.MES_loop)
            return


        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   Beggining of the day actions !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
        if last_day != self.app.day_count:
            print("New day, good morning")

            #updates the first loading dock I hope
            self.update_loading_docks()
            #to test load somrhing into the loading dock 1
            #self.loading_docks[1].load_piece(Piece(self.client, 0, 1, 0, 0, 0, False, False, 0, 0))
#!Set current date in the DB
            DB.set_current_date(self.app.day_count)
            #! Get the purchases for the day
            self.purchases = DB.get_purchasing_queue(self.app.day_count)
            print("Purchases: ", self.purchases)            
            #! Get the prod sched for the day
            daily_prod = DB.get_production_queue(self.app.day_count)
            print("Production orders for the day: ")
            for piece in daily_prod:
                self.production_orders.append(piece)
                print(f"Order ID: {piece.order_id}, Final Type: {piece.final_type}, Delivery Day: {piece.delivery_day}")
            
            #! Get the purchases for the day
            #self.purchases = DB.get_purchases(self.app.day_count)
            #! Get the deliveries for the day
            self.stats.update_orders_data(self.deliveries, self.BotWarehouse)
            
            last_day = self.app.day_count

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Permanent actions !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

        #if self.connected:
        
            #! Purchase actions
            #TODO
            self.update_loading_docks()
            #!Turn self.production_orders into pieces in the top warehouse
            self.update_pieces_w_orders()
            #!update all machines (Simpler algorith : Bottom machines then top machines)
            self.update_all_machines()
            ##!Get the piece in each line output
            self.remove_all_output_piece()
            self.unload_ReverseConveyor()
            #!Send back up the unfinished pieces 
            self.send_unfinished_back_up()
            #! Delivery actions - Barbara
            self.process_ready_orders()

            
            
        self.root.after(200, self.MES_loop)

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

    def update_loading_docks(self):
        for dock_id, dock in self.loading_docks.items():
            self.update_loading_dock(dock_id, dock)
    
    def update_loading_dock(self, dock_id, dock):
        print(f"Checking Loading Dock {dock_id}")
        if not dock.is_Occupied():
            if dock_id in [1, 2]:
                for piece in self.purchases[:]:  # Iterate over a copy of the list
                    if piece == 1:
                        print(f"Loading piece {piece} into Loading Dock {dock_id}")
                        piece_obj = Piece(self.client, 0, piece, 0, 0, 0, False, False, 0, 0)
                        dock.load_piece(piece_obj)
                        self.purchases.remove(piece)  # Remove the piece from the original list
                        break
            elif dock_id in [3, 4]:
                for piece in self.purchases[:]:  # Iterate over a copy of the list
                    if piece == 2:
                        print(f"Loading piece {piece} into Loading Dock {dock_id}")
                        piece_obj = Piece(self.client, 0, piece, 0, 0, 0, False, False, 0, 0)
                        dock.load_piece(piece_obj)
                        self.purchases.remove(piece)  # Remove the piece from the original list
                        break
        else:
            print(f"Loading Dock {dock_id} is occupied.")


            
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
        
    def next_piece(self, piece):
        path = self.transformation_paths.get((piece.type, piece.final_type))
        if not path:
            print(f"No transformation path for piece from type {piece.type} to {piece.final_type}.")
            return
        try:
            current_index = path.index(piece.type)
            if piece.tooltop and piece.toolbot:
                next_index = current_index + 2
            elif piece.tooltop or piece.toolbot:
                next_index = current_index + 1
            else:
                next_index = current_index
            if next_index < len(path):
                print(f"Updated piece type to {path[next_index]}.")
            else:
                print("Reached the end of the transformation path.")
        except ValueError:
            print(f"Current type {piece.type} is not in the transformation path.")
        return path[next_index]
        
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
            print(f"Loaded Piece o\ type {piece.type} into line {line.id} for top machine.")
        elif position == 'bot':
            #take the piece out of the warehouse
            line.setBotBusy(True)
            piece.line_id = line.id
            piece.machinebot = True
            piece.toolbot = self.find_next_transformation(piece.type, piece.final_type)
            line.load_piece(piece)
            print(f"Loaded Piece of type {piece.type} into line {line.id} for bottom machine.")

    def update_all_machines(self):
        #first update all bottom machines
        for _, line in self.lines_machines.items():
            if line.is_Occupied():
                continue
            
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

    def update_pieces_w_orders(self):

        orders_to_remove = []

        for piece_to_produce in self.production_orders:
            for piece in list(self.TopWarehouse.pieces.queue):

                if self.transformation_paths.get((piece.type, piece_to_produce.final_type)) and piece.id == 0:
  
                    piece.final_type = piece_to_produce.final_type
                    piece.order_id = piece_to_produce.order_id
                    piece.id = self.IDcount
                    self.IDcount += 1
                    piece.delivery_day = piece_to_produce.delivery_day
                    print(f"Creating piece for {piece.type}->{piece.final_type}")
                    
                    orders_to_remove.append(piece_to_produce)
                    break

        # Remove the processed orders from the production orders list
        for order_to_remove in orders_to_remove:
            self.production_orders.remove(order_to_remove)


    def remove_all_output_piece(self):
        for _, line in self.lines_machines.items():
            self.remove_output_piece(line)

        for _, dock in self.loading_docks.items():
            self.remove_from_loading_dock(dock)        

    def unload_ReverseConveyor(self):
        removed_piece = self.ReverseConveyor.remove_output_piece()
        if removed_piece:
            print("\nRemoving piece from the Reverse Conveyor output .")
            print(f"Piece type: {removed_piece.type}, machinetop: {removed_piece.machinetop}, machinebot: {removed_piece.machinebot}, tooltop: {removed_piece.tooltop}, toolbot: {removed_piece.toolbot}.")
            for similar_piece in list(self.BotWarehouse.pieces.queue):
                if similar_piece.id == removed_piece.id:

                    self.BotWarehouse.pieces.queue.remove(similar_piece)
                    similar_piece.on_the_floor = False
                    self.TopWarehouse.put_piece_queue(similar_piece)

                    print(f"Piece type: {similar_piece.type}, machinetop: {similar_piece.machinetop}, machinebot: {similar_piece.machinebot}, tooltop: {similar_piece.tooltop}, toolbot: {similar_piece.toolbot}.")               

    def remove_output_piece(self, line):
        removed_piece = line.remove_output_piece()
        if removed_piece:
            print("Removing piece from the line output.")
            print(f"Piece type: {removed_piece.type}, machinetop: {removed_piece.machinetop}, machinebot: {removed_piece.machinebot}, tooltop: {removed_piece.tooltop}, toolbot: {removed_piece.toolbot}.")
            for similar_piece in list(self.TopWarehouse.pieces.queue):
                if similar_piece.id == removed_piece.id:
                    if removed_piece.machinetop:
                        tool_transformation = self.transformations.get((similar_piece.type, similar_piece.tooltop))
                        if tool_transformation:
                            removed_piece.type = tool_transformation['result']
                    if removed_piece.machinebot:
                        tool_transformation = self.transformations.get((similar_piece.type, similar_piece.toolbot))
                        if tool_transformation:
                            similar_piece.type = tool_transformation['result']

                    similar_piece.type = self.next_piece(similar_piece)
                    similar_piece.final_type = similar_piece.final_type
                    similar_piece.on_the_floor = False
                    similar_piece.machinetop = False
                    similar_piece.machinebot = False
                    similar_piece.tooltop = 0
                    similar_piece.toolbot = 0
                    similar_piece.line_id = 0


                    self.TopWarehouse.pieces.queue.remove(similar_piece)
                    self.BotWarehouse.put_piece_queue(similar_piece)
                    #print the piece, all parameters
                    print(f"Piece type: {similar_piece.type}, final type: {similar_piece.final_type} machinetop: {similar_piece.machinetop}, machinebot: {similar_piece.machinebot}, tooltop: {similar_piece.tooltop}, toolbot: {similar_piece.toolbot}.")
                    
    def remove_from_loading_dock(self, dock):
        removed_piece = dock.remove_output_piece()
        if removed_piece:
            print("Removing piece from the dock output.")
            print(f"Piece type: {removed_piece.type}, machinetop: {removed_piece.machinetop}, machinebot: {removed_piece.machinebot}, tooltop: {removed_piece.tooltop}, toolbot: {removed_piece.toolbot}.")
            #add the piece to the top warehouse
            new_piece = Piece(self.client, 0, removed_piece.type, 0, 0, 0, False, False, 0, 0)
            self.TopWarehouse.put_piece_queue(new_piece)                    

    def send_unfinished_back_up(self):

        # if a piece in the bottom warehouse is not finished, load into the reverse conveyor
        #leave when loads a Piece
        leave = False
        for piece in list(self.BotWarehouse.pieces.queue):
            print(f"Checking if piece needs to be sent back up: {piece.id}")
            if piece.final_type != piece.type and not piece.on_the_floor:
                print(f"Piece {piece.id} is not finished.")
                if not self.ReverseConveyor.is_Occupied():
                    
                    print("Sending unfinished piece back up.")
                    print(f"Piece type: {piece.type}, final type: {piece.final_type}, machinetop: {piece.machinetop}, machinebot: {piece.machinebot}, tooltop: {piece.tooltop}, toolbot: {piece.toolbot}.")
                    self.ReverseConveyor.load_piece(piece)
                    piece.on_the_floor = True
                    leave = True
                    break
            if leave:
                break



        return

    def update_deliveries(self):
        available_docks = list(self.unloading_docks.keys())
        remaining_pieces = {dock_id: 6 for dock_id in available_docks}

        dock_piece_counts = {dock_id: 0 for dock_id in available_docks}

        for order in self.deliveries:
            if order.status in ["Ready", "Dispatching"]:
                pieces_to_unload = order.quantity
                dispatch_conveyor = []

                while pieces_to_unload > 0:
                    if not available_docks:
                        print("No available docks for unloading.")
                        return

                    dock_id = available_docks[0]
                    pieces_to_allocate = min(remaining_pieces[dock_id], pieces_to_unload)

                    remaining_pieces[dock_id] -= pieces_to_allocate
                    pieces_to_unload -= pieces_to_allocate

                    dock_piece_counts[dock_id] += pieces_to_allocate
                    dispatch_conveyor.append(str(dock_id))
                    print(f"Assigning {pieces_to_allocate} pieces of order {order.order_id} to Dock {dock_id}")

                    if remaining_pieces[dock_id] == 0:
                        available_docks.pop(0)

                order.dispatch_conveyor = ','.join(dispatch_conveyor)

                for item in self.stats.orders_tree.get_children():
                    if self.stats.orders_tree.item(item, "text") == order.order_id:
                        self.stats.orders_tree.item(item, values=(
                            order.quantity, order.final_type, order.delivery_day, order.status, order.dispatch_conveyor))
                        break

        for dock_id, count in dock_piece_counts.items():
            self.stats.dock_frames[dock_id - 1].config(text=f"Pieces: {count}")
        
        print("Updated deliveries.")
        print(self.deliveries)
        self.stats.update_orders_data(self.deliveries, self.BotWarehouse)

    def process_ready_orders(self):
        for order in self.deliveries:
            if order.status in ["Ready", "Dispatching"] and order.dispatch_conveyor:
                if order.status == "Ready":
                    order.status = "Dispatching"

                conveyors = order.dispatch_conveyor.split(',')
                for conveyor_id in conveyors:
                    conveyor_id = int(conveyor_id)
                    dock = self.unloading_docks[conveyor_id]

                    if not dock.is_Occupied():
                        piece = self.find_piece_in_warehouse(order.final_type, self.BotWarehouse)
                        if piece:
                            dock.load_piece(piece)
                            order.pieces_loaded += 1
                            self.BotWarehouse.pieces.queue.remove(piece)
                            print(f"Loaded piece {piece.id} onto Dock {conveyor_id} for order {order.order_id}")

                    if order.pieces_loaded >= order.quantity:
                        order.status = "Ready for Shipment"
                        break

                self.stats.update_orders_data(self.deliveries, self.BotWarehouse)

    def find_piece_in_warehouse(self, piece_type, warehouse):
        for piece in list(warehouse.pieces.queue):
            if piece.type == piece_type and piece.final_type == piece_type:
                return piece
        return None
                
#######################################################################################################
if __name__ == "__main__":
    #url = "opc.tcp://localhost:4840"

    mes = MES()
   
    last_day = 0
    mes.root.after(1, mes.MES_loop)
    mes.root.mainloop()
