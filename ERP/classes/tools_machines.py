from pieces import P1, P2, P3, P4, P5, P6, P7, P8, P9  

class Tool:
    def __init__(self, number,transformations):
        self.transformations = transformations
        self.number = number
    
    class Transformation:
            def __init__(self, start_piece, end_piece, time_taken):
                self.start_piece = start_piece
                self.end_piece = end_piece
                self.time_taken = time_taken
      
    def print_transformations(self):
        for transformation in self.transformations:
            print(f"Transform {transformation.start_piece} -> {transformation.end_piece} takes {transformation.time_taken} seconds")
        
        


class Machine:
    def __init__(self, number, tools):
        self.number = number
        self.tools = tools

# Create instances for each transformation type with start and end pieces and time taken
transformation1A = Tool.Transformation(start_piece=P1, end_piece=P3, time_taken=45)
transformation1B = Tool.Transformation(start_piece=P2, end_piece=P8, time_taken=45)

transformation2A = Tool.Transformation(start_piece=P3, end_piece=P4, time_taken=15)
transformation2B = Tool.Transformation(start_piece=P4, end_piece=P6, time_taken=25)

transformation3A = Tool.Transformation(start_piece=P3, end_piece=P4, time_taken=25)
transformation3B = Tool.Transformation(start_piece=P4, end_piece=P7, time_taken=15)

transformation4 = Tool.Transformation(start_piece=P4, end_piece=P5, time_taken=25)
transformation5 = Tool.Transformation(start_piece=P8, end_piece=P9, time_taken=45)
transformation6 = Tool.Transformation(start_piece=P8, end_piece=P7, time_taken=15)

# Create instances for each Tool type with transformations
T1 = Tool(1, {transformation1A, transformation1B})
T2 = Tool(2, {transformation2A, transformation2B})
T3 = Tool(3, {transformation3A, transformation3B})
T4 = Tool(4, {transformation4})
T5 = Tool(5, {transformation5})
T6 = Tool(6, {transformation6})

# Create instances for each Machine type with tools
M1 = Machine(1, {T1, T2, T3})
M2 = Machine(2, {T1, T2, T3})
M3 = Machine(3, {T1, T4, T5})
M4 = Machine(4, {T1, T4, T6})
