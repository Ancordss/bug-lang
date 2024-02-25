
from .parser import parser
from .lexer import lexer

def translate_to_go(input_code):
    result = parser.parse(lexer.tokenize(input_code))
    if result:
        return f"package main\n\nfunc main() {{\n\t{result}\n}}"
    else:
        return "Error de sintaxis"

# Ejemplo de uso
input_code = "5 + 3 * 2"
go_code = translate_to_go(input_code)
print(go_code)
