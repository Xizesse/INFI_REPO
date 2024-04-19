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
    Não é preciso circular diretamente a struct, basta um indice para um array de metapeças
    Ao chegar ao tapete de uma máquina, se o ID de máquina não corresponder, segue
    Se corresponder, a máquina faz a transformação 
    A peça é enviada para o WAREHOUSE de saída
    A metapeça é ENVIADA PARA O 
    

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

class MetaPeça:
        #criar a metapeça
    def _init_(self, client, id, type, final_type, order_id, machine_id, transform):
        #! Não é preciso estarem todos na struct

        self.id = id
        self.client = client
        self.type = type
        self.final_type = final_type
        self.order_id = order_id
        self.machine_id = machine_id
        self.transform = transform

    def load_piece(piece_id):
        #TODO ir à base de dados buscar a peça
        #TODO colocar no vetor de receitas a struct da peça
        print(f"Loaded piece {piece_id}.")

    def change_tool():
        #TODO criar peça 
    
       
    

   