
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

    """  
    def calculate_costs():
        total_cost = raw_cost + prod_cost + deprec_cost
    """