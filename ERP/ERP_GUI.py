import tkinter as tk
from tkinter import ttk
import db_config 
import classes.Order
import classes.ProductionPlan
import classes.PurchasingPlan


class ShopFloorStatisticsWindow:
    def __init__(self, master):

        self.window = master
        self.window.title("Interface ERP - Statistics")
        self.window.geometry("900x650")  # Increased window size for more space

        self.initialize_tables()

        #!UPDATES
        # Update the data in the Treeview widgets
        self.update_values()

    def initialize_tables(self):
        #!ORDERS TABLE
        # Orders Table Title
        self.orders_title_label = tk.Label(self.window, text="Orders Table", font=("Arial", 12, "bold"))
        self.orders_title_label.grid(row=1, column=1, padx=5, pady=(10, 0), sticky='n')

        # Orders Table
        self.orders_tree = ttk.Treeview(self.window, columns=("number", "Quantity", "piece", "due_date", "late_pen", "early_pen"))
        self.orders_tree.heading("#0", text="Client")
        self.orders_tree.heading("number", text="Number")
        self.orders_tree.heading("Quantity", text="Quantity")
        self.orders_tree.heading("piece", text="Piece")
        self.orders_tree.heading("due_date", text="Due_date")
        self.orders_tree.heading("late_pen", text="Late Penalty")
        self.orders_tree.heading("early_pen", text="Early Penalty")

        order_col_width = 60
        # Set uniform width for columns
        self.orders_tree.column("#0", minwidth=10, width=order_col_width+15)
        self.orders_tree.column("number", minwidth=10, width=order_col_width)
        self.orders_tree.column("Quantity", minwidth=10, width=order_col_width)
        self.orders_tree.column("piece", minwidth=10, width=order_col_width)
        self.orders_tree.column("due_date", minwidth=10, width=order_col_width)
        self.orders_tree.column("late_pen", minwidth=10, width=order_col_width+15)
        self.orders_tree.column("early_pen", minwidth=10, width=order_col_width+15)

        self.orders_tree.grid(row=2, column=1, padx=5, pady=5, sticky='n')

        #!PRODUCTION PLAN
        # Production Plan Title
        self.prod_plan_title_label = tk.Label(self.window, text="Production Plan", font=("Arial", 12, "bold"))
        self.prod_plan_title_label.grid(row=1, column=2, padx=5, pady=(10, 0), sticky='n')

        # Production Plan Table
        self.prod_plan_tree = ttk.Treeview(self.window, columns=("Order_id"))
        self.prod_plan_tree.heading("#0", text="Start_date")
        self.prod_plan_tree.heading("Order_id", text="Order_id")

        # Set uniform width for columns
        self.prod_plan_tree.column("#0", minwidth=10, width=80)
        self.prod_plan_tree.column("Order_id", minwidth=10, width=80)

        self.prod_plan_tree.grid(row=2, column=2, padx=5, pady=5, sticky='n')

        #!PURCHASING PLAN
        # Purchasing Plan Title
        self.purchase_plan_title_label = tk.Label(self.window, text="Purchasing Plan", font=("Arial", 12, "bold"))
        self.purchase_plan_title_label.grid(row=2, column=1, padx=5, pady=(250, 0), sticky='n')

        # Purchasing Plan Table
        self.purchase_plan_tree = ttk.Treeview(self.window, columns=("P1_quantity", "P2_quantity"))
        self.purchase_plan_tree.heading("#0", text="Arrival_date")
        self.purchase_plan_tree.heading("P1_quantity", text="P1_quantity")
        self.purchase_plan_tree.heading("P2_quantity", text="P2_quantity")

        # Set uniform width for columns
        self.purchase_plan_tree.column("#0", minwidth=10, width=80)
        self.purchase_plan_tree.column("P1_quantity", minwidth=10, width=80)
        self.purchase_plan_tree.column("P2_quantity", minwidth=10, width=80)

        self.purchase_plan_tree.grid(row=3, column=1, padx=5, pady=10, sticky='n')

        #!PROD QUANTITIES
        # Production Quantities Title
        self.prod_quantities_title_label = tk.Label(self.window, text="Production Quantities Table", font=("Arial", 12, "bold"))
        self.prod_quantities_title_label.grid(row=2, column=2, padx=5, pady=(250, 0), sticky='n')

        # Production Quantities Table
        self.prod_quantities_tree = ttk.Treeview(self.window, columns=("P5_quantity", "P6_quantity", "P7_quantity", "P9_quantity"))
        self.prod_quantities_tree.heading("#0", text="Start_date")
        self.prod_quantities_tree.heading("P5_quantity", text="P5_quantity")
        self.prod_quantities_tree.heading("P6_quantity", text="P6_quantity")
        self.prod_quantities_tree.heading("P7_quantity", text="P7_quantity")
        self.prod_quantities_tree.heading("P9_quantity", text="P9_quantity")

        # Set uniform width for columns
        self.prod_quantities_tree.column("#0", minwidth=10, width=80)
        self.prod_quantities_tree.column("P5_quantity", minwidth=10, width=80)
        self.prod_quantities_tree.column("P6_quantity", minwidth=10, width=80)
        self.prod_quantities_tree.column("P7_quantity", minwidth=10, width=80)
        self.prod_quantities_tree.column("P9_quantity", minwidth=10, width=80)

        self.prod_quantities_tree.grid(row=3, column=2, padx=5, pady=5, sticky='n')

        #!CURRENT DATE
        current_date = 0    # Placeholder value
        self.current_date_label = tk.Label(self.window, text=f"Current Date: {current_date}", font=("Arial", 15, "bold"))
        self.current_date_label.grid(row=0, column=1, padx=5, columnspan=2, sticky='n')

    
    def update_values(self):

        db_config.connect_to_db() 

        self.update_orders_data()
        self.update_production_plan_data()
        self.update_purchasing_plan_data()
        self.update_prod_quantities_data()
        
        # Update the current date label
        current_date = db_config.get_current_date()  
        self.current_date_label = tk.Label(self.window, text=f"Current Date: {current_date}", font=("Arial", 12, "bold"))
        self.current_date_label.config(text=f"Current Date: {current_date}")

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
        self.prod_plan_tree.delete(*self.prod_plan_tree.get_children())

        production_plan = db_config.get_production_plan()

        for plan_entry in production_plan:
            self.prod_plan_tree.insert("", "end", text=plan_entry.start_date, values=(plan_entry.order_id))

    def update_prod_quantities_data(self):
        # Clear existing items in the Treeview
        self.prod_quantities_tree.delete(*self.prod_quantities_tree.get_children())

        prod_quantities = db_config.get_prod_quantities()

        for plan_entry in prod_quantities:
            self.prod_quantities_tree.insert("", "end", text=plan_entry.start_date, values=(plan_entry.p5_quantity, plan_entry.p6_quantity, plan_entry.p7_quantity, plan_entry.p9_quantity))

    def update_purchasing_plan_data(self):
        # Clear existing items in the Treeview
        self.purchase_plan_tree.delete(*self.purchase_plan_tree.get_children())
        purchasing_plan = db_config.get_purchasing_plan()  

        for plan_entry in purchasing_plan:
            self.purchase_plan_tree.insert("", "end", text=plan_entry.arrival_date, values=(plan_entry.p1_quantity, plan_entry.p2_quantity))

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



