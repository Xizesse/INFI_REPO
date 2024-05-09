import tkinter as tk
from tkinter import messagebox, Canvas
import sys

class PiecesGUI:
    def __init__(self, mes, on_connect, on_disconnect):
        self.mes = mes
        self.master = mes.root
        self.really_count = 0
        self.day_count = 0
        self.order_queue = None
        self.master.title("MES Client Interface")
        self.master.configure(bg='lightgray')
        self.master.geometry("1300x600")

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
        self.orders_canvas = Canvas(self.master, width=900, height=500)  # Adjust size as needed
        self.orders_canvas.pack()

        # Window closing event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    """ def update_orders_display(self):
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
                self.orders_canvas.create_text(x_position + 20, y_position + 5, text=f"{completed}/{total}", anchor="nw") """
    def update_orders_display(self):
        self.orders_canvas.delete("all")  # Clear previous contents
        self.orders_canvas.config(width=1200, height=600)  # Adjusted to fit smaller screens
        colors = ["brown", "red", "orange", "yellow", "green", "blue", "violet", "gray", "white"]
        header_height = 50
        day_height = 20
        initial_offset = 20  # Reduced offset for compactness
        param_offset = 20    # Reduced distance to ID
        column_width = 50    # Narrower columns to fit more content
        middle_space = 00   # Less space between warehouses to save space
        canvas_width = self.orders_canvas.winfo_reqwidth()

        headers = ["ID", "Type", "Final Type", "Line ID", "M Top", "M Bot", "T Top", "T Bot"]
        for i, header in enumerate(headers):
            # Left side headers (Top Warehouse)
            self.orders_canvas.create_text(initial_offset + param_offset + i * column_width, header_height, text=header, anchor="nw", font=('Helvetica', 10), fill="black")
            # Right side headers (Bot Warehouse)
            self.orders_canvas.create_text(canvas_width//2 + middle_space + initial_offset + param_offset + i * column_width, header_height, text=header, anchor="nw", font=('Helvetica', 10), fill="black")

        # Titles for each warehouse shifted to the right
        self.orders_canvas.create_text(initial_offset + 50, 20, text="Top Warehouse", font=('Helvetica', 14, 'bold'), fill="black")  # Pushed to the right
        self.orders_canvas.create_text(canvas_width//2 + middle_space + initial_offset + 50, 20, text="Bot Warehouse", font=('Helvetica', 14, 'bold'), fill="black")  # Pushed to the right

        # Draw pieces for TopWarehouse
        top_pieces_list = list(self.mes.TopWarehouse.pieces.queue)
        for idx, piece in enumerate(top_pieces_list):
            y_position = header_height + day_height * (idx + 2)
            self.draw_piece_row(piece, y_position, colors, initial_offset, param_offset, column_width, headers)

        # Draw pieces for BotWarehouse
        bot_pieces_list = list(self.mes.BotWarehouse.pieces.queue)
        for idx, piece in enumerate(bot_pieces_list):
            y_position = header_height + day_height * (idx + 2)
            self.draw_piece_row(piece, y_position, colors, canvas_width//2 + middle_space + initial_offset, param_offset, column_width, headers)
                                
    def draw_piece_row(self, piece, y_position, colors, initial_offset, param_offset, column_width, headers):
        color_index = (piece.type - 1) % len(colors)
        color = colors[color_index]
        highlight_color = "light yellow" if piece.final_type != piece.type else "light green"

        adjusted_y_position = y_position + 0  
        square_y_position = y_position + 0    

        # Highlight background, adjusted down
        if piece.id != 0:
            self.orders_canvas.create_rectangle(initial_offset, adjusted_y_position - 5, initial_offset + param_offset + (len(headers) - 1) * column_width, adjusted_y_position + 15, fill=highlight_color, outline="")

        # Draw the piece type color square, adjusted down
        self.orders_canvas.create_rectangle(initial_offset + 20, square_y_position, initial_offset + 35, square_y_position + 15, fill=color, outline=color)
        self.orders_canvas.create_text(initial_offset + 27.5, square_y_position + 7.5, text=str(piece.type), anchor="center", fill="black" if color != "white" else "gray")

        # Text parameters
        for i, param in enumerate([str(piece.id), str(piece.type), str(piece.final_type), str(piece.line_id), str(piece.machinetop), str(piece.machinebot), str(piece.tooltop), str(piece.toolbot)]):
            self.orders_canvas.create_text(initial_offset + 40 + i * column_width, adjusted_y_position + 5, text=param, anchor="nw", font=('Helvetica', 8), fill="black")

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



