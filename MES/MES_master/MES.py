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
import math

DBisWorking = True

class MES:
    def __init__(self):

        self.start_time = time.time()
        self.automatic_mode = True
        self.time_of_the_day = 0

        #! CLIENTE OPC UA e GUI
        #url = "opc.tcp://172.27.64.1:4840"
        url = "opc.tcp://172.27.64.1:4840"
        self.client = Client(url)
        self.root = tk.Tk() 
        self.app = PiecesGUI(self, lambda: self.connect_to_server(self.app), lambda: self.disconnect_server(self.app)) 
        nodes = self.load_nodes_from_file('nodes.json')
        self.connected = False
    

    
        #! PURCHASES - Array of (type)
        self.purchases = []
        for _ in range(10):
            pass
            self.purchases.append(1)
            self.purchases.append(2)
            pass


        #! PRODUCTION ORDERS - Array of (final_type) - Working :)
        self.production_orders = []
        #self.production_orders.append(Piece_to_produce(1, 9, 2))
        #self.production_orders.append(Piece_to_produce(2, 9, 3))
        #self.production_orders.append(Piece_to_produce(3, 5, 5))
        #self.production_orders.append(Piece_to_produce(4, 5, 5))

        #self.production_orders.append(Piece_to_produce(5, 5, 10))
        #self.production_orders.append(Piece_to_produce(6, 5, 10))
        #self.production_orders.append(Piece_to_produce(7, 5, 10))
        #self.production_orders.append(Piece_to_produce(8, 5, 10))

        #self.production_orders.append(Piece_to_produce(5, 9, 10))
        #self.production_orders.append(Piece_to_produce(6, 9, 10))
        #self.production_orders.append(Piece_to_produce(7, 9, 10))
        #self.production_orders.append(Piece_to_produce(8, 9, 10))

        #self.production_orders.append(Piece_to_produce(5, 9, 10))
        #self.production_orders.append(Piece_to_produce(6, 9, 10))
        #self.production_orders.append(Piece_to_produce(7, 9, 10))
        #self.production_orders.append(Piece_to_produce(8, 9, 10))
        

        #! DELIVERIES - Array of (orders) 
        self.deliveries = []
        #self.deliveries.append(Order(quant, type, id, delivery day
        self.deliveries.append(Order(8, 9, 5, 2))
        self.deliveries.append(Order(3, 9, 4, 3))
        #self.deliveries.append(Order(2, 9, 5, 3))

        #self.deliveries.append(Order(2, 9, 5, 5))
        #self.deliveries.append(Order(2, 9, 5, 5))

        #self.deliveries.append(Order(1, 5, 1, 5))
        #self.deliveries.append(Order(1, 6, 2, 5))
        #self.deliveries.append(Order(1, 7, 3, 5))
        #self.deliveries.append(Order(1, 9, 4, 5))

        #self.deliveries.append(Order(3, 5, 1, 10))
        #self.deliveries.append(Order(3, 6, 2, 10))
        #self.deliveries.append(Order(3, 7, 3, 10))
        #self.deliveries.append(Order(3, 9, 4, 10))
        
        
        #!WAREHOUSES
        self.TopWarehouse = Warehouse(self.client)
        self.BotWarehouse = Warehouse(self.client)
        #O warehouse de cima começa com 20 peças 1
        for _ in range(20):
            piece = Piece(self.client, 0, 1, 0, 0, 0, False, False, 0, 0)
            self.TopWarehouse.put_piece_queue(piece)        
        for _ in range(10):
            piece = Piece(self.client, 0, 9, 9, 0, 0, False, False, 0, 0)
            self.BotWarehouse.put_piece_queue(piece)

        #self.TopWarehouse.set_simulation_warehouse()
        #self.BotWarehouse.set_simulation_warehouse()
        #self.SFS = Warehouse(self.client)

        self.IDcount = 1

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

        self.dispatch_conveyor = [0, 0, 0, 0]

        self.ReverseConveyor = Line(self.client, nodes, "ReverseConveyor", 15, {}, {})

        self.stats = ShopFloorStatisticsWindow(self.root, self)
        
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
            (2, 1): {'result': 8},
            (8, 6): {'result': 7},
            (8, 5): {'result': 9}
        }
        #Tods os paths possíveis, em pares inicial e final
        self.transformation_paths = {
            (1, 3): [1, 3],
            (1, 4): [1, 3, 4],
            (1, 5): [1, 3, 4, 5],
            (1, 6): [1, 3, 4, 6],
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

        
  
        self.dispatch_node = nodes["Dispatch"]["dispatch"]

        print("\nMES initialized\n\n")

#######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! MES Loop !!!!!!!!!!!!!!
    def MES_loop(self):
        global last_day

        self.app.update_orders_display()
        self.app.update_time_display()
        if DBisWorking:
            try:
                DB.set_current_date(self.app.day_count)
            except Exception as e:    
                messagebox.showerror("Error setting current date to ERP", str(e))
                
        if self.automatic_mode:
            elapsed_time = time.time() - self.start_time
            self.time_of_the_day = int(elapsed_time)
            if self.time_of_the_day >= 60:
                self.start_time = time.time()
                self.increment_day()

        if self.app.day_count == 0:
            self.root.after(1000, self.MES_loop)
            return

        
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   Beggining of the day actions !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
        if last_day != self.app.day_count:
            print("New day, good morning")
            #!Set current date in the DB
            if DBisWorking and self.connected:
                DB.set_current_date(self.app.day_count)
            #! Get the purchases for the day
                newpurchases = DB.get_purchasing_queue(self.app.day_count) 
                #add the new purchases to the purchases list
                self.purchases.extend(newpurchases)
            #! Get the prod sched for the day
                daily_prod = DB.get_production_queue(self.app.day_count)
                for piece in daily_prod:
                    self.production_orders.append(piece)
                
            #! Get the deliveries for the day
                new_deliveries = DB.get_deliveries()
                for order in new_deliveries:
                    if order.order_id not in [o.order_id for o in self.deliveries]:
                        self.deliveries.append(order) 

            
            self.check_ready_orders()
            self.update_deliveries()

            last_day = self.app.day_count
            

            #! Update the statistics
            
    
                
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Permanent actions !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

        if self.connected:
            self.TopWarehouse.sort_queue_by_delivery_day()
            self.sort_orders()
            #! Purchase actions
            self.update_loading_docks()
            #!Turn self.production_orders into pieces in the top warehouse
            self.update_pieces_w_orders()
            #!update all machines (Simpler algorith : Bottom machines then top machines)
            self.update_all_machines()
            ##!Get the piece in each line output 
            self.remove_all_output_piece()
            self.update_machines_busy()
            self.unload_ReverseConveyor()
            #!Send back up the unfinished pieces 
            self.send_unfinished_back_up()
            #! Delivery actions
            self.process_dispatching_orders()
            self.stats.update_orders_data(self.deliveries)
            self.stats.update_purchasing_queue(self.purchases)
            self.stats.update_production_queue(self.production_orders)
            self.stats.update_machine_statuses()
            self.delivery()

        self.root.after(200, self.MES_loop)

    #######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Time Functions
    def toggle_mode(self):
        self.automatic_mode = not self.automatic_mode

    def increment_day(self):
        self.app.day_count += 1
        print("Incrementing day")
    
    

    #######################################################################################################
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!OPC UA Client Functions
    def delivery(self):
        if self.time_of_the_day > 45:
            #set all dispatches to true
            for i in range(4):
                node = self.client.get_node(self.dispatch_node + f"[{i}]")
                node.set_value(ua.Variant(True, ua.VariantType.Boolean))


            for order in self.deliveries:
                if order.status == "Dispatching" and order.pieces_loaded == order.quantity:
                    #print("Order", order.order_id, "is ready for shipment")
                    order.status = "Dispatched"
                    for cnvyor in order.dispatch_conveyor.split(','):
                        self.dispatch_conveyor[int(cnvyor) - 1] = 0
                    #order.dispatch_conveyor = ""

                    #update the interface
                    self.stats.update_orders_data(self.deliveries)
                    if DBisWorking:
                        DB.set_dispatch_date(order.order_id, self.app.day_count)
                    
        else :
            for i in range(4):
                node = self.client.get_node(self.dispatch_node + f"[{i}]")
                node.set_value(ua.Variant(False, ua.VariantType.Boolean))
                

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

    def check_ready_orders(self):
        #store the quantities of pieces 5 6 7 and 9 in the bot warehouse
        quantities = {i: 0 for i in range(1, 10)}
        for piece in list(self.BotWarehouse.pieces.queue):
            if not piece.to_dispatch:
                quantities[piece.type] += 1

        for order in self.deliveries:
            total_available = quantities[order.final_type]
            if order.status not in ["Ready", "Dispatched", "Dispatching"]:
                if total_available >= order.quantity:
                    #mark order.quantity pieces as to_dispatch
                    for _ in range(order.quantity):
                       for piece in list(self.BotWarehouse.pieces.queue):
                           if piece.type == order.final_type and not piece.to_dispatch:
                               piece.to_dispatch = True
                               break
                               
                    order.status = "Ready"
                    quantities[order.final_type] -= order.quantity
        self.stats.update_orders_data(self.deliveries)


    def update_loading_docks(self):
        for dock_id, dock in self.loading_docks.items():
            self.update_loading_dock(dock_id, dock)
    


    def update_loading_dock(self, dock_id, dock):
       
        if not dock.is_Occupied():
            if dock_id in [1, 2]:
                for piece in self.purchases[:]:  
                    if piece == 1:
                       
                        piece_obj = Piece(self.client, 0, piece, 0, 0, 0, False, False, 0, 0)
                        dock.load_piece(piece_obj)
                        self.purchases.remove(piece)  
                        break
            elif dock_id in [3, 4]:
                for piece in self.purchases[:]: 
                    if piece == 2:
                        
                        piece_obj = Piece(self.client, 0, piece, 0, 0, 0, False, False, 0, 0)
                        dock.load_piece(piece_obj)
                        self.purchases.remove(piece)  
                        break
        
          
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

        if piece.id == 0:
            return False
        

        if (position == 'top' and line.isTopBusy()) or (position == 'bot' and (line.isBotBusy() or line.isTopBusy())):
            return False

        next_tool = self.find_next_transformation(current_type, final_type)

        if next_tool is None:
            return False

        if line.has_tool(next_tool, position):
            return True
        
        else:
            return False

    def get_raw_material(self, final):
        if final in [1, 3, 4, 5, 6]:
            return 1
        elif final in [8, 9, 7]:
            return 2
        else :
            return None
        
    def next_piece(self, piece):
        path = self.transformation_paths.get((piece.type, piece.final_type))
        if not path:
            return None  # Return None if no path exists
        try:
            current_index = path.index(piece.type)
            if piece.tooltop and piece.toolbot:
                next_index = current_index + 2
            elif piece.tooltop or piece.toolbot:
                next_index = current_index + 1
            if next_index < len(path):
                return path[next_index]
        except ValueError:
            return None
        return None
        

    def update_machine(self, line, position, piece):
        if not self.check_machine_can_process(line, position, piece):
            return
    
        elif position == 'top':
            if line.isTopBusy():
                return

            line.setTopBusy(True)
            piece.line_id = line.id
            piece.machinetop = True
            piece.tooltop = self.find_next_transformation(piece.type, piece.final_type)

            line.load_piece(piece)
    
        elif position == 'bot':
            if line.isTopBusy() or line.isBotBusy():
                return
            line.setBotBusy(True)
            piece.line_id = line.id
            piece.machinebot = True
            piece.toolbot = self.find_next_transformation(piece.type, piece.final_type)
            line.load_piece(piece)


    def update_pair_of_machines(self, line, piece):
        if piece.on_the_floor:
            return
        #check if both machines are available
        if line.isTopBusy() :
            return
        #check if the piece has more than one transofarmation to do
        path = self.transformation_paths.get((piece.type, piece.final_type))
        if not path or len(path) < 2:
            return
        
        first_transformation_tool = self.find_next_transformation(piece.type, path[1])
        if not first_transformation_tool or not line.has_tool(first_transformation_tool, 'top'):
            return
        temp_piece = Piece(self.client, piece.id, path[1], piece.final_type, piece.order_id, piece.delivery_day, False, False, first_transformation_tool, 0)
        second_transformation_tool = self.find_next_transformation(temp_piece.type, temp_piece.final_type)
        if not second_transformation_tool or not line.has_tool(second_transformation_tool, 'bot'):
            return
        
        
        piece.line_id = line.id

        line.setTopBusy(True)
        piece.machinetop = True
        piece.tooltop = first_transformation_tool
        
        line.setBotBusy(True)
        piece.machinebot = True
        piece.toolbot = second_transformation_tool


        
        line.load_piece(piece)

        pass

    def sort_orders(self):
        self.production_orders.sort(key=lambda x: x.delivery_day)
        self.deliveries.sort(key=lambda x: x.delivery_day)


    def update_all_machines(self):

        """Algoritmo de atualização de máquinas
            
        
            Melhorado
            Para cada peça
                Tirar as proximas transformaçoes
                Se > 2 
                    Ver se há alguma linha com essas ferramentas

                Ver se há alguma tool bot com essas ferramentas
                Ver se há alguma tool top com essas ferramentas

            Done
            1) Ver se há alguma linha que faça o par de transformações
            2) Ver se há alguma MBOT que faça a prox transformação
            3) Ver se há alguma MTOP que faça a prox transformação

        """ 

        
        for piece in list(self.TopWarehouse.pieces.queue):
            if piece.id == 0 or piece.on_the_floor:
                continue
            else:
                flag_processed = False
                #check for pairs

                path = self.transformation_paths.get((piece.type, piece.final_type))
                if not path :
                    continue
                first_transformation_tool = self.find_next_transformation(piece.type, path[1])
                print("First transformation for piece of type", piece.type, " is ", first_transformation_tool)

                #Let's check for bot machines with the first tool 
                print("Looking for single bot machines")
                for _, line in self.lines_machines.items():
                    if line.is_Occupied():
                        continue
                    if first_transformation_tool and line.current_tool_bot == first_transformation_tool:
                        print("\nFOUND A LINE WITH THE CORRECT BOT MACHINE ON LINE \n", line.id)
                        self.update_machine(line, 'bot', piece)
                        flag_processed = True
                        break
                if flag_processed:
                    continue

                print("Looking for lines")
                if len(path) > 2:
                    print("Path has 2 or more transformation")
                    temp_piece = Piece(self.client, piece.id, path[1], piece.final_type, piece.order_id, piece.delivery_day, False, False, first_transformation_tool, 0)
                    second_transformation_tool = self.find_next_transformation(temp_piece.type, temp_piece.final_type)
                    if not second_transformation_tool:
                        continue
                    print("Second transformation for piece of type", piece.type, " is ", second_transformation_tool)

                    #check if the lines has the correct transformations tools
                    print("Top and bot tools are ", first_transformation_tool, second_transformation_tool)
                    print("Current tools are ", line.current_tool_top, line.current_tool_bot)
                    if line.current_tool_bot == first_transformation_tool and line.current_tool_top == second_transformation_tool:
                        print("\nFOUND A LINE WITH THE CORRECT TOOLS ON LINE \n", line.id)
                        self.update_pair_of_machines(line, piece)
                    
                    
                    
                                    

        
                

              
                

        #percorrer as máquinas de baixo
        for _, line in self.lines_machines.items():
            if line.is_Occupied():
                continue
            for piece in list(self.TopWarehouse.pieces.queue):
                if piece.id == 0:
                    continue
                if not piece.machinetop and not piece.machinebot and piece.id != 0 and not piece.on_the_floor:
                    self.update_machine(line, 'bot', piece)

        #look for pairs of machines
        for _, line in self.lines_machines.items():
            if line.is_Occupied():
                continue
            for piece in list(self.TopWarehouse.pieces.queue):
                if piece.id == 0:
                    continue
                if not piece.machinetop and not piece.machinebot and piece.id != 0 and not piece.on_the_floor:
                    if line.top_busy:
                        continue
                    self.update_pair_of_machines(line, piece)

        #percorrer as máquinas de cima
        for _, line in self.lines_machines.items():
            if line.is_Occupied():
                continue
            for piece in list(self.TopWarehouse.pieces.queue):
                if piece.id == 0:
                    continue
                if not piece.machinetop and not piece.machinebot and piece.id != 0 and not piece.on_the_floor:
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
                    orders_to_remove.append(piece_to_produce)
                    break
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
            
            for similar_piece in list(self.BotWarehouse.pieces.queue):
                if similar_piece.id == removed_piece.id:

                    self.BotWarehouse.pieces.queue.remove(similar_piece)
                    similar_piece.on_the_floor = False
                    self.TopWarehouse.put_piece_queue(similar_piece)

    def remove_output_piece(self, line):
        removed_piece = line.remove_output_piece()
        if removed_piece:
            """
            if removed_piece.machinetop:
                print(f"Setting top to Free in line {line.id}")
                line.setTopBusy(False)
            if removed_piece.machinebot:
                print(f"Setting bot to Free in line {line.id}")
                line.setBotBusy(False)          
            """ 
               
            for similar_piece in list(self.TopWarehouse.pieces.queue):
                if similar_piece.id == removed_piece.id:
                    similar_piece.type = removed_piece.type #hmmm test this
                    similar_piece.on_the_floor = False
                    similar_piece.machinetop = False
                    similar_piece.machinebot = False
                    similar_piece.tooltop = 0
                    similar_piece.toolbot = 0
                    similar_piece.line_id = 0
            
                    self.TopWarehouse.pieces.queue.remove(similar_piece)
                    self.BotWarehouse.put_piece_queue(similar_piece)

    def update_machines_busy(self):
        if self.connected:
            for lines in self.lines_machines.values():
                lines.update_machine_busy()

    def remove_from_loading_dock(self, dock):
        removed_piece = dock.remove_output_piece()
        if removed_piece:
            #add the piece to the top warehouse
            new_piece = Piece(self.client, 0, removed_piece.type, 0, 0, 0, False, False, 0, 0)
            self.TopWarehouse.put_piece_queue(new_piece)                    

    def send_unfinished_back_up(self):

        # if a piece in the bottom warehouse is not finished, load into the reverse conveyor
        #leave when loads a Piece
        if not self.ReverseConveyor.is_Occupied():  
            leave = False
            for piece in list(self.BotWarehouse.pieces.queue):
                if piece.final_type != piece.type and not piece.on_the_floor:
                    self.ReverseConveyor.load_piece(piece)
                    piece.on_the_floor = True
                    leave = True

                if leave:
                    break



        return

    def update_deliveries(self):
        #available_docks = list(self.unloading_docks.keys())
        available_docks = []
        for dock_id, dock in self.unloading_docks.items():
            if self.dispatch_conveyor[dock_id - 1] == 0:
                available_docks.append(dock_id)


        for order in self.deliveries:
            if order.status in ["Ready"] and order.delivery_day <= self.app.day_count:
                pieces_to_unload = order.quantity
                dispatch_conveyor = []

                number_of_needed_docks = math.ceil(pieces_to_unload / 6)
                if number_of_needed_docks > len(available_docks):
                    return
                else :
                    while pieces_to_unload > 0:
                            
                        dock_id = available_docks[0]
                        pieces_to_allocate = min(6, pieces_to_unload)

                        pieces_to_unload -= pieces_to_allocate

                        dispatch_conveyor.append(str(dock_id))

                        available_docks.pop(0)

                        self.dispatch_conveyor[dock_id - 1] = order.order_id

                    order.status = "Dispatching"

                order.dispatch_conveyor = ','.join(dispatch_conveyor)
     
        
        

    def process_dispatching_orders(self):
        for order in self.deliveries:
            #print("Processing order", order.order_id, "with status", order.status, "and dispatch conveyor", order.dispatch_conveyor, "and pieces loaded", order.pieces_loaded)
            if order.status in ["Dispatching"] and order.dispatch_conveyor and order.pieces_loaded < order.quantity:
                conveyors = order.dispatch_conveyor.split(',')
                print("Conveyors", conveyors)
                for conveyor_id in conveyors:
                    print("Conveyor id", conveyor_id)
                    conveyor_id = int(conveyor_id)
                    dock = self.unloading_docks[conveyor_id]

                    if not dock.is_Occupied():
                        piece = self.find_piece_in_warehouse(order.final_type, self.BotWarehouse)
                        if piece:
                            dock.load_piece(piece)
                            order.pieces_loaded += 1
                            self.BotWarehouse.pieces.queue.remove(piece)
                   
                #self.stats.update_orders_data(self.deliveries, self.BotWarehouse)

    def find_piece_in_warehouse(self, piece_type, warehouse):
        for piece in list(warehouse.pieces.queue):
            if piece.type == piece_type:
                return piece
        return None
                
#######################################################################################################
if __name__ == "__main__":
    #url = "opc.tcp://localhost:4840"

    mes = MES()
   
    last_day = 0
    mes.root.after(1, mes.MES_loop)
    mes.root.mainloop()
