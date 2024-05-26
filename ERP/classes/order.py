from classes.raw_order import Raw_order
import xml.etree.ElementTree as ET

class Order:
    def __init__(self, client, number, piece, quantity, due_date, late_pen, early_pen):
        self.client = client
        self.number = number
        self.piece = piece
        self.quantity = quantity
        self.due_date = due_date
        self.late_pen = late_pen
        self.early_pen = early_pen

    def __str__(self):
        return f"Client: {self.client}, Order Number: {self.number}, Piece: {self.piece}, Quantity: {self.quantity}, Due Date: {self.due_date}, Late Pen: {self.late_pen}, Early Pen: {self.early_pen}"

    @classmethod
    def parse_order(cls, order_elem, client_name):
        order_number = int(order_elem.attrib.get("Number", 0))
        workpiece = order_elem.attrib.get("WorkPiece", "")
        quantity = int(order_elem.attrib.get("Quantity", 0))
        due_date = int(order_elem.attrib.get("DueDate", 0))
        late_pen = int(order_elem.attrib.get("LatePen", 0))
        early_pen = int(order_elem.attrib.get("EarlyPen", 0))

        order = Order(client=client_name, number=order_number, piece=workpiece,
                  quantity=quantity, due_date=due_date, late_pen=late_pen,
                  early_pen=early_pen)

        return order

    @staticmethod
    def print_orders(orders):
        for order in orders:
            print(order)


    def calculate_costs(self):

        from classes.ProductionPlan import avg_prod_times
        from db import get_order, get_purchasing_plan, get_dispatch_date

        order_id = self.number

        order = get_order(order_id)

        purchasing_plan = get_purchasing_plan(order_id)
        prod_time = avg_prod_times[order.piece]
        dispatch_date = get_dispatch_date(order_id) 
        cost = order.calculate_costs(purchasing_plan, prod_time, dispatch_date)

        prod_cost = prod_time * 1       # 1€ per hour

        for plan in purchasing_plan:    #For each raw order used for this order
            raw_order = plan.raw_order
            raw_cost+= raw_order.price_pp * plan.quantity
            if plan.arrival_date > arrival_date:
                arrival_date = plan.arrival_date
            
        deprec_cost = raw_cost * (dispatch_date - arrival_date) * 1  # 1% depreciation per day
        total_cost = raw_cost + prod_cost + deprec_cost
        unit_cost = total_cost / self.quantity

        return total_cost, unit_cost
    

def parse_new_orders(new_orders_file):
    
        # Parse XML data from file
        tree = ET.parse(new_orders_file)
        root = tree.getroot()

        # Extract client data
        client_name = root.find('Client').get('NameId')

        new_orders = []
        
        for order in root.findall('Order'):
            new_order = Order.parse_order(order, client_name)
            new_orders.append(new_order)

        return new_orders