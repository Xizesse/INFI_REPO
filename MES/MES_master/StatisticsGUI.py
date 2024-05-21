import tkinter as tk
from tkinter import ttk
import DB
from warehouse import Warehouse
from Line import Line
import copy

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
        self.orders_tree.column("Dispatch Conveyor", minwidth=10, width=125)

        self.orders_tree.grid(row=0, column=6, rowspan=4, padx=20)

        # Fetch initial order data
        initial_orders_data = DB.get_deliveries()

        # Update the display with initial order data
        self.update_orders_data(initial_orders_data, Warehouse(None))

<<<<<<< HEAD

    # Function to update the status of each order
    def update_orders_data(self, orders_data, warehouse):
=======
    

    def update_orders_data(self, orders_data):
>>>>>>> b7170c89fb2d4e4751c01c9957bce1b1d6bedd5b
        # Clear existing items in the Treeview
        self.orders_tree.delete(*self.orders_tree.get_children())

        # Create a deep copy of the warehouse
        warehouse_copy = copy.deepcopy(warehouse)

        # Fetch quantities of all piece types currently in the copied warehouse
        warehouse_quantities = warehouse_copy.get_quantities()

        # Insert new order data into the Treeview with updated statuses
        for order in orders_data:
            total_available = 0
            # Get the number of pieces available in the copied warehouse for the order's final type
            for piece in list(warehouse_copy.pieces.queue):
                if piece.final_type == order.final_type:
                    total_available += 1

            # Determine the status based on the availability of the required pieces
            if total_available >= order.quantity:
                order.status = "Ready"
                # Remove the required pieces from the copied warehouse
                pieces_removed = 0
                for piece in list(warehouse_copy.pieces.queue):
                    if piece.final_type == order.final_type:
                        warehouse_copy.pieces.queue.remove(piece)
                        pieces_removed += 1
                        if pieces_removed == order.quantity:
                            break
            else:
                order.status = "Not Ready"

            # Insert the order into the Treeview with the updated status
            self.orders_tree.insert("", "end", text=order.order_id, values=(
                order.quantity, order.final_type, order.delivery_day, order.status, order.dispatch_conveyor))
            
            
    #function to update the unloading docks
    def update_dispatch_conveyor(self, orders_data, unloading_docks):
        # Initialize variables to keep track of available docks and pieces
        available_docks = list(unloading_docks.keys())
        remaining_pieces = {dock_id: 6 for dock_id in available_docks}

        # Iterate through orders marked as "Ready"
        for order in orders_data:
            if order.status == "Ready":
                pieces_to_unload = order.quantity
                dispatch_conveyor = []  # List to store dock IDs used for this order
                # Iterate until all pieces of the order are unloaded
                while pieces_to_unload > 0:
                    # Check available docks
                    if not available_docks:
                        print("No available docks for unloading.")
                        return  # Exit if no available docks

                    # Select the next available dock
                    dock_id = available_docks.pop(0)
                    pieces_to_allocate = min(remaining_pieces[dock_id], pieces_to_unload)

                    # Update remaining pieces for the dock
                    remaining_pieces[dock_id] -= pieces_to_allocate

                    # Update pieces to unload
                    pieces_to_unload -= pieces_to_allocate

                    # Add dock ID to the list of dock IDs used for this order
                    dispatch_conveyor.append(str(dock_id))

                    # Print information or perform unloading operation
                    print(f"Unloading {pieces_to_allocate} pieces of order {order.order_id} at Dock {dock_id}")

                    # Perform unloading operation here
                    # dock_id can be used to access the respective unloading dock object

                    # If the dock is full, remove it from available docks
                    if remaining_pieces[dock_id] == 0:
                        print(f"Dock {dock_id} is full.")
                        remaining_pieces.pop(dock_id)

                # Update dispatch_conveyor for this order
                order.dispatch_conveyor = ','.join(dispatch_conveyor)

                # Update orders_tree with dispatch_conveyor information for this order
                for item in self.orders_tree.get_children():
                    if self.orders_tree.item(item, "text") == order.order_id:
                        self.orders_tree.item(item, values=(
                            order.quantity, order.final_type, order.delivery_day, order.status, order.dispatch_conveyor))
                        break  # Stop searching once the order is found


        # Handle cases where there are remaining pieces but no orders
        if remaining_pieces:
            print("There are remaining pieces in some docks after unloading all orders.")





    

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    stats_window = ShopFloorStatisticsWindow(root)
    root.mainloop()
