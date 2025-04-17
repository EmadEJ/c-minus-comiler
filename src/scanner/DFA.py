import scanner.token_types as token_types
from scanner.const import *

class State:
    
    def __init__(self, ID, final_type: str, index_back, invalid_transition=-1):
        self.ID = ID
        self.final_type = final_type
        self.index_back = index_back
        self.transition = {}
        self.invalid_transition = invalid_transition # Assume invalid char state is -1
        
    def add_transition(self, dest, char_list):
        for char in char_list:
            if char in self.transition.keys():
                print(f"Err: double transition on {char} for state {self.ID}")
            self.transition[char] = dest 
    
    def transit(self, char):
        if char not in valid_chars:
            return self.invalid_transition
        if char not in self.transition.keys():
            print(f"Err: transition not defined on {char} for state {self.ID}")
            return None
        return self.transition[char]
    
       
class DFA:
    
    def __init__(self):
        self.states: dict[int, State] = {}
        self.start_state = 0
        self.current = self.start_state
        
        self.construct_DFA()
        
    def construct_DFA(self):
        # State definition
        self.add_state(-1, token_types.INVALID_INPUT, False)  # Invalid input
        self.add_state(0, None, None)  # Start
        self.add_state(1, None, None)  # 4
        self.add_state(2, token_types.ID, True)  # Text
        self.add_state(3, None, None)  # /
        self.add_state(4, None, None, 4)  # * INVALID PRUNE
        self.add_state(5, None, None, 4)  # 3 INVALID PRUNE
        self.add_state(6, token_types.COMMENT, False)  # COMM
        self.add_state(7, token_types.UNCLOSED_COMMENT, True)  # Unclosed comment error
        self.add_state(8, token_types.SYMBOL, True)  # S*
        self.add_state(9, None, None)  # 2
        self.add_state(10, token_types.UNMATCHED_COMMENT, False)  # Unmatched comment error
        self.add_state(11, None, None)  # =
        self.add_state(12, token_types.SYMBOL, False)  # S
        self.add_state(13, None, None)  # 1
        self.add_state(14, token_types.NUMBER, True)  # NUM
        self.add_state(15, token_types.INVALID_NUMBER, False)  # Invalid number error
        self.add_state(16, None, None, 17) # 0
        self.add_state(17, token_types.WHITESPACE, True) # Whitespace
        self.add_state(18, token_types.EOF, False)
        
        ### Transitions
        
        # Text
        self.add_transition(0, 1, letters)
        
        self.add_transition(1, 1, letters + digits)
        self.add_transition(1, 2, whitespace + all_symbols + eof)
                
        # Comment
        self.add_transition(0, 3, slash_symbol)
        
        self.add_transition(3, 4, star_symbol)
        self.add_transition(3, 8, whitespace + digits + letters + symbol + slash_symbol + equal_symbol + eof)
        
        self.add_transition(4, 4, whitespace + digits + letters + symbol + slash_symbol + equal_symbol)
        self.add_transition(4, 5, star_symbol)
        self.add_transition(4, 7, eof)
        
        self.add_transition(5, 4, whitespace + digits + letters + symbol + equal_symbol)
        self.add_transition(5, 5, star_symbol)
        self.add_transition(5, 6, slash_symbol)
        self.add_transition(5, 7, eof)
        
        self.add_transition(0, 9, star_symbol)
        
        self.add_transition(9, 10, slash_symbol)
        self.add_transition(9, 9, star_symbol)
        self.add_transition(9, 8, whitespace + digits + letters + symbol + equal_symbol + eof)
        
        # Symbols
        self.add_transition(0, 11, equal_symbol)
        
        self.add_transition(11, 8, whitespace + digits + letters + symbol + slash_symbol + star_symbol + eof)
        self.add_transition(11, 12, equal_symbol)
        
        self.add_transition(0, 12, symbol)
        
        # Numbers
        self.add_transition(0, 13, digits)
        
        self.add_transition(13, 13, digits)
        self.add_transition(13, 14, whitespace + all_symbols + eof)
        self.add_transition(13, 15, letters)
        
        # Whitespace
        self.add_transition(0, 16, whitespace)
        self.add_transition(16, 16, whitespace)
        self.add_transition(16, 17, digits + letters + all_symbols + eof)
        
        # EOF
        self.add_transition(0, 18, eof)
    
    def add_state(self, ID, final_type, index_back, invalid_transition=-1):
        state = State(ID, final_type, index_back, invalid_transition)
        self.states[ID] = state

    def add_transition(self, src, dest, char_list):
        self.states[src].add_transition(dest, char_list)
        
    def get_current_state(self):
        return self.states[self.current]
        
    def transit(self, char):
        result = self.states[self.current].transit(char)
    
        if not isinstance(result, int):
            print("Err: DFA invalid transit")
            return result
        
        self.current = result
        return self.states[self.current]

    def reset(self):
        self.current = self.start_state
