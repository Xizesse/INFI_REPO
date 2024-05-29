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

        from erp_db import get_dispatch_date, insert_costs, get_order_raw_cost_info
        from ProductionPlan import avg_prod_times

        raw_orders = get_order_raw_cost_info(self.number)       # Get the raw orders used for this order
        
        dispatch_date = get_dispatch_date(self.number) 

        prod_time = avg_prod_times[self.piece]         # Average production time for this piece
        
        prod_cost = prod_time * 1       # 1€ per second 

        total_cost = 0
        for raw_order in raw_orders:    # For each raw order used for this order

            raw_cost = raw_order['price_pp'] * raw_order['used_quantity']  # Raw cost for the pieces used from this order
            deprec_cost = raw_cost * (dispatch_date - raw_order['arrival_date']) * 1  # 1% depreciation per day per piece 
                     
            total_cost+= raw_cost + deprec_cost
        
        total_cost = total_cost + prod_cost * self.quantity    
        unit_cost = total_cost / self.quantity

        insert_costs(self.number, total_cost, unit_cost)

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


