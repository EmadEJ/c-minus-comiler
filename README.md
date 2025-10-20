#  C-Minus Compiler  
 A one-pass compiler for the C-Minus language — implemented in Python.  

---

##  Authors
- **Emad Emamjomeh**  
- **Amirhossein Maleck Mohammadi** 

---

This project implements a one-pass compiler for a simplified version of the C programming language.  
It was developed as part of the Compiler Design (40-414) course at Sharif University of Technology during Spring 2025.

The compiler performs lexical analysis, syntax analysis, and intermediate code generation.

1. **Lexical Analyzer (Scanner)**
    Implemented using a Deterministic Finite Automaton (DFA) that recognizes valid tokens of the C-Minus language.
    The scanner handles: identifiers, keywords, numbers, symbols, whitespace, and comments.
Lexical errors are recovered using the Panic Mode recovery method. When an invalid token is detected, the analyzer skips characters until a valid token boundary is found, allowing compilation to continue gracefully.
 
2. **Syntax Analyzer (Predictive Top-Down Parser)**
 Implemented using the transition diagram method for each non-terminal in the grammar.
 The parser is predictive (non-recursive), relying on FIRST and FOLLOW sets to select the correct production without backtracking.
 Syntax errors also handled via Panic Mode. When a parsing error occurs, input symbols are discarded until a suitable synchronization token is reached, minimizing the    cascading effect of errors.

4. **Intermediate Code Generator**  
Generates Three-Address Code as the intermediate representation.
Uses a semantic stack to manage operands and operators during parsing and to perform syntax-directed translation in tandem with parsing.
The Intermediate code generator supports:
Arithmetic and relational operations,
Conditional and looping constructs, and
Assignments and simple function calls.


---

##  Running the Code

Make sure you have **Python 3.8+** installed and **anytree** library. 

Clone the repository.

Go to the src directory.

Ensure `input.txt` is present in the same folder as `compiler.py`. This is the C-Minus source program for the compiler.

Run compiler.py by ```python3 compiler.py```.

After running compiler.py three text files will be produced:

1. `output.txt` – contains the generated intermediate code
2. `parse_tree.txt` – contains the parse tree
3. `syntax_errors.txt` – contains any syntax errors detected

---

##  Project Structure


```
# C-Minus Compiler Project Structure

c-minus-comiler/
│
├── src/
│   ├── IntermediateCodeGeneration/
│   ├── parser/
│   ├── scanner/
│   ├── test/
│   └── compiler.py          # Main program
├── testcase/
└── README.md
```

