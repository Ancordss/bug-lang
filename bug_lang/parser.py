import sly
from rich.console import Console
from rich.table import Table

from bug_lang.go_ast import *
from bug_lang.lexer import Lexer


class Parser(sly.Parser):
    # debugfile="buglang.txt"
    # La lista de tokens se copia desde Lexer
    tokens = Lexer.tokens

    def __init__(self, ctxt):
        super().__init__()
        self.ctxt = ctxt
        self.token_log = []
        self.last_token_end = 0

    def log_token(self, token):
        self.token_log.append(token)

    def create_token_log_table(self):
        table = Table(title="Result Objects")
        # Aquí definirías las columnas que deseas para tus objetos
        table.add_column("Function Name")
        table.add_column("Parameters")
        table.add_column("Statements")

        for obj in self.token_log:
            if isinstance(obj, FuncDeclaration):
                table.add_row(obj.name, obj.parameters, obj.stmts)
            elif isinstance(obj, ForStmt):
                table.add_row(obj.for_init, obj.for_cond, obj.for_increment, obj.for_body)
            # Añade más tipos según necesites

        return table

    # preceencia de operadores
    precedence = (
        ("left", PLUSPLUS),
        ("left", MINUSMINUS),
        ("right", ADDEQ),
        ("right", MINEQ),
        ("right", TIMESEQ),
        ("right", DIVIDEEQ),
        ("right", MODULEEQ),
        ("right", ASSIGN),  # menor precedencia
        ("left", OR),
        ("left", AND),
        ("left", EQ, NE),
        ("left", LT, LE, GT, GE),
        ("left", PLUS, MINUS),
        ("left", TIMES, DIVIDE, MODULE),
        ("right", UNARY),
    )

    # Definimos las reglas en BNF (o en EBNF)
    @_("{ declaration }")
    def program(self, p):
        self.log_token((p.declaration))
        return Program(p.declaration)

    @_("class_declaration", "func_declaration", "var_declaration", "statement")
    def declaration(self, p):
        return p[0]

    @_("CLASS IDENT [ LPAREN LT IDENT RPAREN ] LBRACE { function } RBRACE ")
    def class_declaration(self, p):
        return ClassDeclaration(p.IDENT0, p.IDENT1, p.function)

    @_("FUN function")
    def func_declaration(self, p):
        return p[1]

    @_("VAR  STRING_TYPE|INT_TYPE|FLOAT_TYPE  IDENT [ ASSIGN expression ] SEMI")
    def var_declaration(self, p):
        return VarDeclaration(p.IDENT, p.expression)

    @_(
        "expr_stmt",
        "for_stmt",
        "if_stmt",
        "print_stmt",
        "return_stmt",
        "while_stmt",
        "block",
        "continue_stmt",
        "break_stmt",
    )
    def statement(self, p):
        return p[0]

    @_("expression SEMI")
    def expr_stmt(self, p):
        return ExprStmt(p.expression)

    @_("FOR LPAREN for_initialize [ expression ] SEMI [ expression ] RPAREN statement")
    def for_stmt(self, p):
        return ForStmt(p.for_initialize, p.expression0, p.expression1, p.statement)

    @_("FOR LPAREN SEMI [ expression ] SEMI [ expression ] RPAREN statement")
    def for_stmt(self, p):
        return ForStmt(None, p.expression0, p.expression1, p.statement)

    @_("var_declaration", "expr_stmt")
    def for_initialize(self, p):
        return p[0]

    #########################################
    @_("CONTINUE SEMI")
    def continue_stmt(self, p):
        return Continue(p[0])

    @_("BREAK SEMI")
    def break_stmt(self, p):
        return Break(p[0])

    #########################################
    @_("IF LPAREN [ expression ] RPAREN statement [ ELSE statement ] END_IF")
    def if_stmt(self, p):
        return IfStmt(p.expression, p.statement0, p.statement1)

    #########################################
    @_("PRINT LPAREN expression RPAREN SEMI")
    def print_stmt(self, p):
        return Print(p.expression)

    @_("RETURN [ expression ] SEMI")
    def return_stmt(self, p):
        return Return(p.expression)

    @_("WHILE LPAREN expression RPAREN statement")
    def while_stmt(self, p):
        return WhileStmt(p.expression, p.statement)

    @_("LBRACE { declaration } RBRACE")
    def block(self, p):
        return Block(p.declaration)

    @_(
        "expression ASSIGN expression",
        "expression ADDEQ expression",
        "expression MINEQ expression",
        "expression TIMESEQ expression",
        "expression DIVIDEEQ expression",
        "expression MODULEEQ expression",
    )
    def expression(self, p):
        if isinstance(p.expression0, Variable):
            return Assign(p[1], p.expression0.name, p.expression1)
        elif isinstance(p.expression0, Get):
            return Set(p.expression0.obj, p.expression0.name, p.expression1)
        else:
            raise SyntaxError(f"{p.lineno}: PARSER ERROR, it was impossible to assign {p.expression0}")

    @_("expression OR  expression", "expression AND expression")
    def expression(self, p):
        return Logical(p[1], p.expression0, p.expression1)

    @_(
        "expression PLUS expression",
        "expression MINUS expression",
        "expression TIMES expression",
        "expression DIVIDE expression",
        "expression MODULE expression",
        "expression LT  expression",
        "expression LE  expression",
        "expression GT  expression",
        "expression GE  expression",
        "expression EQ  expression",
        "expression NE  expression",
    )
    def expression(self, p):
        return Binary(p[1], p.expression0, p.expression1)

    @_("factor")
    def expression(self, p):
        return p.factor

    @_("REAL", "NUM", "STRING")
    def factor(self, p):
        return Literal(p[0])

    @_("TRUE", "FALSE")
    def factor(self, p):
        return Literal(p[0] == "true")

    @_("NIL")
    def factor(self, p):
        return Literal(None)

    @_("THIS")
    def factor(self, p):
        return This()

    @_("IDENT")
    def factor(self, p):
        return Variable(p.IDENT, None)

    @_("SUPER POINT IDENT")
    def factor(self, p):
        return Super(p.IDENT)

    @_("factor POINT IDENT")
    def factor(self, p):
        return Get(p.factor, p.IDENT)

    @_("factor LPAREN [ arguments ] RPAREN ")
    def factor(self, p):
        return Call(p.factor, p.arguments)

    @_(" LPAREN expression RPAREN ")
    def factor(self, p):
        return Grouping(p.expression)

    @_("MINUS factor %prec UNARY", "NOT factor %prec UNARY")
    def factor(self, p):
        return Unary(p[0], p.factor)

    ##################################################################################################
    @_("factor PLUSPLUS", "factor MINUSMINUS")
    def factor(self, p):
        return AssignPostfix(p[1], p.factor)

    @_("PLUSPLUS factor", "MINUSMINUS factor")
    def factor(self, p):
        return AssignPrefix(p[0], p.factor)

    ##################################################################################################

    @_("IDENT LPAREN [ parameters ] RPAREN { type } block")
    def function(self, p):
        return FuncDeclaration(p.IDENT, p.type, p.parameters, p.block)

    # Definición de parámetros con tipos
    @_("IDENT COLON type { COMMA IDENT COLON type }")
    def parameters(self, p):
        first_param = (p.IDENT0, p.type0)
        try:
            other_params = [(p[i], p[i + 2]) for i in range(3, len(p), 4)]
            return [first_param] + other_params
        except:
            return [first_param]

    @_("expression { COMMA expression }")
    def arguments(self, p):
        return [p.expression0] + p.expression1

    def token(self, tok):
        # Registramos el token
        self.log_token(tok)
        return tok

    @_("STRING_TYPE")
    def type(self, p):
        return p.STRING_TYPE

    @_("INT_TYPE")
    def type(self, p):
        return p.INT_TYPE

    @_("FLOAT_TYPE")
    def type(self, p):
        return p.FLOAT_TYPE

    # def save_token_log_as_html(self, output_file="token_log.html"):
    #     console = Console(record=True)
    #     console.print("\n\n[bold blue]********** TOKEN LOG **********[/bold blue]\n")

    #     Crear la tabla de la bitácora
    #     table = self.create_token_log_table()

    #     Imprimir la tabla usando Rich
    #     console.print(table)

    #     Obtener la salida como HTML usando Rich
    #     html_output = console.export_html()

    #     Guardar la salida HTML en un archivo
    #     with open(output_file, "w", encoding="utf-8") as html_file:
    #         html_file.write(html_output)

    def error(self, p):
        if p:
            error_message = f"PARSER ERROR at line {p.lineno}, column {p.index}: Syntax error near '{p.value}'"
            self.ctxt.error(p.lineno, p.index, error_message)
        else:
            error_message = "PARSER ERROR: Syntax error at EOF"
            self.ctxt.error(None, None, error_message)
