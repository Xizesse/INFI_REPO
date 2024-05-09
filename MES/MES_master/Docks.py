class LoadingDock:
    def __init__(self, mes, piece_type):
        self.mes = mes
        self.busy = False
        self.type = piece_type

    def load_piece(self, piece):
        """Load a piece onto the dock. Assumes the dock is not busy."""
        if not self.is_busy():
            self.current_piece = piece
            print(f"Piece loaded onto the dock: {piece}")
        else:
            print("Failed to load piece: Dock is busy.")

    def is_busy(self):
        """Check if the dock is busy (i.e., if there's a piece currently on the dock)."""
        return self.busy 
    
    def has_piece_ready(self):
        """Check if the dock has a piece ready to be unloaded."""
        return False

    def unload_dock(self):
        """Remove the piece from the dock and return it."""
        if self.is_busy():
            
            return 
        else:
            print("No piece to unload: Dock is not busy.")
            return None
        
class UnloadingDock:
    def __init__(self, mes):
        self.mes = mes
        self.busy = False


    def load_piece(self, piece):
        """Load a piece onto the dock. Assumes the dock is not busy."""
        if not self.is_busy():
            self.current_piece = piece
            print(f"Piece loaded onto the dock: {piece}")
        else:
            print("Failed to load piece: Dock is busy.")

    def is_busy(self):
        """Check if the dock is busy (i.e., if there's a piece currently on the dock)."""
        return self.busy 

    