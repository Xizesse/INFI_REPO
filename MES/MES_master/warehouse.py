import queue

class Warehouse:
    def __init__(self):


        self.pieces_queue = queue.PriorityQueue()
        #TODO Barbara cenas de bases de dados
        print("Warehouse created")

    def put_piece(self, piece):
        #TODO Barbara cenas de bases de dados
        return 
    

    def get_piece(self):
        # TODO Barbara cenas de bases de dados
        return
    
    def put_piece_queue(self, piece):
        # Puts a piece in the queue
        self.pieces_queue.put(piece)

    def get_piece_queue(self):
        # Gets a piece from the queue
        if not self.pieces_queue.empty():
            return self.pieces_queue.get()
        else:
            print("No pieces left in the queue.")
            return None

    def peek_next_piece(self):
        # Peeks at the next piece to be delivered without removing it from the queue
        if not self.pieces_queue.empty():
            return self.pieces_queue.queue[0]
        else:
            print("No pieces left in the queue.")
            return None

    def is_empty(self):
        # Checks if the queue is empty
        return self.pieces_queue.empty()

