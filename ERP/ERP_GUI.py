import tkinter as tk
from tkinter import ttk
import db_config 
import classes.Order
import classes.ProductionPlan
import classes.PurchasingPlan


class ShopFloorStatisticsWindow:
    def __init__(self, master):

        self.window = master

        self.window.title("Interface ERP - Shop Floor Statistics")
        self.window.geometry("1400x500")  # Increased window size for more space

        # Create first Treeview widget to display "orders information"
        self.orders_tree = ttk.Treeview(self.window, columns=("number","Quantity", "piece", "due_date", "late_pen", "early_pen"))
        self.orders_tree.heading("#0", text="Client")
        self.orders_tree.heading("number", text="Number")
        self.orders_tree.heading("Quantity", text="Quantity")
        self.orders_tree.heading("piece", text="Piece")
        self.orders_tree.heading("due_date", text="Due_date")
        self.orders_tree.heading("late_pen", text="Late Penalty")
        self.orders_tree.heading("early_pen", text="Early Penalty")

        # Set minimum width for columns
        self.orders_tree.column("#0", minwidth=10, width=80)
        self.orders_tree.column("number", minwidth=10, width=75)
        self.orders_tree.column("Quantity", minwidth=10, width=75 )
        self.orders_tree.column("piece", minwidth=10, width=75)
        self.orders_tree.column("due_date", minwidth=10, width=75)
        self.orders_tree.column("late_pen", minwidth=10, width=75)
        self.orders_tree.column("early_pen", minwidth=10, width=75)

        self.orders_tree.grid(row=0, column=6, padx=20, pady=10)

        # Create a second Treeview widget to display "production_plan"
        self.second_table_tree = ttk.Treeview(self.window, columns=("Order_id", "Workpiece", "Quantity"))
        self.second_table_tree.heading("#0", text="Start_date")
        self.second_table_tree.heading("Order_id", text="Order_id")
        self.second_table_tree.heading("Workpiece", text="Workpiece")
        self.second_table_tree.heading("Quantity", text="Quantity")

        # Set minimum width for columns
        self.second_table_tree.column("#0", minwidth=10, width=80)
        self.second_table_tree.column("Order_id", minwidth=10, width=75)
        self.second_table_tree.column("Workpiece", minwidth=10, width=75)
        self.second_table_tree.column("Quantity", minwidth=10, width=75)

        self.second_table_tree.grid(row=0, column=1, padx=20, pady=10)

        # Create a third Treeview widget to display "purchasing_plan"
        self.third_table_tree = ttk.Treeview(self.window, columns=("P1_quantity", "P2_quantity"))
        self.third_table_tree.heading("#0", text="Arrival_date")
        self.third_table_tree.heading("P1_quantity", text="P1_quantity")
        self.third_table_tree.heading("P2_quantity", text="P2_quantity")

        # Set minimum width for columns
        self.third_table_tree.column("#0", minwidth=10, width=80)
        self.third_table_tree.column("P1_quantity", minwidth=10, width=75)
        self.third_table_tree.column("P2_quantity", minwidth=10, width=75)

        self.third_table_tree.grid(row=0, column=2, padx=20, pady=10)

        # Create a title label for the first table
        self.orders_title_label = tk.Label(self.window, text="Orders Table", font=("Arial", 12, "bold"))
        self.orders_title_label.grid(row=10, column=6, padx=10)

        # Create a title label for the second table
        self.second_table_title_label = tk.Label(self.window, text="Production Plan Table", font=("Arial", 12, "bold"))
        self.second_table_title_label.grid(row=10, column=1, padx=10)

        # Create a title label for the third table
        self.third_table_title_label = tk.Label(self.window, text="Purchasing Plan Table", font=("Arial", 12, "bold"))
        self.third_table_title_label.grid(row=10, column=2, padx=10)
        
        # Update the data in the Treeview widgets
        self.update_values()


    def update_values(self):

        db_config.connect_to_db() 

        self.update_orders_data()
        self.update_production_plan_data()
        self.update_purchasing_plan_data()
        
        # Update the current date label
        current_date = db_config.get_current_date()  
        self.current_date_label = tk.Label(self.window, text=f"Current Date: {current_date}", font=("Arial", 12, "bold"))
        self.current_date_label.grid(row=0, column=0, padx=10)

        db_config.close_db_connection() 
        
        self.window.after(5*1000, self.update_values)  # Update every 5 seconds    

    def update_orders_data(self):
        # Clear existing items in the Treeview
        self.orders_tree.delete(*self.orders_tree.get_children())
        
        # Fetch initial order data
        orders_data = db_config.get_orders()

        # Insert new order data into the Treeview
        for i, order in enumerate(orders_data, start=1):
            self.orders_tree.insert("", "end", text=order.client, values=(order.number, order.quantity, order.piece, order.due_date, order.late_pen, order.early_pen))

    def update_production_plan_data(self):
        # Clear existing items in the Treeview
        self.second_table_tree.delete(*self.second_table_tree.get_children())

        production_plan = db_config.get_production_plan()

        for plan_entry in production_plan:
            self.second_table_tree.insert("", "end", text=plan_entry.start_date, values=(plan_entry.order_id, plan_entry.workpiece, plan_entry.quantity))

    def update_purchasing_plan_data(self):
        # Clear existing items in the Treeview
        self.third_table_tree.delete(*self.third_table_tree.get_children())
        purchasing_plan = db_config.get_purchasing_plan()  

        for plan_entry in purchasing_plan:
            self.third_table_tree.insert("", "end", text=plan_entry.arrival_date, values=(plan_entry.p1_quantity, plan_entry.p2_quantity))

    def update_current_date(self):
        # This function can be used later if your implementation involves retrieving the date dynamically
        current_date = db_config.get_current_date()
        self.current_date_label.config(text=f"Current Date: {current_date}")


def erp_gui():

    root = tk.Tk()
    ShopFloorStatisticsWindow(root)
    root.mainloop()

if __name__ == "__main__":

    erp_gui()



