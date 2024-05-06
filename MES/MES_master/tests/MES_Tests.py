import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from MES import MES
from Warehouse import Warehouse
from Piece import Piece
from Line import Line


class TestMES(unittest.TestCase):

    def setUp(self):
        """Set up the MES environment and simulate warehouses."""
        self.mes = MES()
        self.mes.TopWarehouse.set_simulation_warehouse()
        self.mes.BotWarehouse.set_simulation_warehouse()

    def test_warehouse_initialization(self):
        """Test if the warehouses are initialized with the correct pieces."""
        # Assuming the get_piece_queue method pops the first item in the queue
        top_first_piece = self.mes.TopWarehouse.get_piece_queue()
        self.assertEqual(top_first_piece.id, 1)
        self.assertEqual(top_first_piece.type, 1)
        self.assertEqual(top_first_piece.final_type, 5)
        self.assertEqual(top_first_piece.order_id, 9)
        self.assertEqual(top_first_piece.delivery_day, 10)
        self.assertFalse(top_first_piece.machinetop)
        self.assertFalse(top_first_piece.machinebot)
        self.assertEqual(top_first_piece.tooltop, 0)
        self.assertEqual(top_first_piece.toolbot, 0)

    def test_find_next_transformation(self):
        """Test if the transformation lookup returns the correct tool."""
        tool = self.mes.find_next_transformation(1, 3)
        self.assertIsNotNone(tool, "No tool found for valid transformation path.")
        self.assertEqual(tool, 1, "Incorrect tool returned for the transformation.")

    def test_count_pieces_by_type_and_day(self):
        """Test if the warehouse can count pieces by type and day."""
        for day in range(0, 12):
            print(f"Day {day}")
            for piece_type in range(0, 6):
                completed, total = self.mes.TopWarehouse.count_pieces_by_type_and_day(piece_type, day)
                print(f"Type {piece_type}: {completed}/{total}")
                
    def test_check_machine_can_process(self):
        """Test if the machine can process the piece depending on its capabilities."""
        piece = Piece(self.mes.client, 1, 1, 5, 9, 10, False, False, 0, 0)

        # Loop through all lines and test both 'top' and 'bot' positions
        for line_id, line in self.mes.lines_machines.items():
            for position in ['top', 'bot']:  # Check both top and bot for each line
                with self.subTest(line=line_id, position=position):
                    can_process = self.mes.check_machine_can_process(line, position, piece)
                    self.assertTrue(can_process, f"Machine on line {line_id} at {position} should be able to process the piece but cannot.")
        piece = Piece(self.mes.client, 1, 3, 5, 9, 10, False, False, 0, 0)
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[1], 'top', piece)
        self.assertTrue(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[1], 'bot', piece)
        self.assertTrue(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[2], 'top', piece)
        self.assertTrue(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[2], 'bot', piece)
        self.assertTrue(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[3], 'top', piece)
        self.assertTrue(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[3], 'bot', piece)
        self.assertTrue(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[4], 'top', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[4], 'bot', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[5], 'top', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[5], 'bot', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[6], 'top', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[6], 'bot', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")

        #Test for busy machines
        self.mes.lines_machines[1].setTopBusy(True)
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[1], 'top', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        self.mes.lines_machines[1].setTopBusy(False)
        
        #Test for impossible transformation
        piece = Piece(self.mes.client, 1, 1, 2, 9, 10, False, False, 0, 0)
        can_process = self.mes.check_machine_can_process(self.mes.lines_machines[1], 'top', piece)
        self.assertFalse(can_process, "Machine should not be able to process the piece.")
        
        

    

if __name__ == '__main__':
    unittest.main()