import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
import tkinter as tk
import time
import json
import os
from Piece import Piece

NO_PIECE = -1
GHOST_PIECE = 0

#TODO funções para a MES fazer sair as meta + peças
#TODO funções para a MES pegar nas peças produzidas

class Line:
    def __init__(self, client, all_nodes, line_key, line_id, top_tools, bot_tools):
        self.id = line_id
        self.client = client
        self.line_info = all_nodes[line_key]
        
        self.top_tools = top_tools
        self.bot_tools = bot_tools

        self.piece_out_node_id = self.line_info['pieceOut']
        self.line_input_node_id = self.line_info['lineIn']
        self.line_output_node_id = self.line_info['lineOut']

        self.top_busy = False
        self.bot_busy = False

    def load_piece(self, piece):#Loads both the physical and the meta piece#
        try:
            if self.is_Occupied():
                print("Line is occupied. Cannot load piece.")
                return
            print(f"Loading piece {piece.id} of type {piece.type} into line {self.id}.")
            #load the meta piece into the line input
            self.load_meta_piece(piece)
            #load the physical piece 
            self.load_physical_piece(piece)
            

        except Exception as e:
            messagebox.showerror("Error Loading the Piece", str(e))

    def load_physical_piece(self, piece): #Loads the physical piece into the line output
        try:
            piece_out_node = self.client.get_node(self.piece_out_node_id)
            piece_out_node.set_value(ua.Variant(0, ua.VariantType.Int16))
            time.sleep(1)
            piece_out_node.set_value(ua.Variant(piece.type, ua.VariantType.Int16))
            
            print(f"Loaded a physical piece of type {piece.type} into line {self.id}.")
        except Exception as e:
            messagebox.showerror("Error Loading Physical Piece", str(e))

    def load_meta_piece(self, piece): #Loads the meta piece into the line input
        
        try:
            #Set the type
            """"
            print("Sending meta piece to line input.")
            type_node = self.client.get_node(self.line_input_node_id + ".pieceType")
            type_node.set_value(ua.Variant(piece.type, ua.VariantType.Int16))
            #Set machine top
            machine_top_node = self.client.get_node(self.line_input_node_id + ".machineTOP")
            machine_top_node.set_value(ua.Variant(piece.machinetop, ua.VariantType.Boolean))
            #Set machine bot
            machine_bot_node = self.client.get_node(self.line_input_node_id + ".machineBOT")
            machine_bot_node.set_value(ua.Variant(piece.machinebot, ua.VariantType.Boolean))
            #Set tool top
            tool_top_node = self.client.get_node(self.line_input_node_id + ".toolTOP")
            tool_top_node.set_value(ua.Variant(piece.tooltop, ua.VariantType.Int16))
            #Set tool bot
            tool_bot_node = self.client.get_node(self.line_input_node_id + ".toolBOT")
            tool_bot_node.set_value(ua.Variant(piece.toolbot, ua.VariantType.Int16)) 
            """
        except Exception as e:
            messagebox.showerror("Error Loading Meta Piece", str(e))

    def get_input_piece_type(self): #Returns the type of the piece in the line input
        try:
            #node is the line_input_node + ".pieceType"
            type_node = self.client.get_node(self.line_input_node_id + ".pieceType")
            type_value = type_node.get_value()
            return type_value
        except Exception as e:
            messagebox.showerror("Error Getting Input Piece Type", str(e))

    def is_Occupied(self): #Returns True if the line is occupied
        try:
            return False
            return self.get_input_piece_type() != NO_PIECE
        except Exception as e:
            messagebox.showerror("Error Checking Line Occupancy", str(e))

    def has_tool(self, tool, position):
        if position == 'top':
            return tool in self.top_tools
        elif position == 'bot':
            return tool in self.bot_tools

    def isTopBusy(self):
        return self.top_busy
    
    def isBotBusy(self):
        return self.bot_busy

    def setTopBusy(self, state):
        self.top_busy = state

    def setBotBusy(self, state):
        self.bot_busy = state

    def change_tool(self, new_tool, position):
        #send a ghost piece with the transformation
        if position == 'top':
            if new_tool in self.top_tools:
                ghost = Piece(0, GHOST_PIECE, 0, 0, 0, new_tool, 0, 0)
                self.load_meta_piece(ghost)
        elif position == 'bot':
            if new_tool in self.bot_tools:
                ghost = Piece(0, GHOST_PIECE, 0, 0, 0, 0, 0, new_tool)
                self.load_meta_piece(ghost)


    ##Old functions
