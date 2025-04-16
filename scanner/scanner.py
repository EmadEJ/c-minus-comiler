from DFA import DFA
from reader import Reader
import token_types, const

class Scanner:
    
    def __init__(self, filepath):
        self.reader = Reader(filepath)
        self.dfa = DFA()
        self.tokens = {}
        self.errors = {}
        self.symbol_table = const.keywords()
        
    def add_token(self, line, token):
        if not line in self.tokens.keys():
            self.tokens[line] = []
        self.tokens[line].append(token)
    
    def scan(self):
        token = ""
        while True:
            char = self.reader.read_char()
            token += char

            cur_state = self.dfa.transit(char)
            
            if cur_state.final_type is not None:
                if cur_state.index_back == True:
                    self.reader.unread_char()
                    token = token[:-1]
                
                if cur_state.final_type.endswith("ERROR"):
                    self.errors[self.reader.line_number] = (cur_state.final_type, token)
                    self.reader.read_line()
                else:
                    if cur_state.final_type == token_types.ID and token in const.keywords:
                        self.add_token(self.reader.line_number, (token_types.KEYWORD, token))
                    else:
                        self.symbol_table.append(token)
                        self.add_token(self.reader.line_number, (cur_state.final_type, token))
                
                break
    
    def save(self, path_token, path_error, path_symbol_table):
        with open(path_token, "w") as token_file:
            for line, tokens in self.tokens.items():
                token_file.write(f"{line}:\t{', '.join(tokens)}\n")
        
        with open(path_error, "w") as error_file:
            for line, error in self.errors.items():
                error_file.write(f"{line}:\t{error}\n")
        
        with open(path_symbol_table, "w") as symbol_table_file:
            for idx, lexeme in enumerate(self.symbol_table):
                symbol_table_file.write(f"{idx}:\t{lexeme}\n")
        