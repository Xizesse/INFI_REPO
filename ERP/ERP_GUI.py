import tkinter as tk
from tkinter import ttk
import db_config


class ShopFloorStatisticsWindow:
    def __init__(self, master):
        self.master = master
        
        self.window = tk.Toplevel(master)
        self.window.title("Interface ERP - Shop Floor Statistics")
        self.window.geometry("1600x1600")  # Increased window size for more space
        
        # Create a label to display the current date
        current_date = db_config.get_current_date()  # Get the current date from db_config

        self.current_date_label = tk.Label(self.window, text=f"Current Date: {current_date}", font=("Arial", 12, "bold"))
        self.current_date_label.grid(row=0, column=0, padx=10)

        #update the current date
        self.update_current_date()

        # Create first Treeview widget to display "orders information"
        self.orders_tree = ttk.Treeview(self.window, columns=("number","Quantity", "Final Type", "Delivery Day", "late_pen", "early_pen"))
        self.orders_tree.heading("#0", text="Client")
        self.orders_tree.heading("number", text="Order ID")
        self.orders_tree.heading("Quantity", text="Quantity")
        self.orders_tree.heading("Final Type", text="Final Type")
        self.orders_tree.heading("Delivery Day", text="Delivery Day")
        self.orders_tree.heading("late_pen", text="Late Penalty")
        self.orders_tree.heading("early_pen", text="Early Penalty")

        # Set minimum width for columns
        self.orders_tree.column("#0", minwidth=10, width=80)
        self.orders_tree.column("number", minwidth=10, width=75)
        self.orders_tree.column("Quantity", minwidth=10, width=75 )
        self.orders_tree.column("Final Type", minwidth=10, width=75)
        self.orders_tree.column("Delivery Day", minwidth=10, width=75)
        self.orders_tree.column("late_pen", minwidth=10, width=75)
        self.orders_tree.column("early_pen", minwidth=10, width=75)

        self.orders_tree.grid(row=0, column=6, padx=20, pady=10)
        
        # Fetch initial order data
        initial_orders_data = db_config.get_orders()

        # Update the display with initial order data
        self.update_orders_data(initial_orders_data)

        # Create a second Treeview widget to display "production_plan"
        self.second_table_tree = ttk.Treeview(self.window, columns=("P5_quantity", "P6_quantity", "P7_quantity", "P9_quantity"))
        self.second_table_tree.heading("#0", text="Start_date")
        self.second_table_tree.heading("P5_quantity", text="P5 Quantity")
        self.second_table_tree.heading("P6_quantity", text="P6 Quantity")
        self.second_table_tree.heading("P7_quantity", text="P7 Quantity")
        self.second_table_tree.heading("P9_quantity", text="P9 Quantity")

        # Set minimum width for columns
        self.second_table_tree.column("#0", minwidth=10, width=80)
        self.second_table_tree.column("P5_quantity", minwidth=10, width=75)
        self.second_table_tree.column("P6_quantity", minwidth=10, width=75)
        self.second_table_tree.column("P7_quantity", minwidth=10, width=75)
        self.second_table_tree.column("P9_quantity", minwidth=10, width=75)

        self.second_table_tree.grid(row=0, column=1, padx=20, pady=10)

        # Fetch initial production plan data
        initial_production_plan_data = db_config.get_production_plan()

        # Update the display with initial production plan data
        self.update_production_plan_data(initial_production_plan_data)

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

        # Fetch initial purchasing plan data
        initial_purchasing_plan_data = db_config.get_purchasing_plan()

        # Update the display with initial purchasing plan data
        self.update_purchasing_plan_data()

        # Create a title label for the first table
        self.orders_title_label = tk.Label(self.window, text="Orders Table", font=("Arial", 12, "bold"))
        self.orders_title_label.grid(row=10, column=6, padx=10)

        # Create a title label for the second table
        self.second_table_title_label = tk.Label(self.window, text="Production_Plan Table", font=("Arial", 12, "bold"))
        self.second_table_title_label.grid(row=10, column=1, padx=10)

        # Create a title label for the third table
        self.third_table_title_label = tk.Label(self.window, text="Purchasing_Plan Table", font=("Arial", 12, "bold"))
        self.third_table_title_label.grid(row=10, column=2, padx=10)

        


    def update_orders_data(self, orders_data):
        # Clear existing items in the Treeview
        self.orders_tree.delete(*self.orders_tree.get_children())
        
        # Insert new order data into the Treeview
        for i, order in enumerate(orders_data, start=1):
            self.orders_tree.insert("", "end", text=order.client, values=(order.order_id, order.quantity, order.final_type, order.delivery_day, order.late_pen, order.early_pen))

    def update_production_plan_data(self, initial_production_plan_data):
        production_plan = db_config.get_production_plan()

        for plan_entry in production_plan:
            self.second_table_tree.insert("", "end", text=plan_entry['start_date'], values=(plan_entry['p5_quantity'], plan_entry['p6_quantity'], plan_entry['p7_quantity'], plan_entry['p9_quantity']))

    def update_purchasing_plan_data(self):
        purchasing_plan = db_config.get_purchasing_plan()  # Assuming this returns a list of dictionaries

        for plan_entry in purchasing_plan:
            self.third_table_tree.insert("", "end", text=plan_entry['arrival_date'], values=(plan_entry['p1_quantity'], plan_entry['p2_quantity']))
  
    def update_current_date(self):
        # This function can be used later if your implementation involves retrieving the date dynamically
        current_date = db_config.get_current_date()
        self.current_date_label.config(text=f"Current Date: {current_date}")

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    stats_window = ShopFloorStatisticsWindow(root)
    root.mainloop()