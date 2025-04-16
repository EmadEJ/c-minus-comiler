from scanner.DFA import DFA
from scanner.reader import Reader
import scanner.token_types as token_types, scanner.const as const

class Scanner:
    
    def __init__(self, filepath):
        self.reader = Reader(filepath)
        self.dfa = DFA()
        self.tokens = {}
        self.errors = {}
        self.symbol_table = const.keywords
        
    def add_token(self, line, token):
        if not line in self.tokens.keys():
            self.tokens[line] = []
        self.tokens[line].append(token)
    
    def add_error(self, line, error):
        if not line in self.errors.keys():
            self.errors[line] = []
        self.errors[line].append(error)
    
    
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
                    self.add_error(self.reader.line_number, (token, cur_state.final_type))
                    # self.reader.read_line()
                elif cur_state.final_type not in [token_types.WHITESPACE, token_types.EOF] :
                    if cur_state.final_type == token_types.ID:
                        if token in const.keywords:
                            self.add_token(self.reader.line_number, (token_types.KEYWORD, token))
                        else:
                            self.add_token(self.reader.line_number, (cur_state.final_type, token))
                            if not token in self.symbol_table:
                                self.symbol_table.append(token)
                    else:
                        self.add_token(self.reader.line_number, (cur_state.final_type, token))
                    
                token = ""
                self.dfa.reset()
                
                if char == "":
                    break
    
    def save(self, path_token, path_error, path_symbol_table):
        with open(path_token, "w") as token_file:
            for line, tokens in self.tokens.items():
                token_file.write(f"{line}.\t")
                for token in tokens:
                    token_file.write(f"({token[0]}, {token[1]}) ")
                token_file.write("\n")
        
        with open(path_error, "w") as error_file:
            for line, errors in self.errors.items():
                error_file.write(f"{line}.\t")
                for error in errors:
                    error_file.write(f"({error[0]}, {error[1]}) ")
                error_file.write("\n")
        
        with open(path_symbol_table, "w") as symbol_table_file:
            for idx, lexeme in enumerate(self.symbol_table):
                symbol_table_file.write(f"{idx+1}.\t{lexeme}\n")
