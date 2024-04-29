import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import MES



class TestMES(unittest.TestCase):
    #Tests fpr find_machine
    def test_find_machine(self):
        mes = MES.MES()
        #print(mes.transformations)
        self.assertEqual(mes.find_machine(9, 3), (None, None, None))
        line, machine, tool = mes.find_machine(4, 7)
        self.assertEqual(machine, 'top')
        self.assertEqual(tool, 3)
        self.assertEqual(line.id, 1)

        line, machine, tool = mes.find_machine(1, 7)
        self.assertEqual(machine, 'top')
        self.assertEqual(tool, 1)
        self.assertEqual(line.id, 1)

        line, machine, tool = mes.find_machine(8, 7)
        self.assertEqual(machine, 'bot')
        self.assertEqual(tool, 6)
        self.assertEqual(line.id, 4)

        
        

if __name__ == '__main__':
    unittest.main()