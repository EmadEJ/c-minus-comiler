from scanner.scanner import Scanner

scanner = Scanner("input.txt")
scanner.scan()
scanner.save("tokens.txt", "lexical_errors.txt", "symbol_table.txt")