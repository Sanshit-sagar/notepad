import unittest 
from editor import PieceTable

class PieceTableTester(unittest.TestCase): 
    
    def test_piece_table_init(self): 
        init_file_data = "Hello there."
        p = PieceTable(init_file_data)
        self.assertEqual(p.get_added_buffer(), "")
        self.assertEqual(p.get_original_buffer(), init_file_data)
        self.assertEqual(p.get_sequence_length(), len(init_file_data))
        self.assertEqual(len(p.get_undo_stack()), 0)
        self.assertEqual(len(p.get_redo_stack()), 0)

    def test_insertions(self): 
        test_sequence = "Hello there." 
        p = PieceTable(test_sequence)
        str1 = "1111"
        str2 = "2222"
        str3 = "3333"
        
        p.insert(0, str1)
        test_sequence = str1 + test_sequence
        self.assertEqual(p.get_sequence(), test_sequence)

        p.insert(3, str2)
        test_sequence = test_sequence[ : 3] + str2 + test_sequence[3: ]
        self.assertEqual(p.get_sequence(), test_sequence)

        p.insert(len(p.get_sequence()), str3)
        test_sequence = test_sequence + str3 
        self.assertEqual(p.get_sequence(), test_sequence)
    
    def test_deletions(self): 
        test_sequence = "1111 2222 3333 4444"
        p = PieceTable(test_sequence)
        
        test_sequence = test_sequence[4:]
        p.delete(0, 4)
        test_sequence = test_sequence[:6] + test_sequence[11:]
        p.delete(6, 5)
        self.assertEqual(p.get_sequence(), test_sequence)

    def test_subsequence(self): 
        test_sequence = "1111 2222 3333 4444"
        p = PieceTable(test_sequence)

        self.assertEqual(p.get_subsequence(0, 4), test_sequence[0:4])
        self.assertEqual(p.get_subsequence(5, 7), test_sequence[5:12])


    def test_undo(self): 
        test_sequence = "1111 2222 3333 4444 5555" 
        p = PieceTable(test_sequence)
        
        p.delete(0, 4) 
        p.delete(4, 4)
        p.undo() 
        p.undo() 
        self.assertEqual(p.get_sequence(), test_sequence)
        p.insert(2, "HELLO")
        p.delete(6, 3)
        p.undo()
        p.undo() 
        self.assertEqual(p.get_sequence(), test_sequence)

    def test_redo(self): 
        test_sequence = "A large span of text"
        p = PieceTable(test_sequence)
        str1, str2, str3, str4 = "1111", "2222", "3333", "4444"
        strA = "AAA"
        p.insert(0, str1)
        p.insert(10, str2)
        p.insert(15, str3)
        p.insert(32, str4)
        p.delete(2,5)
        p.delete(3,7) 
        p.undo()
        p.undo()
        p.redo() 
        p.redo()
        p.insert(10, strA)
        p.redo() 
        test_sequence = str1 + test_sequence
        test_sequence = test_sequence[0:10] + str2 + test_sequence[10:]
        test_sequence = test_sequence[0:15] + str3 + test_sequence[15:]
        test_sequence = test_sequence[0:32] + str4 + test_sequence[32:]
        test_sequence = test_sequence[0:2] + test_sequence[7:]
        test_sequence = test_sequence[0:3] + test_sequence[10:]
        test_sequence = test_sequence[0:10] + strA + test_sequence[10:]
        self.assertEqual(p.get_sequence(), test_sequence) 
        
if __name__ == '__main__': 
    unittest.main() 


