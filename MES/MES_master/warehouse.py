import queue
from Piece import Piece
import copy

class Warehouse:
    def __init__(self, client):
        self.client = client
        self.pieces = queue.Queue() 
        print("Warehouse created")

    def count_pieces_by_type_and_day(self, piece_type, day):
        total = 0
        completed = 0
        for piece in list(self.pieces.queue):
            if piece.final_type == piece_type and piece.delivery_day == day:
                total += 1
                if piece.type == piece.final_type:
                    completed += 1
        return total

    def put_piece_queue(self, piece):
        # Puts a piece in the queue
        self.pieces.put(piece)

    def get_piece_queue(self):
        # Gets a piece from the queue
        if not self.pieces.empty():
            return self.pieces.get()
        else:
            print("No pieces left in the queue.")
            return None
        
    def peek_piece_queue(self):
        if not self.pieces.empty():
            return self.pieces.queue[0]
        else:
            print("No pieces to peek at in the queue.")
            return None

    def is_empty(self):
        # Checks if the queue is empty
        return self.pieces.empty()
    
    def set_simulation_warehouse(self):
        print("Setting up simulation warehouse")
        piece1 = Piece(self.client, 1, 1, 5, 9, 10, False, False, 0, 0)
        self.put_piece_queue(piece1)
        piece2 = Piece(self.client, 2, 1, 5, 9, 10, False, False, 0, 0)
        self.put_piece_queue(piece2)
        piece3 = Piece(self.client, 3, 1, 6, 9, 11, False, False, 0, 0)
        self.put_piece_queue(piece3)
        piece4 = Piece(self.client, 3, 1, 6, 9, 11, False, False, 0, 0)
        self.put_piece_queue(piece4)
    
    def sort_queue_by_delivery_day(self):
        # Sorts the queue by delivery day, but the id 0 is always last
        sorted_queue = sorted(list(self.pieces.queue), key=lambda x: (x.delivery_day, x.id))
        self.pieces.queue.clear()
        for piece in sorted_queue:
            if piece.id != 0:
                self.pieces.put(piece)
        for piece in sorted_queue:
            if piece.id == 0:
                self.pieces.put(piece)

    
    def __deepcopy__(self, memo):
        # Create a new instance of Warehouse
        new_warehouse = Warehouse(self.client)
        # Deepcopy each piece and add it to the new queue
        for piece in list(self.pieces.queue):
            new_piece = copy.deepcopy(piece, memo)
            new_warehouse.put_piece_queue(new_piece)
        return new_warehouse
    
