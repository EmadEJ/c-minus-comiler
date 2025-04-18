from scanner.scanner import Scanner

# G6
# Emad Emamjomeh - 400108774
# Amirhossein MaleckMohammadi - 401106577


scanner = Scanner("input.txt")
scanner.scan()
scanner.save("tokens.txt", "lexical_errors.txt", "symbol_table.txt")
