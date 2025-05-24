from parser.grammar import Grammar
from anytree import Node, RenderTree
import scanner.const as const
import scanner.token_types as token_types


class Parser:
    
    def __init__(self, scanner):
        self.scanner = scanner
        self.grammar = Grammar()
        self.diagrams = self.grammar.get_diagrams()  # you can also get the diagrams one by one
    
    def proc(self):
        self.next_lookahead()
        start_nonterminal = self.grammar.start_nontermibnal

        start_diagram = self.diagrams[start_nonterminal]
        parse_tree = self.get_parse_tree(start_diagram)
        self.print_tree(parse_tree)

    def get_parse_tree(self, diagram):
        root = Node(diagram.name)

        
        predict = diagram.predict
        follow = diagram.follow
        states = diagram.states
        current_state_number = 0


        while (current_state_number != 1):
            current_state = states[current_state_number]
            transitions = current_state.transitions

            chosen_transition = None
            mismatch = False
            mismatch_exp_lexm = None
            exp_tr = None
            for tr in transitions:
                exp_tr = tr
                if tr.isTerminal:
                    if tr.terminal[0] == 'EPS':
                        driven = predict['']
                        if self.is_token_in(self.lookahead, driven):
                            chosen_transition = tr
                            break
                    elif current_state_number == 0:
                        if self.is_equal_token(self.lookahead, tr.terminal):
                            chosen_transition = tr
                            break
                    else:
                        if self.is_equal_token(self.lookahead, tr.terminal):
                            chosen_transition = tr
                            break
                        else:
                            mismatch = True
                            mismatch_exp_lexm = tr.terminal
                            break

                else:
                    if current_state_number == 0:
                        driven = predict[tr.nonterminal]

                        if self.is_token_in(self.lookahead, driven):
                            chosen_transition = tr
                            break
                    else:
                        chosen_transition = tr
                        break
            if chosen_transition == None:
                line_num = self.scanner.reader.line_number
                if mismatch:
                    print(f"#{line_num} : syntax error, missing {mismatch_exp_lexm}")
                
                elif self.lookahead in follow:
                    print()
                    return root
                else:
                    return root
                current_state_number = exp_tr.next_state

                
            else:
                next_state = tr.next_state
                if tr.isTerminal:
                    if tr.terminal[0] == 'EPS':
                        Node("epsilon", parent=root)
                    else:
                        Node(self.lookahead, parent=root)
                        self.next_lookahead()
                else:
                    child = self.get_parse_tree(self.diagrams[tr.nonterminal])
                    child.parent = root
                current_state_number = next_state
            
        
        # self.print_tree(root)
        return root
    

    def next_lookahead(self):
        self.lookahead = self.scanner.get_next_token()
                

    def is_equal_token(self, token, expected_token):

        if isinstance(expected_token, tuple):
            exptype, sym = expected_token
            toktype, lex = token
            if exptype == token_types.KEYWORD:
                return lex == sym and toktype == token_types.KEYWORD
            if exptype == token_types.SYMBOL:
                return lex == sym and toktype == token_types.SYMBOL
            if exptype == token_types.NUMBER:
                return toktype == token_types.NUMBER
            if exptype == token_types.ID:
                return toktype == token_types.ID
            if exptype == token_types.EOF:
                return toktype == token_types.EOF
 
        
        else:
            sym = expected_token
            toktype, lex = token
            if sym in const.keywords:
                return lex == sym and toktype == token_types.KEYWORD
            if sym in (const.all_symbols + ["=="]):
                return lex == sym and toktype == token_types.SYMBOL
            if sym == "NUM":
                return toktype == token_types.NUMBER
            if sym == "ID":
                return toktype == token_types.ID
            if sym == '$':
                return toktype == token_types.EOF

    def is_token_in(self, token, list_sym):
        for sym in list_sym:
            if self.is_equal_token(token, sym):
                return True
        return False

    def print_tree(self, root):
        for pre, fill, node in RenderTree(root):
            print(f"{pre}{node.name}")