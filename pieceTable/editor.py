from enum import Enum, auto 

class Piece: 
    def __init__(self, buf_type, buf_ind, piece_len): 
        self.buffer_type = buf_type
        self.buffer_start = buf_ind
        self.length = piece_len
    
    def __str__(self): 
        return f'Buffer Type: {self.buffer_type}, Start Index : {self.buffer_start}, Length: {self.length}' 
            
class PieceTable: 
    class BUFFER(Enum): 
        ORIGINAL = auto()
        UPDATED = auto()

        def __str__(self):
            return self.name 
        
    def __init__(self, file_data = ""):
        first_entry = Piece(self.BUFFER.ORIGINAL, 0, len(file_data)) 
        self._table = [ (first_entry) ] 
        self._original_buffer = file_data
        self._added_buffer = "" 
        self._sequence_length = len(file_data)
        self._misspellings = 0
        self._undo_stack = [] 
        self._redo_stack = [] 
        self.dictionary = set() 
        with open("/usr/share/dict/words") as input_dictionary:
            for line in input_dictionary:
                words = line.strip().split(" ")
                for word in words:
                    self.dictionary.add(word)
    
    def __str__(self): 
        res = ""
        for piece in self._table: 
            res += f'{piece} \n'
        return res 

    def get_table(self): 
        return self._table
    
    def get_sequence_length(self): 
        return self._sequence_length
    
    def get_original_buffer(self): 
        return self._original_buffer
    
    def get_added_buffer(self): 
        return self._added_buffer 
    
    def get_undo_stack(self): 
        return self._undo_stack 
    
    def get_redo_stack(self): 
        return self._redo_stack 
    
    def get_misspellings(self): 
        return self._misspellings
    
    def get_logical_offset(self, table_index):
        """
        Finds the running total of all the lengths of the pieces 
        in the table. 
        """
        if table_index < 0: 
            raise ValueError(f'Index: {table_index} out of bounds.')

        difference = table_index
        for i in range(len(self._table)):
            curr_piece = self._table[i]
            if difference <= curr_piece.length: 
                logical_offset = curr_piece.buffer_start + difference 
                return (i, logical_offset, curr_piece) 
            difference -= curr_piece.length         
        
        raise ValueError(f'Index: {table_index} out of bounds.')
        
    def update_table(self, start, num_updates, updates): 
        """
        Ignores any empty/edge pieces, and then updates a table with either the 
        2 (in case of a delete) or 3 (for inserts) updated/new pieces.
        """
        updates = list(filter(lambda piece: piece.length > 0, updates)) 
        return self._table[ : start] + updates + self._table[start + num_updates :]

    def get_sequence(self): 
        """
        Returns the entire text by simply appending the parts pointed to by 
        each of the pieces in the table, to each other.
        """
        sequence = "" 
        for piece in self._table: 
            curr_buffer = self.get_buffer(piece)
            sequence += curr_buffer[piece.buffer_start : piece.buffer_start + piece.length]
        #print(sequence)
        return sequence

    def get_buffer(self, piece): 
        """
        Each piece points to either the immutable original buffer, or the add buffer - to which 
        all additions are appended. 
        """
        curr_buffer = self._original_buffer if piece.buffer_type==self.BUFFER.ORIGINAL else self._added_buffer
        return curr_buffer

    def get_subsequence(self, start_index, length): 
        """
        Returns only part of the document as specified by the parameters. 
        """
        end_index = start_index + length 
        start_table_index, start_logical_offset, start_piece = self.get_logical_offset(start_index)
        end_table_index, end_logical_offset, end_piece = self.get_logical_offset(end_index)

        curr_buffer = self.get_buffer(start_piece)
        
        if start_table_index == end_table_index: 
            return curr_buffer[start_logical_offset : start_logical_offset + length]
        
        subsequence = curr_buffer[start_logical_offset : start_piece.buffer_start + start_piece.length]
        for i in range(start_table_index + 1, end_table_index + 1):
            curr_piece = self._table[i]
            curr_buffer = self.get_buffer(curr_piece)
            if i == end_table_index: 
                subsequence += curr_buffer[curr_piece.buffer_start : end_logical_offset]
            else: 
                subsequence += curr_buffer[curr_piece.buffer_start : curr_piece.buffer_start + curr_piece.length]
        
        return subsequence
    
    def reset_redo_stack(self): 
        """
        Empties the stack when a new action is taken eg: after 5 undoes, a new 
        insert is made.
        """
        self._redo_stack = [] 
    
    def insert(self, index, addition, reset_redo_stack = False):
        """
        Appends the string at the end of the add buffer. Additionally, 
        updates the piece table by splitting the table into two parts
        and the new piece goes in the middle. 
        """
        if index < 0 or index > self.get_sequence_length(): 
            raise ValueError(f'Index {index} out of bounds.')

        if not reset_redo_stack: 
            self.reset_redo_stack() 
        
        self._misspellings += self.calculate_misspellings(addition)

        added_buffer_len = len(self._added_buffer)
        self._sequence_length += len(addition)
        self._added_buffer += addition 

        table_index, logical_offset, curr_piece = self.get_logical_offset(index)

        if self._table[table_index].buffer_type == self.BUFFER.UPDATED: 
            if logical_offset == self._table[table_index].buffer_start + self._table[table_index].length == added_buffer_len: 
                self._table[table_index].length += len(addition)
                return 
        
        curr_piece = self._table[table_index]
        partition_index = logical_offset - curr_piece.buffer_start
        table_additions = [
            Piece(curr_piece.buffer_type, curr_piece.buffer_start, partition_index), 
            Piece(self.BUFFER.UPDATED, added_buffer_len, len(addition)), 
            Piece(curr_piece.buffer_type, logical_offset, curr_piece.length - partition_index), 
        ]

        self._table = self.update_table(table_index, 1, table_additions)
        self._undo_stack.append( ("INSERT", addition, index) )
        
    def delete(self, start_index, length, reset_redo_stack = False): 
        """
        The text isn't deleted from the add buffer, but the piece table is updated 
        so that any there isn't any piece that now points to the text in the given range. 
        """
        if start_index + length < 0 or start_index + length > self.get_sequence_length(): 
            raise ValueError(f'Index: {start_index + length} out of bounds for {self.get_sequence_length()}')

        if not reset_redo_stack: 
            self.reset_redo_stack() 

        start_table_index, start_logical_offset, start_piece = self.get_logical_offset(start_index)
        end_table_index, end_logical_offset, end_piece = self.get_logical_offset(start_index + length)
        self._sequence_length -= length 
        deleted_text = self.get_subsequence(start_index, length) 
        self._undo_stack.append( ("DELETE", deleted_text, start_index) ) 
        self._misspellings -= self.calculate_misspellings(deleted_text)
        
        if start_table_index == end_table_index: 
            curr_piece = self._table[start_table_index]

            if start_logical_offset == curr_piece.buffer_start:
                curr_piece.length -= length
                curr_piece.buffer_start += length
                return 
            elif end_logical_offset == curr_piece.buffer_start + curr_piece.length: 
                curr_piece.length -= length
                return 

        table_deletions = [
            Piece(start_piece.buffer_type, start_piece.buffer_start, start_logical_offset - start_piece.buffer_start),
            Piece(end_piece.buffer_type, end_logical_offset, end_piece.length - (end_logical_offset - end_piece.buffer_start)),
        ]

        self._table = self.update_table(start_table_index, end_table_index - start_table_index + 1, table_deletions)
        
       
    def calculate_misspellings(self, text): 
        """
        Called everytime a text is inserted or deleted.
        """
        result = 0
        for word in text.split(" "):
            if word not in self.dictionary:
                result = result + 1
        return result

    def undo(self):
        """
        Traverses down the stack, and undoes a delete by inserting the value that was deleted
        and vice versa. It then pushes the action onto the redo stack.
        """
        if len(self._undo_stack) == 0: 
            print("At initial state.")
            return 

        action_type, modification_str, modification_index = self._undo_stack.pop() 
        if action_type == 'DELETE': 
            self.insert(modification_index, modification_str, True)
        else: 
            self.delete(modification_index, len(modification_str), True)
        self._undo_stack.pop() 
        self._redo_stack.append( (action_type, modification_str, modification_index) )
    
    def redo(self): 
        """
        Does the exact opposite of the undo function the only caveat is, the redo stack 
        gets emptied out anytime a new action is taken after the undo/redo function is 
        done being called.
        """
        if len(self._redo_stack) == 0: 
            print("At latest state.")
            return 
        
        action_type, modification_str, modification_index = self._redo_stack.pop()
        if action_type == 'DELETE':
            self.delete(modification_index, len(modification_str), True)
        else: 
            self.insert(modification_index, modification_str, True)

class SimpleEditor:
    def __init__(self, document):
        self.document = document
        self.piece_table = PieceTable(document) 
        self.paste_text = ""

    def cut(self, i, j):
        if j<i: 
            raise ValueError(f'End index {j} cannot be larger than the start index: {i}')
        self.paste_text = self.piece_table.get_subsequence(i, j-i)
        self.piece_table.delete(i, j-i)
        self.document = self.piece_table.get_sequence() 

    def copy(self, i, j):
        if j<i: 
            raise ValueError(f'End index {j} cannot be larger than the start index: {i}')
        self.paste_text = self.piece_table.get_subsequence(i, j-i)

    def paste(self, i):
        self.piece_table.insert(i, self.paste_text)
        self.document = self.piece_table.get_sequence()

    def get_text(self):
        return self.piece_table.get_sequence()

    def misspellings(self):
        return self.piece_table.get_misspellings() 
        
import timeit

class EditorBenchmarker:
    new_editor_case = """
from __main__ import SimpleEditor
s = SimpleEditor("{}")"""

    editor_cut_paste = """
for n in range({}):
    if n%2 == 0:
        s.cut(1, 3)
    else:
        s.paste(2)"""

    editor_copy_paste = """
for n in range({}):
    if n%2 == 0:
        s.copy(1, 3)
    else:
        s.paste(2)"""

    editor_get_text = """
for n in range({}):
    s.get_text()"""

    editor_mispellings = """
for n in range({}):
    s.misspellings()"""

    def __init__(self, cases, N):
        self.cases = cases
        self.N = N
        self.editor_cut_paste = self.editor_cut_paste.format(N)
        self.editor_copy_paste = self.editor_copy_paste.format(N)
        self.editor_get_text = self.editor_get_text.format(N)
        self.editor_mispellings = self.editor_mispellings.format(N)

    def benchmark(self):
        for case in self.cases:
            print("Evaluating case: {}".format(case))
            new_editor = self.new_editor_case.format(case)
            cut_paste_time = timeit.timeit(stmt=self.editor_cut_paste,setup=new_editor,number=1)
            print("{} cut paste operations took {} s".format(self.N, cut_paste_time))
            copy_paste_time = timeit.timeit(stmt=self.editor_copy_paste,setup=new_editor,number=1)
            print("{} copy paste operations took {} s".format(self.N, copy_paste_time))
            get_text_time = timeit.timeit(stmt=self.editor_get_text,setup=new_editor,number=1)
            print("{} text retrieval operations took {} s".format(self.N, get_text_time))
            mispellings_time = timeit.timeit(stmt=self.editor_mispellings,setup=new_editor,number=1)
            print("{} mispelling operations took {} s".format(self.N, mispellings_time))
            

if __name__ == "__main__":
    b = EditorBenchmarker(["hello friends"], 100)
    b.benchmark()