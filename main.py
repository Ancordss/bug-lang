from bug_lang.lexer import lexer
from bug_lang.parser import parser
from bug_lang.translator import translate_to_go

if __name__ == "__main__":
    input_code = input("Ingrese código a traducir: ")
    go_code = translate_to_go(input_code)
    print("Código Go generado:")
    print(go_code)
