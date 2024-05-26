import tkinter as tk
from tkinter import messagebox, Canvas
import sys
import time

class PiecesGUI:
    def __init__(self, mes, on_connect, on_disconnect):
        self.mes = mes
        self.master = mes.root
        self.day_count = 0
        self.auto_mode_active = False
        self.start_time = None

        self.master.title("Pieces GUI")
        self.master.configure(bg='lightgray')
        self.master.geometry("1300x600")

        # Top Frame for Buttons
        self.top_frame = tk.Frame(self.master, bg='lightgray')
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # Buttons
        self.connect_button = tk.Button(self.top_frame, text="Connect", command=on_connect)
        self.connect_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.disconnect_button = tk.Button(self.top_frame, text="Disconnect", command=on_disconnect)
        self.disconnect_button.pack(side=tk.LEFT, padx=10)

        # Time of the day display
        self.time_label = tk.Label(self.master, text=f"Time of the Day: {self.mes.time_of_the_day}")
        self.time_label.pack()

        # Increment day button
        self.increment_day_button = tk.Button(self.master, text="Increment Day", command=self.increment_day)
        self.increment_day_button.pack()

        self.reset_button = tk.Button(self.top_frame, text="Reset Day", command=self.reset_day_count)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        #self.mode_button = tk.Button(self.top_frame, text="Switch to Automatic Mode", command=self.toggle_mode)
        #self.mode_button.pack(side=tk.LEFT, padx=10)

        # Status Labels and Indicators
        self.status_label = tk.Label(self.top_frame, text="Disconnected", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.light_indicator = tk.Label(self.top_frame, bg="grey", width=2, height=1)
        self.light_indicator.pack(side=tk.LEFT, padx=10)

        self.day_count_label = tk.Label(self.top_frame, text=f"Day Count: {self.day_count}")
        self.day_count_label.pack(side=tk.LEFT, padx=10)

        # Bottom Frame for Canvas and other contents
        self.bottom_frame = tk.Frame(self.master, bg='lightgray')
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.orders_canvas = Canvas(self.bottom_frame, width=900, height=500)
        self.orders_canvas.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        #self.update_time_display()
        
        # Handling window closing
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_time_display(self):
        # Update the time display every second
        self.time_label.config(text=f"Time of the Day: {self.mes.time_of_the_day}")
        self.day_count_label.config(text=f"Day Count: {self.day_count}")
        #self.master.after(1000, self.update_time_display)   
        #update the day display
        
    

    def increment_day(self):
        self.mes.time_of_the_day = 0
        self.mes.app.day_count += 1
        self.mes.app.update_time_display()

    

    def update_orders_display(self):
        self.orders_canvas.delete("all")
        self.orders_canvas.config(width=1200, height=600)
        colors = ["brown", "red", "orange", "yellow", "green", "blue", "violet", "gray", "white"]
        header_height = 50
        day_height = 20
        initial_offset = 20
        column_width = 60  # Adjust width if needed
        canvas_width = self.orders_canvas.winfo_reqwidth()

        # Create headers for both warehouses
        headers = ["ID", "Type", "Final Type", "Line ID", "M Top", "M Bot", "T Top", "T Bot"]
        for i, header in enumerate(headers):
            self.orders_canvas.create_text(initial_offset*2.5 + i * column_width, header_height, text=header, anchor="nw", font=('Helvetica', 10), fill="black")

        # Draw rows for TopWarehouse and BotWarehouse
        top_pieces_list = list(self.mes.TopWarehouse.pieces.queue)
        bot_pieces_list = list(self.mes.BotWarehouse.pieces.queue)
        total_pieces = max(len(top_pieces_list), len(bot_pieces_list))
        for idx in range(total_pieces):
            if idx < len(top_pieces_list):
                piece = top_pieces_list[idx]
                y_position = header_height + day_height * (idx + 1)
                self.draw_piece_row(piece, y_position, colors, initial_offset, column_width, headers)
            if idx < len(bot_pieces_list):
                piece = bot_pieces_list[idx]
                y_position = header_height + day_height * (idx + 1)
                self.draw_piece_row(piece, y_position, colors, canvas_width//2, column_width, headers)

    def draw_piece_row(self, piece, y_position, colors, initial_offset, column_width, headers):
        
        if piece is None:
            return
        if piece.type is None:
            return
        color_index = (piece.type - 1) % len(colors)
        color = colors[color_index]
        
        if piece.id == 0:
            highlight_color = None
        elif piece.on_the_floor:
            highlight_color = "orange"
        elif piece.final_type == piece.type:
            highlight_color = "light green"
        else:
            highlight_color = "light yellow"

        # Apply highlight if not None
        if highlight_color:
            self.orders_canvas.create_rectangle(initial_offset, y_position + 4 , initial_offset + len(headers) * column_width, y_position + 19, fill=highlight_color, outline="")

        # Adjust square position to align vertically
        self.orders_canvas.create_rectangle(initial_offset + 20, y_position + 4, initial_offset + 35, y_position + 19, fill=color, outline=color)
        self.orders_canvas.create_text(initial_offset + 27.5, y_position + 11.5, text=str(piece.type), anchor="center", fill="black" if color != "white" else "gray")

        # Adjust text position for alignment
        params = [piece.id, piece.type, piece.final_type, piece.line_id, piece.machinetop, piece.machinebot, piece.tooltop, piece.toolbot]
        for i, param in enumerate(params):
            self.orders_canvas.create_text(initial_offset + 40 + i * column_width, y_position + 5, text=str(param), anchor="nw", font=('Helvetica', 8), fill="black")
   


    def update_day_timer(self):
        if self.start_time is None:
            self.start_time = time.time()
            
        elapsed_time = int(time.time() - self.start_time)
        
        self.day_timer_label.config(text=f"Time Elapsed Today: {elapsed_time} seconds")
        self.day_count_label.config(text=f"Day Count: {self.day_count}")
        
        # Proceed with the following only if in Automatic Mode
        if self.auto_mode_active:
            # Check if 60 seconds have passed
            if elapsed_time >= 60:
                # If yes, increment the day count and reset the timer
                self.increment_day_count()
                self.reset_day_timer()
            else:
                # Otherwise, schedule the next check in 1 second
                self.timer_job = self.master.after(1000, self.update_day_timer)
        else:
            # In Manual mode, we stop the timer or do not continue the auto increment loop
            if hasattr(self, 'timer_job'):
                self.master.after_cancel(self.timer_job)

    def reset_day_timer(self):
        # Only reset the start time and update the display, timer scheduling is handled by update_day_timer
        self.start_time = time.time()
        self.update_day_timer() 

    def reset_day_count(self):
        self.day_count = 0
        self.day_count_label.config(text=f"Day Count: {self.day_count}")
        self.reset_day_timer()

    def start_blinking(self):
        self.blinking = True
        self.blink()

    def stop_blinking(self):
        self.blinking = False
        self.light_indicator.config(bg="grey")  # Set to default non-blinking color

    def blink(self):
        if self.blinking:
            current_color = self.light_indicator.cget("bg")
            new_color = "green" if current_color == "grey" else "grey"
            self.light_indicator.config(bg=new_color)
            self.master.after(300, self.blink)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.master.destroy()
            sys.exit()


