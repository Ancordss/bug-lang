
from bug_lang.lexer import Lexer
import sly
from bug_lang.go_ast import *

class Parser(sly.Parser):
    debugfile="buglang.txt"
    # La lista de tokens se copia desde Lexer
    tokens = Lexer.tokens

    def __init__(self, ctxt):
        self.ctxt=ctxt

    # preceencia de operadores
    precedence = (
        # ('left', PLUSPLUS),
        # ('left', MINUSMINUS),
        # ('right', ADDEQ),
        # ('right', MINEQ),
        # ('right', TIMESEQ),
        # ('right', DIVIDEEQ),
        # ('right', MODULEEQ),
        ('right', ASSIGN),     # menor precedencia
        # ('left', OR),
        # ('left', AND),
        # ('left', EQ, NE),
        # ('left', LT, LE, GT, GE),
        # ('left', PLUS, MINUS),
        # ('left', TIMES, DIVIDE, MODULE),
        # ('right', UNARY),
    )

    # Definimos las reglas en BNF (o en EBNF)
    @_("{ declaration }")
    def program(self, p):
        return Program(p.declaration)

    @_("var_declaration",
       "statement")
    def declaration(self, p):
        return p[0]


    @_("VAR IDENT [ ASSIGN expression ] SEMI")
    def var_declaration(self, p):
        return VarDeclaration(p.IDENT, p.expression)

    @_("print_stmt")
    def statement(self, p):
        return p[0]

#########################################
    @_("PRINT LPAREN expression RPAREN SEMI")
    def print_stmt(self, p):
        return Print(p.expression)


    @_("expression ASSIGN expression")
    def expression(self, p):
        if isinstance(p.expression0, Variable):
            return Assign(p[1], p.expression0.name, p.expression1)
        elif isinstance(p.expression0, Get):
            return Set(p.expression0.obj, p.expression0.name, p.expression1)
        else:
            raise SyntaxError(f"{p.lineno}: PARSER ERROR, it was impossible to assign {p.expression0}")


    @_("factor")
    def expression(self, p):
        return p.factor

    @_("REAL", "NUM", "STRING")
    def factor(self, p):
        return Literal(p[0])


    @_("IDENT")
    def factor(self, p):
        return Variable(p.IDENT)

    def error(self, p):
        if p:
            self.ctxt.error(p, f"PARSER ERROR, Syntax error in the Token {p.type} due to: {p}")
            # Just discard the token and tell the parser it's okay.
        else:
            self.ctxt.error(p, f"PARSER ERROR, Syntax Error in EOF. Check braces, semicolons and END_IF ")
