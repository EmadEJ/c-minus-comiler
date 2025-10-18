from scanner.scanner import Scanner
from parser.grammar import Grammar
from parser.parser import Parser

# G6
# Emad Emamjomeh - 400108774
# Amirhossein MaleckMohammadi - 401106577

scanner = Scanner("input.txt")
# scanner.scan()

grammar = Grammar()
# grammar.display()

parser = Parser(scanner)
parser.proc()

# scanner.save("tokens.txt", "lexical_errors.txt", "symbol_table.txt")
