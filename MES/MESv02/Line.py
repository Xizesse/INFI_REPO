import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
from GUI import OPCUAClientGUI 
import tkinter as tk
import time
import json
import os

#TODO escalar para machine bot ...

class Line:
    def __init__(self, client, all_nodes, line_key):
        self.occupied = False
        self.client = client
        self.line_info = all_nodes[line_key]  
        
        self.tool_node_id = all_nodes[self.line_info['toolTop']]['id']
        self.machine_node_id = all_nodes[self.line_info['machineOFF']]['id']
        self.piece_out_node_id = all_nodes[self.line_info['pieceOut']]['id']
    

    def change_tool(self, new_tool):
        try:
            tool_node = self.client.get_node(self.tool_node_id)
            tool_node.set_value(ua.Variant(new_tool, ua.VariantType.Int16))
            print(f"Changed tool to {new_tool}.")
        except Exception as e:
            messagebox.showerror("Tool Change Error", str(e))

    def change_machine_off(self, state):
        try:
            machine_node = self.client.get_node(self.machine_node_id)
            machine_node.set_value(ua.Variant(state, ua.VariantType.Boolean))
            print(f"Machine {'turned off' if state else 'turned back on'} successfully.")
        except Exception as e:
            messagebox.showerror("Machine Control Error", str(e))

    def load_piece(self, new_piece):
        try:
            piece_out_node = self.client.get_node(self.piece_out_node_id)
            current_value = piece_out_node.get_value()
            print(f"Current value: {current_value}")
            
            piece_out_node.set_value(ua.Variant(0, ua.VariantType.Int16))
            time.sleep(1)
            piece_out_node.set_value(ua.Variant(new_piece, ua.VariantType.Int16))
            print(f"Set new piece to {new_piece}.")
        except Exception as e:
            messagebox.showerror("Load Piece Error", str(e))