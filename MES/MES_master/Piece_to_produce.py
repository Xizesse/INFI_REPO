class Piece_to_produce:
    def __init__(self, order_id, final_type, delivery_day):
        """
        Args:
        order_id (int): The ID of the order.
        final_type (int): The final type of the piece.
        delivery_day (int): The day the piece is due.
        """
        self.order_id = order_id
        self.final_type = final_type
        self.delivery_day = delivery_day
    
    def __str__(self):
        return f"Order ID: {self.order_id}, Final Type: {self.final_type}"
