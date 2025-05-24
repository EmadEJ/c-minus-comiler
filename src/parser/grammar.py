from parser.diagram import Diagram
from parser.c_minus_grammar import start_nonterminal, c_minus_grammar, EPS


class Grammar:
    
    def __init__(self):
        self.grammar = c_minus_grammar
        self.nonterminals = set(self.grammar.keys())
        self.terminals = set()
        for prods in self.grammar.values():
            for prod in prods:
                for sym in prod:
                    if sym not in self.nonterminals:
                        self.terminals.add(sym)
        self.first, self.follow, self.predict = self.prep(self.grammar, self.nonterminals, self.terminals)
        
        self.start_nontermibnal = start_nonterminal
        
    def prep(self, grammar, nonterminals, terminals):
        

        FIRST = {nt: set() for nt in nonterminals}
        FOLLOW = {nt: set() for nt in nonterminals}

        def first_of_symbol(sym):
            if sym in terminals:
                return {sym}
            return FIRST[sym]

        changed = True
        while changed:
            changed = False
            for nt, prods in grammar.items():
                for prod in prods:
                    if not prod:
                        if EPS not in FIRST[nt]:
                            FIRST[nt].add(EPS); changed = True
                    else:
                        temp_set = set()
                        contains_epsilon = True
                        for sym in prod:
                            sym_first = first_of_symbol(sym)
                            temp_set |= (sym_first - {EPS})
                            if EPS not in sym_first:
                                contains_epsilon = False
                                break
                        if contains_epsilon:
                            temp_set.add(EPS)
                        if not temp_set.issubset(FIRST[nt]):
                            FIRST[nt] |= temp_set
                            changed = True

        start_symbol = "Program"
        FOLLOW[start_symbol].add("$")

        changed = True
        while changed:
            changed = False
            for nt, prods in grammar.items():
                for prod in prods:
                    trailer = FOLLOW[nt].copy()
                    for sym in reversed(prod):
                        if sym in nonterminals:
                            if not trailer.issubset(FOLLOW[sym]):
                                FOLLOW[sym] |= trailer
                                changed = True
                            if EPS in FIRST[sym]:
                                trailer |= (FIRST[sym] - {EPS})
                            else:
                                trailer = FIRST[sym]
                        else:
                            trailer = first_of_symbol(sym)

        PREDICT = {}
        for nt, prods in grammar.items():
            PREDICT[nt] = {}
            for prod in prods:
                first_alpha = set()
                contains_epsilon = True
                if not prod:
                    first_alpha = {EPS}
                else:
                    for sym in prod:
                        sym_first = first_of_symbol(sym)
                        first_alpha |= (sym_first - {EPS})
                        if EPS not in sym_first:
                            contains_epsilon = False
                            break
                predict = set(first_alpha)
                if contains_epsilon:
                    predict |= FOLLOW[nt]
                PREDICT[nt][prod[0] if prod else ''] = predict
                
        
        return FIRST, FOLLOW, PREDICT
    
    def get_diagrams(self):
        diagrams = {}
        for nonterminal in self.nonterminals:
            diagrams[nonterminal] = self.get_diagram(nonterminal)
        return diagrams
    
    def get_diagram(self, nonterminal):        
        diagram = Diagram(nonterminal, self.first[nonterminal], self.follow[nonterminal], self.predict[nonterminal])
        
        for rule in self.grammar[nonterminal]:
            diagram.add_rule(rule)
            
        return diagram
    
    def display(self):
        diagrams = self.get_diagrams()
        
        print("################################ FIRST ################################ ")
        for nt, first in self.first.items():
            print(f"{nt}:")
            print(first)
            
        print("################################ FOLLOW ################################ ")
        for nt, follow in self.follow.items():
            print(f"{nt}:")
            print(follow)
            
        print("################################ PREDICT ################################ ")
        for nt, predict in self.predict.items():
            print(f"##### {nt}:")
            for rule, syms in predict.items():
                print(f"'{rule}':\n{syms}")
                
        print("################################ DIAGRAMS ################################ ")
        for nt, diagram in diagrams.items():
            print()
            print(f"########## {nt}")
            for id, state  in diagram.states.items():
                print(f"# {id}:")
                for transition in state.transitions:
                    print(transition.isTerminal, transition.next_state, transition.terminal, transition.nonterminal, sep=" ")
                    
        