class Piece:
    def __init__(self, number, color):
        self.number = number
        self.color = color

    def __str__(self):
        return f"Piece {self.number} is {self.color}"

    def print_color(self):
        print(self.color)


# Create instances for each piece type with a number
P1 = Piece(number=1, color="Brown")
P2 = Piece(number=2, color="Red")
P3 = Piece(number=3, color="Orange")
P4 = Piece(number=4, color="Yellow")
P5 = Piece(number=5, color="Green")
P6 = Piece(number=6, color="Blue")
P7 = Piece(number=7, color="Violet")
P8 = Piece(number=8, color="Grey")
P9 = Piece(number=9, color="White")


