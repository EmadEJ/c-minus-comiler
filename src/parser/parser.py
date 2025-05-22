from parser.grammar import Grammar

class Parser:
    
    def __init__(self, scanner):
        self.scanner = scanner
        self.grammar = Grammar()
        self.diagrams = self.grammar.get_diagrams()  # you can also get the diagrams one by one
    
    def proc(self):
        # TODO
        pass