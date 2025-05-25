from parser.grammar import Grammar
from anytree import Node, RenderTree
import scanner.const as const
import scanner.token_types as token_types
import sys

ERROR_FILE_PATH = 'syntax_errors.txt'
PARSE_PATH = 'parse_tree.txt'

class Parser:
    
    def __init__(self, scanner):
        self.scanner = scanner
        self.grammar = Grammar()
        self.diagrams = self.grammar.get_diagrams()  # you can also get the diagrams one by one
        self.errors = []
    
    def proc(self):
        self.next_lookahead()
        start_nonterminal = self.grammar.start_nontermibnal

        start_diagram = self.diagrams[start_nonterminal]
        
        parse_tree, _ , _= self.get_parse_tree(start_diagram)
        self.save(parse_tree)

    def get_parse_tree(self, diagram):
        root = Node(diagram.name)

        
        predict = diagram.predict
        follow = diagram.follow
        states = diagram.states
        current_state_number = 0

        current_state = states[current_state_number]
        transitions = current_state.transitions
        
        while True:
            chosen_transition = None
            for tr in transitions:
                if tr.isTerminal:
                    mismatch_exp_lexm = tr.terminal
                    if tr.terminal[0] == 'EPS':
                        driven = predict['']
                        if self.is_token_in(self.lookahead, driven) or current_state_number > 0:
                            chosen_transition = tr
                            break
                    
                    if self.is_equal_token(self.lookahead, tr.terminal):
                        chosen_transition = tr
                        break


                else:
                    driven = predict[tr.nonterminal]

                    if self.is_token_in(self.lookahead, driven):
                        chosen_transition = tr
                        break
            
            if chosen_transition == None:
                
                line_num = self.scanner.reader.line_number
                if self.is_token_in(self.lookahead, follow):
                    self.add_error(f"#{line_num} : syntax error, missing {diagram.name}")
                    return root, True, False
                elif self.lookahead[1] == '$':
                    self.add_error(f"#{max(line_num+1, 0)} : syntax error, Unexpected EOF")
                    return root, False, False
                else:
                    self.add_error(f"#{line_num} : syntax error, illegal {self.leximer_expected(self.lookahead)}")
                    self.next_lookahead()
                
            else:
                break





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
                    mismatch_exp_lexm = tr.terminal
                    if tr.terminal[0] == 'EPS':
                        driven = predict['']
                        if self.is_token_in(self.lookahead, driven) or current_state_number > 0:
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
                 
                print(mismatch_exp_lexm)

                if (mismatch_exp_lexm[0] == 'EPS'):

                    current_state_number = exp_tr.next_state

                if mismatch:
                    self.add_error(f"#{line_num} : syntax error, missing {self.leximer_expected(mismatch_exp_lexm)}")
                
                elif self.is_token_in(self.lookahead, follow):
                    self.add_error(f"#{line_num} : syntax error, missing {diagram.name}")
                    return root, True, True
                else:
                    self.add_error(f"#{line_num} : syntax error, illegal {self.leximer_expected(mismatch_exp_lexm)}")
                    self.next_lookahead()
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
                    child, not_exit, add_child = self.get_parse_tree(self.diagrams[tr.nonterminal])
                    if add_child:
                        child.parent = root
                    if not not_exit:
                        return root, False, True
                current_state_number = next_state
            
        
        # self.print_tree(root)
        return root, True, True
    

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
    
    def add_error(self, error_massage):
        self.errors.append(error_massage)

    def save(self, parse_tree):
        self.write_tree(parse_tree)
        self.write_errors()
    def write_tree(self, root):
        with open(PARSE_PATH, "w", encoding='utf-8') as parse_file:     
            for pre, fill, node in RenderTree(root):
                name = node.name
                if isinstance(name, tuple):
                    if name[1] == '$':
                        name = "$"
                    else:
                        name = "(" + str(name[0]) + ", " + str(name[1])+")"
                parse_file.write("%s%s"%(pre, name))
                parse_file.write("\n")
    def write_errors(self):
        with open(ERROR_FILE_PATH, "w", encoding='utf-8') as er_file:
            if len(self.errors) == 0:
                er_file.write('There is no syntax error.')
            else:
                for er_massage in self.errors:
                    er_file.write(er_massage)  
                    er_file.write("\n")

    def leximer_expected(self, token):
        if isinstance(token, tuple):
            toktype, lex = token
            if toktype == token_types.KEYWORD:
                return lex
            if toktype == token_types.SYMBOL:
                return lex
            if toktype == token_types.NUMBER:
                return token_types.NUMBER
            if toktype == token_types.ID:
                return token_types.ID
            if toktype == token_types.EOF:
                return "$"
        else:
            return token