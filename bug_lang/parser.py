from sly import Parser

class MyParser(Parser):
    tokens = MyLexer.tokens

    # Regla para expresión matemática simple: expr -> term (PLUS|MINUS term)*
    @_('term')
    def expr(self, p):
        return p.term

    @_('expr PLUS term',
       'expr MINUS term')
    def expr(self, p):
        if p[1] == '+':
            return p.expr + p.term
        elif p[1] == '-':
            return p.expr - p.term

    # Regla para término: term -> factor (TIMES|DIVIDE factor)*
    @_('factor')
    def term(self, p):
        return p.factor

    @_('term TIMES factor',
       'term DIVIDE factor')
    def term(self, p):
        if p[1] == '*':
            return p.term * p.factor
        elif p[1] == '/':
            return p.term / p.factor

    # Regla para factor: factor -> NUMBER | ID
    @_('NUMBER')
    def factor(self, p):
        return int(p.NUMBER)

    @_('ID')
    def factor(self, p):
        return p.ID

# Crear una instancia del Parser
parser = MyParser()
