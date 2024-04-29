import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
import tkinter as tk
import time
import json
import os

#The array in codesys is a global array, made of structs
#the struct is the meta piece
#the struct has the following fields:
#   - piecetype (int)
#   - machineTop (bool)
#   - machineBot (bool)
#   - toolTop (int)
#   - toolBot (int)



#! Not being used after the recent changes 
class Recipes:
    def __init__(self, client, all_nodes):
        self.client = client
        #node is the one from called "MetaPieces" in the json
        self.array_node = all_nodes['MetaPieces']['id']
        indexmin = 0
        indexmax = 0
    
    def add_piece(self, piece):
        try:
            # go the the first element of the array and add this struct
            reciepe_node = self.array_node + "[" + str(piece.line_id) + "]"
            reciepe_type = reciepe_node + ".pieceType"
            reciepe_machineTop = reciepe_node + ".machineTOP"
            reciepe_machineBot = reciepe_node + ".machineBOT"
            reciepe_toolTop = reciepe_node + ".toolTOP"
            reciepe_toolBot = reciepe_node + ".toolBOT"
            reciepe_done = reciepe_node + ".done"

            reciepe_type.set_value(ua.Variant(piece.type, ua.VariantType.Int16))
            reciepe_machineBot.set_value(ua.Variant(piece.machinebot, ua.VariantType.Boolean))
            reciepe_machineTop.set_value(ua.Variant(piece.machinetop, ua.VariantType.Boolean))
            reciepe_toolBot.set_value(ua.Variant(piece.toolbot, ua.VariantType.Int16))
            reciepe_toolTop.set_value(ua.Variant(piece.tooltop, ua.VariantType.Int16))
            reciepe_done.set_value(ua.Variant(False, ua.VariantType.Boolean))
            self.indexmax += 1
    
            print(f"Added piece to array.")

        except Exception as e:
            messagebox.showerror("Error, Adding Piece to Recipes", str(e))

    def send_piece(self, piece, line):
        try:
            
            print(f"Sent piece to line {line.id}.")
        except Exception as e:
            messagebox.showerror("Error, Sending Piece to Line", str(e))