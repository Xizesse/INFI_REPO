import sys
from opcua import Client
from opcua import ua
from tkinter import messagebox
from GUI import OPCUAClientGUI 
import tkinter as tk
import time
import json
import os

"""
    #? A MES faz sair as peças E as metapeças
    Para a PLC, a metapeça isto vai ser uma struct que vai circular entre os tapetes
    Circula diretamente a struct
    Ao chegar ao tapete de uma máquina, vê tool top tool bot
        Se for fantasma, ou seja, pieceType = 0 , segue
    Se corresponder, a máquina faz a transformação 
    A peça é enviada para o WAREHOUSE de saída
    A metapeça é enviada até ao útlimo tapete.
    Quando um tapete passa, poe o valor em si.
        tool
    A MES tira receitas do ultimo tapete
    

    #? Penso que fazer sair as peças dos armazens, tanto o de cima como o de baixo é mais fácil ser a MES, em vez de 
#? ter que criar um warehouse complexo na PLC
    #hmm A otimização de "Fazer a maquina mudar sem transformar", passa para ser enviar uma Piece sem transformar 
    #hmm A MES manda sair sempre primeiro o que vai para a maquina BOT de um tapete antes de mandar para o TOP
    #hmm Em princípio a MES, com isto, vai poder ser cega a o que está a acontecer na PLC, manda ordens assincronas
    #hmm Corre mal quando : Estiver uma peça no tapete de entrada e a MES mandar sair logo outra
                #hmm Dá para contornar este problema (timings / ler o sensor do primeiro tapete)

"""

"""
PLC : 
Array Global de Receitas

"""

class Piece:
        #criar a metapeça
    def _init_(self, client, id, type, final_type, order_id, delivery_day, machine_top, machine_bot, tool_top, tool_bot):
        """
        Args:
        client (opcua.Client): The client object.
        id (int): The ID of the piece.
        type (int): The type of the piece.
        final_type (int): The final type of the piece.
        order_id (int): The ID of the order.
        line_id (int): The ID of the line.
        machine_top (int): The ID of the top machine.
        machine_bot (int): The ID of the bottom machine.
        tool_top (int): The ID of the top tool.
        tool_bot (int): The ID of the bottom tool.
        
        """
        #! Não é preciso estarem todos na struct


        self.id = id  
        self.client = client 
        self.type = type # para ghost é 0 
        self.final_type = final_type 
        self.order_id = order_id 
        self.delivery_day = delivery_day 
        self.machinetop = machine_top 
        self.machinebot = machine_bot 
        self.tooltop = tool_top 
        self.toolbot = tool_bot 
        self.done = False 

    def load_piece(self, line, Recipes ): 
        
        #TODO colocar no vetor de receitas a struct da peça
        Recipes.add_piece(self)
        #TODO enviar a METApeça para o tapete de entrada da linha
        #Recipes.send_piece(self, line)
        #TODO enviar a peça para o tapete de entrada da linha
        #line.load_piece(self.type)
        
        print(f"Loaded piece {self.id} into line {line.id}.")    


    #def change_tool():
        #TODO criar peça 
        print("Changed tool.")
    
       
    

   