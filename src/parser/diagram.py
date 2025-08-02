from parser.c_minus_grammar import c_minus_grammar, EPS
import scanner.const as const
import scanner.token_types as token_types

def get_token(sym):
    if sym in const.keywords:
        return (token_types.KEYWORD, sym)
    if sym in (const.all_symbols + ["=="]):
        return (token_types.SYMBOL, sym)
    if sym == "NUM":
        return (token_types.NUMBER, None)
    if sym == "ID":
        return (token_types.ID, None)
    if sym == "$":
        return (token_types.EOF, '$')
    
    assert()
    return None

class Transition:
    
    def __init__(self, isTerminal: bool, next_state, terminal, nonterminal):
        self.isTerminal = isTerminal
        self.terminal = terminal
        self.nonterminal = nonterminal
        self.next_state = next_state
        
        if self.isTerminal:
            assert(self.nonterminal is None)
        else:
            assert(self.terminal is None)
    

class State:
    
    def __init__(self, id, isFinal=False):
        self.id = id
        self.transitions = []
        self.isFinal = isFinal
    
    def add_transition(self, transition: Transition):
        self.transitions.append(transition)
    
    
class Diagram:
    
    def __init__(self, name, first, follow, predict):
        self.states = {
            1: State(1, True),
            0: State(0)
        }  # first and final state
        self.name = name
        
        self.first = first
        self.follow = follow
        self.predict = predict
    
    def add_rule(self, rule: list):
        if len(rule) == 0:
            self.states[0].add_transition(Transition(True, 1, ("EPS", ""), None))
            return
        
        cur_state = 0
        for idx, sym in enumerate(rule):
            nxt_state_id = 1
            if idx != len(rule) - 1:
                nxt_state_id = len(self.states)
                self.states[nxt_state_id] = State(nxt_state_id)
            
            if sym in set(c_minus_grammar.keys()):  # non-terminal
                transition = Transition(False, nxt_state_id, None, sym)
            else:
                transition = Transition(True, nxt_state_id, get_token(sym), None)
            
            self.states[cur_state].add_transition(transition)
            cur_state = nxt_state_id