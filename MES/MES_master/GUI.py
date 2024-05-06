import tkinter as tk
from tkinter import messagebox, Canvas
import sys

class OPCUAClientGUI:
    def __init__(self, mes, on_connect, on_disconnect):
        self.mes = mes
        self.master = mes.root
        self.really_count = 0
        self.day_count = 0
        self.order_queue = None
        self.master.title("MES Client Interface")
        self.master.configure(bg='lightgray')
        self.master.geometry("900x600")

        # GUI elements
        self.connect_button = tk.Button(self.master, text="Connect", command=on_connect)
        self.connect_button.place(x=50, y=200)

        self.disconnect_button = tk.Button(self.master, text="Disconnect", command=on_disconnect)
        self.disconnect_button.place(x=50, y=230)

        self.status_label = tk.Label(self.master, text="Disconnected", fg="red")
        self.status_label.place(x=50, y=260)

        self.light_indicator = tk.Label(self.master, bg="grey", width=2, height=1)
        self.light_indicator.place(x=50, y=290)
        self.blinking = False

        # Day Count
        self.day_count_label = tk.Label(self.master, text=f"Day Count: {self.day_count}")
        self.day_count_label.pack()

        # Increment/Reset buttons
        self.increment_button = tk.Button(self.master, text="Increment Day", command=self.increment_day_count)
        self.increment_button.pack()

        self.reset_button = tk.Button(self.master, text="Reset Day", command=self.reset_day_count)
        self.reset_button.pack()

        # Canvas for drawing orders
        self.orders_canvas = Canvas(self.master, width=600, height=500)  # Adjust size as needed
        self.orders_canvas.pack()

        # Window closing event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_orders_display(self):
        self.orders_canvas.delete("all")  
        colors = ["brown", "red", "orange", "yellow", "green", "blue", "violet", "gray", "white"]  # Colors for 9 piece types
        header_height = 20  
        day_height = 20 
        piece_width = 50  
        initial_offset = 50  

        
        for piece_type in range(9):  
            x_position = initial_offset + piece_width * (piece_type + 0.5)  
            color = colors[piece_type % len(colors)]
            self.orders_canvas.create_rectangle(x_position, 0, x_position + 15, 15, fill=color, outline=color)
            self.orders_canvas.create_text(x_position + 7.5, 0, text=str(piece_type), anchor="n", fill="black" if color != "white" else "gray")

       
        for i in range(12):  # Display data for 12 days
            day = self.day_count + i  
            y_position = header_height + day_height * i  
            self.orders_canvas.create_text(10, y_position + 5, text=f"Day {day}:", anchor="nw")
            for piece_type in range(9):
                completed, total = self.mes.TopWarehouse.count_pieces_by_type_and_day(piece_type, day)
                x_position = initial_offset + piece_width * piece_type  
                self.orders_canvas.create_text(x_position + 20, y_position + 5, text=f"{completed}/{total}", anchor="nw")


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.master.destroy()
            sys.exit()

    def increment_day_count(self):
        self.day_count += 1
        self.day_count_label.config(text=f"Day Count: {self.day_count}")

    def reset_day_count(self):
        self.day_count = 0
        self.day_count_label.config(text=f"Day Count: {self.day_count}")

    def blink(self):
        if self.blinking:
            current_color = self.light_indicator.cget("bg")
            new_color = "green" if current_color == "grey" else "grey"
            self.light_indicator.config(bg=new_color)
            self.master.after(300, self.blink)
