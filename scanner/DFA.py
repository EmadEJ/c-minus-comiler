import const
import types

class State:
    
    def __init__(self, ID, final_type, index_back, invalid_transition = -1):
        self.ID = ID
        self.final_type = final_type
        self.index_type = index_back
        self.transition = {}
        self.invalid_transition = invalid_transition # Assume invalid char state is -1
        
    def add_transition(self, char_list, dest):
        for char in char_list:
            if char in self.transition.keys():
                print(f"Err: double transition on {char} for state {self.ID}")
            self.transition[char] = dest 
    
    def transit(self, char):
        if char not in const.valid_chars:
            return self.invalid_transition
        if char not in self.transition.keys():
            print(f"transition not defined on {self.ID} on {char}")
            return None
        return self.transition[char]
    
       
class DFA:
    
    def __init__(self):
        self.states: dict[int, State] = {}
        self.start_state = None
        self.current = self.start_state
        
        self.construct_DFA()
        
    def construct_DFA(self):
        # TODO
        pass
    
    def add_state(self, ID, final_type, index_back):
        state = State(ID, final_type, index_back)
        self.states[ID] = state

    def add_transition(self, src, dest, char_list):
        self.states[src].add_transition(dest, char_list)
        
    def get_current_state(self):
        return self.states[self.current]
        
    def transit(self, char):
        result = self.states[self.current].transit(char)
    
        if not isinstance(result, int):
            return result
        
        self.current = result
        return None

    def reset(self):
        self.current = self.start_state