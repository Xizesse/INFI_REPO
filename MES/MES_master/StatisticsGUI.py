import tkinter as tk
from tkinter import ttk
import DB

class ShopFloorStatisticsWindow:
    def __init__(self, master):
        self.master = master
        
        self.window = tk.Toplevel(master)
        self.window.title("Shop Floor Statistics")
        self.window.geometry("1600x600")  # Increased window size for more space

        # Create frames for each dock with a boxed look
        self.dock_frames = []
        for i in range(4):  # Assuming 4 docks
            frame = tk.LabelFrame(self.window, text=f"Dock {i+1}", padx=5, pady=5)
            frame.grid(row=0, column=i, sticky="ew", padx=10)
            label = tk.Label(frame, text="Pieces: 0")
            label.pack()
            self.dock_frames.append(label)

        # Add a separator between docks and lines for better visual separation
        separator = tk.Frame(self.window, height=2, bd=1, relief="sunken")
        separator.grid(row=1, columnspan=6, sticky="ew", padx=20, pady=10)

        # Create frames for each line with two separate machines (top and bottom)
        self.line_frames = []
        for i in range(6):  # Assuming 6 lines
            # Line indicator
            line_label = tk.Label(self.window, text=f"Line {i+1}", font=('Helvetica', 10, 'bold'))
            line_label.grid(row=2, column=i, sticky="ew", padx=20)

            line_frame = tk.Frame(self.window)
            line_frame.grid(row=3, column=i, padx=20, pady=30)

            # Machine Top
            top_frame = tk.LabelFrame(line_frame, text=f"Machine Top", padx=10, pady=10)
            top_frame.pack(side="top", fill="x", expand=True, pady=10)  # Increased padding for separation
            top_time_label = tk.Label(top_frame, text="Total Time: 0", font=('Helvetica', 8))
            top_time_label.pack(pady=10)

            # Machine Bottom
            bottom_frame = tk.LabelFrame(line_frame, text=f"Machine Bottom", padx=10, pady=10)
            bottom_frame.pack(side="top", fill="x", expand=True, pady=10)  # Increased padding for separation
            bot_time_label = tk.Label(bottom_frame, text="Total Time: 0", font=('Helvetica', 8))
            bot_time_label.pack(pady=10)

            self.line_frames.append((top_time_label, bot_time_label))

        # Create a Treeview widget to display orders' information
        self.orders_tree = ttk.Treeview(self.window, columns=("Quantity", "Final Type", "Delivery Day", "Status", "Dispatch Conveyor"))
        self.orders_tree.heading("#0", text="Order ID")
        self.orders_tree.heading("Quantity", text="Quantity")
        self.orders_tree.heading("Final Type", text="Final Type")
        self.orders_tree.heading("Delivery Day", text="Delivery Day")
        self.orders_tree.heading("Status", text="Status")
        self.orders_tree.heading("Dispatch Conveyor", text="Dispatch Conveyor")

        # Set minimum width for columns
        self.orders_tree.column("#0", minwidth=10, width=75)
        self.orders_tree.column("Quantity", minwidth=10, width=75 )
        self.orders_tree.column("Final Type", minwidth=10, width=75)
        self.orders_tree.column("Delivery Day", minwidth=10, width=75)
        self.orders_tree.column("Status", minwidth=10, width=75)
        self.orders_tree.column("Dispatch Conveyor", minwidth=10, width=75)

        self.orders_tree.grid(row=0, column=6, rowspan=4, padx=20)

        # Fetch initial order data
        initial_orders_data = DB.get_deliveries()

        # Update the display with initial order data
        self.update_orders_data(initial_orders_data)

    def update_orders_data(self, orders_data):
        # Clear existing items in the Treeview
        self.orders_tree.delete(*self.orders_tree.get_children())
        
        # Insert new order data into the Treeview
        for i, order in enumerate(orders_data, start=1):
            self.orders_tree.insert("", "end", text=order.order_id, values=(order.quantity, order.final_type, order.delivery_day, order.status, order.dispatch_conveyor))

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    stats_window = ShopFloorStatisticsWindow(root)
    root.mainloop()
