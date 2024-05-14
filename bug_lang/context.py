# context.py
"""
Clase de alto nivel que contiene todo sobre el análisis/ejecución
de un programa.

Sirve como repositorio de información sobre el programa, incluido
el código fuente, informe de errores, etc.
"""
from rich import print

import bug_lang.go_ast as go_ast
from bug_lang.gointerp import Interpreter
from bug_lang.lexer import Lexer
from bug_lang.parser import Parser


class Context:
    def __init__(self):
        self.errors = []
        self.lexer = Lexer(self)
        self.parser = Parser(self)
        self.interp = Interpreter(self)
        self.source = ""
        self.ast = None
        self.have_errors = False

    def parse(self, source):  # makes work the Parser
        self.have_errors = False
        self.source = source
        self.ast = self.parser.parse(self.lexer.tokenize(self.source))

    def run(self, sym):  # makes work the interpreter
        if not self.have_errors:
            
            return self.interp.interpret(self.ast, sym)

    def find_source(self, node):  # it searches the line
        indices = self.parser.index_position(node)
        if indices:
            return self.source[indices[0] : indices[1]]
        else:
            return f"{type(node).__name__} (Sorry, source not available)"

    def error(self, lineno, index, message):
        if lineno is None or index is None:
            # Maneja los casos donde lineno o index son None
            print(f"Error: {message}")
            print("Location unknown")
        else:
            line_start = self.source.rfind("\n", 0, index) + 1
            line_end = self.source.find("\n", index)
            line_end = line_end if line_end != -1 else len(self.source)
            marker = " " * (index - line_start) + "^"

            # Muestra el error con ubicación precisa
            print(f"Error at line {lineno}, column {index - line_start + 1}: {message}")
            print(self.source[line_start:line_end])
            print(marker)

        self.have_errors = True
        self.errors.append(f'{lineno if lineno is not None else "Unknown"}: {message}')
