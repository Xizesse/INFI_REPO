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
import DB

#TODO : meter a MES a fazer sair uma peça com metapeça
    #TODO : com transformações


connected = False

#TODO Passar para database de warehouse
upperWarehouse = {
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
bottomWarehouse = {
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
orders = {
    3: 1,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    9: 0
}

order_queue = Queue()
for piece, quantity in orders.items():
    if quantity > 0:
        for _ in range(quantity):
            order_queue.put(piece)
#Print this queue
print(order_queue.queue)


transformations = {
#    (start_piece, tool): {'result': final_piece}
    (1, 1): {'result': 3},
    (3, 2): {'result': 4},
    (3, 3): {'result': 4},
    (4, 4): {'result': 5},
    (4, 2): {'result': 6},
    (2, 3): {'result': 7},
    (8, 1): {'result': 8},
    (8, 6): {'result': 7},
    (8, 5): {'result': 9},

}

machines = {
    1: {1, 2, 3},
    2: {1, 2, 3},
    3: {1, 4, 5},
    4: {1, 4, 6},
}

#TODO Expecificar que machines por linha como ? No constructor ? 


#######################################################################################################

def connect_to_server(gui):
    global connected

    if connected:
        return
    try:
        # OPC UA connect logic here
        client.connect()
        gui.status_label.config(text="Connected", fg="green")
        gui.start_blinking()
        connected = True
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))
    


def load_nodes_from_file(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_path = os.path.join(dir_path, filename)
    with open(full_path, 'r') as file:
        data = json.load(file)
    return data



def disconnect_server(gui):
    global connected
    if not connected:
        return
    try:
        # OPC UA disconnect logic here
        client.disconnect()
        gui.status_label.config(text="Disconnected", fg="red")
        gui.stop_blinking()
        connected = False
    except Exception as e:
        messagebox.showerror("Disconnection Error", str(e))

""" def update_client():
    try:
        node_id = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Factory_Transformation.Line1.Tools_TOP[0]"
        node = client.get_node(node_id)
        value = node.get_value()
        print(value)
        print("Updated client")  # Placeholder for actual update logic
    except Exception as e:
        messagebox.showerror("Update Error", str(e))
 """
    
#######################################################################################################

def process_order(piece):
    if line1.occupied:
            print("Line is occupied. Cannot load piece.")
            return
    if upperWarehouse[piece] > 0:
        #pop the first item from the queue
        order_queue.get()
        line1.load_piece(piece)
        upperWarehouse[piece] -= 1
        print(f"Loaded piece {piece} to line.")
    else:
        print(f"Piece {piece} not available in warehouse.")
        precursor, tool, result = find_transformation(piece)
        if precursor is not None:
            print(f"Found transformation for piece {piece}.")
            print(f"Piece {piece} will be transformed into piece {result} using tool {tool}.")
            line1.change_tool(tool)
            order_queue.get()
            line1.load_piece(precursor)
            upperWarehouse[precursor] -= 1
            print(f"Loaded piece {precursor} to line.")
        else:
            print(f"Could not find transformation for piece {piece}.")
            return

def process_order_metapeça(piece):
    #TODO criar a metapeça
    piece = MetaPessa(client, id, type, final_type, order_id, machine_id, transform)
    #TODO colocar no vetor de receitas a struct da peça, não esquecer confirmar o index
    print(f"Created metapessa {piece_id}.")


def find_transformation(final_piece):
    for (start_piece, tool), transformation in transformations.items():
        if transformation['result'] == final_piece and upperWarehouse[start_piece] > 0:
            return start_piece, tool, final_piece
    return None, None, None



def MES_loop():
    global connected
    global last_day

    print(app.day_count)
    if connected and app.day_count > 0:
        #update_client()
        try:

            """if not order_queue.empty():
                next_order = order_queue.queue[0]
                print("Next process: ", next_order)
                process_order(next_order)
            else :
                print("No orders in queue.")
            """
            if app.day_count == 1 and last_day != app.day_count:
                print("Rise and shine, it's Day 1")
                

                #TODO Create a Piece
                id = 1
                type = 1
                final_type = 3
                order_id = 1
                machine_top = 1
                machine_bot = 1

                piece1 = Piece(client, id, type, final_type, order_id, machine_top, machine_bot)
                #TODO Change the array on the PLC
                piece1.load_piece(1)
                #TODO Send the Piece to the warehouse

                #TODO Send the MetaPiece index to the warehouse

                  

                last_day = app.day_count

                    
            if app.day_count == 2 and last_day != app.day_count:
                print("Food moning, it's Day 2")
                


                last_day = app.day_count
            
            
        except Exception as e:
            messagebox.showerror("Set Value Error", str(e))
    app.update_queue()
    root.after(1000, MES_loop)




#######################################################################################################
if __name__ == "__main__":
    url = "opc.tcp://172.27.64.1:4840"
    #url = "opc.tcp://localhost:4840"

    client = Client(url)
    root = tk.Tk()
    app = OPCUAClientGUI(root, lambda: connect_to_server(app), lambda: disconnect_server(app))
    app.set_queue(order_queue)
    nodes = load_nodes_from_file('nodes.json')
    line1 = Line(client, nodes, "Line1", 1)
    last_day = 0
    root.after(1, MES_loop)
    root.mainloop()
