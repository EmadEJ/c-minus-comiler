#  C-Minus Compiler  
 A one-pass compiler for the C-Minus language — implemented in Python.  

---

##  Authors
- **Emad Emamjomeh**  
- **Amirhossein Maleck Mohammadi** 

---

This project implements a one-pass compiler for a simplified version of the C programming language.  
It was developed as part of the Compiler Design (40-414) course at Sharif University of Technology during Spring 2025.

The compiler is built in **Python 3.8**, with `anytree` library.  
It consists of three main phases:

1. **Scanner (Lexical Analyzer)**  
2. **Parser (Predictive Top-Down Parser)**  
3. **Intermediate Code Generator**  

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

