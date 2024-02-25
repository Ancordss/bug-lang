from sly import Lexer

class MyLexer(Lexer):
    tokens = {ID, NUMBER, PLUS, MINUS, TIMES, DIVIDE}

    # Definir expresiones regulares para los tokens
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'\d+'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'

    ignore = ' \t\n'  # Ignorar espacios en blanco y saltos de línea

    # Función para ignorar comentarios
    @_(r'//.*')
    def comment(self, t):
        pass

    # Función para manejar errores
    def error(self, t):
        print("Caracter inválido:", t.value[0])
        self.index += 1

# Crear una instancia del Lexer
lexer = MyLexer()
