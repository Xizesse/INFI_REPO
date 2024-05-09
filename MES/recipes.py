import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
from GUI import OPCUAClientGUI 
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



class Recipes:
    def __init__(self, client, all_nodes):
        self.client = client
        #node is the one from called "MetaPieces" in the json
        self.array_node = all_nodes['MetaPieces']['id']
    
    def add_piece(self, piece):
        try:
            # go the the first element of the array and add this struct
            
            print(f"Added piece to array.")
            
        except Exception as e:
            messagebox.showerror("Error, Adding Piece to Recipes", str(e))

    def send_piece(self, piece, line):
        try:
            print(f"Sent piece to line {line.id}.")
        except Exception as e:
            messagebox.showerror("Error, Sending Piece to Line", str(e))