import tkinter as tk
from tkinter import ttk
import DB
from warehouse import Warehouse
from Line import Line
from Piece import Piece

class ShopFloorStatisticsWindow:
    def __init__(self, master, mes):
        self.master = master
        self.lines = mes.lines_machines
        
        self.window = tk.Toplevel(master)
        self.window.title("Shop Floor Statistics")
        self.window.geometry("1600x800")  # Increased height to accommodate new sections

        self.dock_frames = []
        for i in range(4):  
            frame = tk.LabelFrame(self.window, text=f"Dock {i+1}", padx=5, pady=5)
            frame.grid(row=0, column=i, sticky="ew", padx=10)
            label = tk.Label(frame, text="Pieces: 0")
            label.pack()
            self.dock_frames.append(label)

        
        separator = tk.Frame(self.window, height=2, bd=1, relief="sunken")
        separator.grid(row=1, columnspan=6, sticky="ew", padx=20, pady=10)

       
        self.line_frames = []
        for i in range(6):  
            line_label = tk.Label(self.window, text=f"Line {i+1}", font=('Helvetica', 10, 'bold'))
            line_label.grid(row=2, column=i, sticky="ew", padx=20)

            line_frame = tk.Frame(self.window)
            line_frame.grid(row=3, column=i, padx=20, pady=30)

            top_frame = tk.LabelFrame(line_frame, text=f"Machine Top", padx=10, pady=10)
            top_frame.pack(side="top", fill="x", expand=True, pady=10)  
            top_time_label = tk.Label(top_frame, text="Total Time: 0", font=('Helvetica', 8))
            top_time_label.pack(pady=10)
            top_tool_label = tk.Label(top_frame, text="Current Tool: 0", font=('Helvetica', 8))  # New label for top tool
            top_tool_label.pack(pady=5)

            bottom_frame = tk.LabelFrame(line_frame, text=f"Machine Bottom", padx=10, pady=10)
            bottom_frame.pack(side="top", fill="x", expand=True, pady=10)  
            bot_time_label = tk.Label(bottom_frame, text="Total Time: 0", font=('Helvetica', 8))
            bot_time_label.pack(pady=10)
            bot_tool_label = tk.Label(bottom_frame, text="Current Tool: 0", font=('Helvetica', 8))  # New label for bottom tool
            bot_tool_label.pack(pady=5)
            
            self.line_frames.append((top_frame, bottom_frame, top_time_label, bot_time_label, top_tool_label, bot_tool_label))

        self.orders_tree = ttk.Treeview(self.window, columns=("Quantity", "Final Type", "Delivery Day", "Status", "Dispatch Conveyor"))
        self.orders_tree.heading("#0", text="Order ID")
        self.orders_tree.heading("Quantity", text="Quantity")
        self.orders_tree.heading("Final Type", text="Final Type")
        self.orders_tree.heading("Delivery Day", text="Delivery Day")
        self.orders_tree.heading("Status", text="Status")
        self.orders_tree.heading("Dispatch Conveyor", text="Dispatch Conveyor")

        self.orders_tree.column("#0", minwidth=10, width=75)
        self.orders_tree.column("Quantity", minwidth=10, width=75 )
        self.orders_tree.column("Final Type", minwidth=10, width=75)
        self.orders_tree.column("Delivery Day", minwidth=10, width=75)
        self.orders_tree.column("Status", minwidth=10, width=75)
        self.orders_tree.column("Dispatch Conveyor", minwidth=10, width=125)

        self.orders_tree.grid(row=0, column=6, rowspan=4, padx=20)

        # Add new sections for purchasing and production queues
        self.purchasing_label = tk.LabelFrame(self.window, text="Purchasing Queue", padx=10, pady=10)
        self.purchasing_label.grid(row=5, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        self.purchasing_text = tk.Text(self.purchasing_label, height=10, width=50)
        self.purchasing_text.pack()

        self.production_label = tk.LabelFrame(self.window, text="Production Queue", padx=10, pady=10)
        self.production_label.grid(row=5, column=3, columnspan=3, sticky="ew", padx=10, pady=10)
        self.production_text = tk.Text(self.production_label, height=10, width=50)
        self.production_text.pack()

        #self.update_machine_statuses()

    def update_orders_data(self, orders_data):
        try:
            self.orders_tree.delete(*self.orders_tree.get_children())
        except tk.TclError:
            return

        for order in orders_data:
            self.orders_tree.insert("", "end", text=order.order_id, values=(
                order.quantity, order.final_type, order.delivery_day, order.status, order.dispatch_conveyor))

    def update_machine_statuses(self):
        for i, line in self.lines.items():
            top_frame, bottom_frame, top_time_label, bot_time_label, top_tool_label, bot_tool_label = self.line_frames[i - 1]
            if line.isTopBusy():
                top_frame.config(bg="green")
            else:
                top_frame.config(bg="SystemButtonFace")
                
                
            if line.isBotBusy():
                bottom_frame.config(bg="green")
                
            else:
                bottom_frame.config(bg="SystemButtonFace")
                
                
            bot_tool_label.config(text=f"Current Tool: {line.current_tool_bot}")
            top_tool_label.config(text=f"Current Tool: {line.current_tool_top}")

            line.get_machine_time()
            top_time_label.config(text=f"Total Time: {line.total_time_top/1000} s")
            bot_time_label.config(text=f"Total Time: {line.total_time_bot/1000} s")

    def update_machineTime(self, line_id, top_time, bot_time):
        if 0 <= line_id - 1 < len(self.line_frames):
            top_time_label = self.line_frames[line_id - 1][2]
            bot_time_label = self.line_frames[line_id - 1][3]
            
            top_time_label.config(text=f"Total Time: {top_time/1000} s")
            bot_time_label.config(text=f"Total Time: {bot_time/1000} s")
        

    def update_purchasing_queue(self, purchases):
        self.purchasing_text.delete(1.0, tk.END)
        self.purchasing_text.insert(tk.END, "\n".join(str(p) for p in purchases))

    def update_production_queue(self, production_orders):
        self.production_text.delete(1.0, tk.END)
        self.production_text.insert(tk.END, "\n".join(str(p.final_type) for p in production_orders))

if __name__ == "__main__":
    root = tk.Tk()
    stats_window = ShopFloorStatisticsWindow(root, None)
    root.mainloop()
