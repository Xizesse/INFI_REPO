import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
import tkinter as tk
import time
import json
import os
from Piece import Piece

NO_PIECE = 0
GHOST_PIECE = -1

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

    def load_piece(self, piece):
        try:
            #if self.is_Occupied():
            #    print("Line is occupied. Cannot load piece.")
            #    return
            #print what machine is True
            #load the meta piece into the line input
            self.load_meta_piece(piece)
            #load the physical piece 
            self.load_physical_piece(piece)
            piece.on_the_floor = True
        
        except Exception as e:
            messagebox.showerror("Error Loading the Piece", str(e))

    def load_physical_piece(self, piece): 
        try:
            piece_out_node = self.client.get_node(self.piece_out_node_id)
            #print what is on that node
            piece_out_node.set_value(ua.Variant(piece.type, ua.VariantType.Int16))
            time.sleep(1)
            piece_out_node.set_value(ua.Variant(0, ua.VariantType.Int16))
            
        except Exception as e:
            messagebox.showerror("Error Loading Physical Piece", str(e))

    def load_meta_piece(self, piece): #Loads the meta piece into the line input
        
        try:
            #Set the type
            type_node = self.client.get_node(self.line_input_node_id + ".pieceTYPE")
            type_node.set_value(ua.Variant(piece.type, ua.VariantType.Int16))
            #Set machine top
            machine_top_node = self.client.get_node(self.line_input_node_id + ".machineTOP")
            machine_top_node.set_value(ua.Variant((not piece.machinetop), ua.VariantType.Boolean))
            #Set machine bot
            machine_bot_node = self.client.get_node(self.line_input_node_id + ".machineBOT")
            machine_bot_node.set_value(ua.Variant((not piece.machinebot), ua.VariantType.Boolean))
            #Set tool top
            tool_top_node = self.client.get_node(self.line_input_node_id + ".toolTOP")
            tool_top_node.set_value(ua.Variant(piece.tooltop, ua.VariantType.Int16))
            #Set tool bot
            tool_bot_node = self.client.get_node(self.line_input_node_id + ".toolBOT")
            tool_bot_node.set_value(ua.Variant(piece.toolbot, ua.VariantType.Int16)) 
            #Set ID
            id_node = self.client.get_node(self.line_input_node_id + ".ID")
            id_node.set_value(ua.Variant(piece.id, ua.VariantType.Int16))

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


    def remove_output_piece(self): #Removes the piece from the line output
        try:
            #new piece to return, and get all the parameters
            type_node = self.client.get_node(self.line_output_node_id + ".pieceTYPE")
            type_value = type_node.get_value()
            if type_value == NO_PIECE:
                return None
            machinetop_node = self.client.get_node(self.line_output_node_id + ".machineTOP")
            machinetop_value = machinetop_node.get_value()
            machinebot_node = self.client.get_node(self.line_output_node_id + ".machineBOT")
            machinebot_value = machinebot_node.get_value()
            tooltop_node = self.client.get_node(self.line_output_node_id + ".toolTOP")
            tooltop_value = tooltop_node.get_value()
            toolbot_node = self.client.get_node(self.line_output_node_id + ".toolBOT")
            toolbot_value = toolbot_node.get_value()
            id_node = self.client.get_node(self.line_output_node_id + ".ID")
            id_value = id_node.get_value()

            #set type to NO_PIECE
            type_node.set_value(ua.Variant(NO_PIECE, ua.VariantType.Int16))
            if machinebot_value == True:
                self.bot_busy = False
            if machinetop_value == True:
                self.top_busy = False
    
            return Piece(self.client, id_value, type_value, 0, 0, 0, machinetop_value, machinebot_value, tooltop_value, toolbot_value)
        except Exception as e:
            messagebox.showerror(f"Error Removing Output Piece from Line {self.id}", str(e))

        

    def is_Occupied(self): #Returns True if the line is occupied
        try:
            ocupied = self.get_input_piece_type() != NO_PIECE
            #print(f"Line {self.id} is occupied: {ocupied}")
            return ocupied
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
