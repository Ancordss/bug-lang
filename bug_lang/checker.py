from bug_lang.go_ast import *
from bug_lang.utils.stdlib import *

# ---------------------------------------------------------------------
#  Tabla de Simbolos
# ---------------------------------------------------------------------


class Symtab:
    """
    Tabla de símbolos.

    Este es un objeto simple que sólo mantiene una hashtable (dict)
    de nombres de simbolos y los nodos de declaracion a los que se
    refieren.
    Hay una tabla de simbolos separada para cada elemento de
    código que tiene su propio contexto (por ejemplo cada función,
    clase, tendra su propia tabla de simbolos). Como resultado,
    las tablas de simbolos se pueden anidar si los elementos de
    código estan anidados y las búsquedas de las tablas de
    simbolos se repetirán hacia arriba a través de los padres
    para representar las reglas de alcance léxico.
    """

    class SymbolDefinedError(Exception):
        """
        Se genera una excepción cuando el código intenta agregar
        un simbol a una tabla donde el simbol ya se ha definido.
        Tenga en cuenta que 'definido' se usa aquí en el sentido
        del lenguaje C, es decir, 'se ha asignado espacio para el
        simbol', en lugar de una declaración.
        """

        pass

    def __init__(self, parent=None):
        """
        Crea una tabla de símbolos vacia con la tabla de
        simbolos padre dada.
        """
        self.entries = {}
        ###########################
        for k, v in stdlibFunctions.items():
            self.entries[k] = v
        ##########################
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.children = []

    def add(self, name, value):
        """
        Agrega un simbol con el valor dado a la tabla de simbolos.
        El valor suele ser un nodo AST que representa la declaración
        o definición de una función, variable (por ejemplo, Declaración
        o FuncDeclaration)
        """
        if name in self.entries:
            raise Symtab.SymbolDefinedError()
        self.entries[name] = value

    def get(self, name):
        """
        Recupera el símbol con el nombre dado de la tabla de
        simbol, recurriendo hacia arriba a traves de las tablas
        de simbol principales si no se encuentra en la actual.
        """
        if name in self.entries:
            return self.entries[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            return None


InLoop = False


class Checker(Visitor):
    """
    Visitante que crea y enlaza tablas de simbolos al AST
    """

    def _add_symbol(self, node, env: Symtab):
        """
        Intenta agregar un símbolo para el nodo dado a
        la tabla de símbolos actual, capturando cualquier
        excepción que ocurra e imprimiendo errores si es
        necesario.
        """
        try:
            env.add(node.name, node)
        except Symtab.SymbolDefinedError:
            self.error(node, f"Checker error, this symbol '{node.name}' is already defined.")

    def error(cls, position, txt):
        cls.ctxt.error(position, txt)

    @classmethod
    def check(cls, model, ctxt):
        cls.ctxt = ctxt
        check = cls()
        # print("***********Starting cheking process*********** \n")
        model.accept(check)
        # print("\n***********Cheking process finished***********")
        return check

    ###################
    # this is the gateway
    def visit(self, node: Node):
        s1 = Symtab()
        self.visit(node, s1)

    ###################
    # nodos de Declaration

    def visit(self, node: ClassDeclaration, env: Symtab):
        """
        1. Agregar el nombre de la clase a la tabla de simbolos actual
        2. Si esta definida la superclass, buscarla. Si no se encuentra,
           especificar un error.
        3. Crear una nueva tabla de simbolos (contexto)
        4. Visitar la definicion de metodos de la clase.
        """
        self._add_symbol(node, env)
        if node.sclass:
            value = env.get(node.sclass)
            if value is None:
                self.error(node, f"Checker error, parent class not found: '{node.sclass}'")
        # env = Symtab(env)
        for meth in node.methods:
            self.visit(meth, env)

    def visit(self, node: FuncDeclaration, env: Symtab):
        """
        1. Agregar el nombre de la función a la tabla de simbolos actual
        2. Crear una nueva tabla de simbolos (contexto)
        3. Agregamos los parametros a la nueva tabla de simbolos
        4. Visitar cada una de las instrucciones del cuerpo de la funcion
        """

        self._add_symbol(node, env)

        env = Symtab(env)
        # the inner environment must know about the function itself
        # to allow recursivity
        # self._add_symbol(node, env)

        # the inner environment must know about the function itself to allow recursivity
        # self._add_symbol(node.ident, env)

        if node.parameters:
            for param_name, param_type in node.parameters:
                variable = Variable(param_name, param_type)
                env.add(param_name, variable)

        self.visit(node.stmts, env)

        # if node.parameters:
        #     print(node.parameters)
        #     print(node)
        #     for param in node.parameters:
        #         self._add_symbol(Variable(param), env)
        # self.visit(node.stmts, env)

    def _add_symbol(self, name, env):
        # This method should handle adding the symbol to the environment
        env.add(name, "function")

    def visit(self, node: VarDeclaration, env: Symtab):
        """
        1. Agregar el nombre de la variable a la tabla de simbolos actual
        2. Visitar la expresion, si esta definida
        """
        self._add_symbol(node, env)
        if node.expr:
            self.visit(node.expr, env)

    # Statement
    def visit(self, node: Program, env: Symtab):
        """
        1. Visitar decl
        """
        # self._add_symbol(node, env)
        for d in node.decl:
            self.visit(d, env)

    def visit(self, node: Block, env: Symtab):
        """
        1. Visitar cada una de las instrucciones
        """
        env = Symtab(env)
        for stmt in node.stmts:
            self.visit(stmt, env)

    def visit(self, node: Print, env: Symtab):
        """
        1. Visitar expresion
        """
        self.visit(node.expr, env)

    def visit(self, node: IfStmt, env: Symtab):
        """
        1. Visitar la condicion
        2. Visitar las instrucciones del then
        3. Visitar las instrucciones del opt, si esta definido
        """
        self.visit(node.cond, env)
        # env = Symtab(env)
        self.visit(node.cons, env)
        if node.altr:
            self.visit(node.altr, env)

    def visit(self, node: WhileStmt, env: Symtab):
        """
        1. Visitar la condicion
        2. Visitar las instrucciones del cuerpo
        """
        global InLoop
        self.visit(node.cond, env)
        # env = Symtab(env)
        InLoop = True
        self.visit(node.body, env)
        InLoop = False

    def visit(self, node: ForStmt, env: Symtab):
        global InLoop
        env = Symtab(env)
        self.visit(node.for_init, env)
        self.visit(node.for_cond, env)
        self.visit(node.for_increment, env)
        InLoop = True
        self.visit(node.for_body, env)
        InLoop = False

    def visit(self, node: Return, env: Symtab):
        """
        1. Visitar expresion
        """
        if node.expr:
            self.visit(node.expr, env)

    ###################################################

    def visit(self, node: Continue, env: Symtab):
        if not InLoop:
            self.error(node, f"Checker error, '{node.name}' not in a loop")

    def visit(self, node: Break, env: Symtab):
        if not InLoop:
            self.error(node, f"Checker error, '{node.name}' not in a loop")

    ##################################################

    def visit(self, node: ExprStmt, env: Symtab):
        """
        1. Visitar expresion
        """
        if node.expr is not None:
            self.visit(node.expr, env)

    # Expression

    def visit(self, node: Literal, env: Symtab):
        """
        No se hace nada
        """
        pass

    def visit(self, node: Binary, env: Symtab):
        """
        1. Visitar el hijo izquierdo
        2. Visitar el hijo derecho
        """
        self.visit(node.left, env)
        self.visit(node.right, env)

    def visit(self, node: Logical, env: Symtab):
        """
        1. Visitar el hijo izquierdo
        2. Visitar el hijo derecho
        """

        self.visit(node.left, env)
        self.visit(node.right, env)

    def visit(self, node: Unary, env: Symtab):
        """
        1. Visitar expresion
        """
        self.visit(node.expr, env)

    def visit(self, node: Grouping, env: Symtab):
        """
        1. Visita Expresion
        """
        self.visit(node.expr, env)

    def visit(self, node: Variable, env: Symtab):
        """
        1. Buscar nombre en la tabla de simbolos (contexto actual)
        """
        result = env.get(node.name)
        if result is None:
            self.error(node, f"Checker error, the variable '{node.name}' is not defined")

    def visit(self, node: Assign, env: Symtab):
        """
        1. Verificar "node.var" en la symtab actual
                Ahora node.var se guarda como una variable, por lo que
                si se visita node.var, cuando entre al nodo tipo variable
                se determina si esta o no definido dicha variable
        2. Visitar/Recorrer "node.expr"
        """
        # DON'T DO: self.visit(node.name, env)
        # I just have to check if it's already defined before
        result = env.get(node.name)
        if result is None:
            self.error(node, f"Checker error. Assign left symbol '{node.name}' is not defined")

        self.visit(node.expr, env)

    def visit(self, node: AssignPostfix, env: Symtab):
        self.visit(node.expr, env)

    def visit(self, node: AssignPrefix, env: Symtab):
        self.visit(node.expr, env)

    def visit(self, node: Call, env: Symtab):
        """
        1. Buscar la funcion en la tabla de simbolos
        2. Validar el numero de argumentos pasados
        3. Visitar las expr de los argumentos
        """

        self.visit(node.func, env)
        result = env.get(node.func.name)
        if node.args is not None:
            for arg in node.args:
                self.visit(arg, env)

        if result is FuncDeclaration:
            if result is not None:
                if result.parameters is not None:
                    if len(result.parameters) != len(node.args):
                        self.error(node, "Checker error, given arguments don't match expected arguments in Call")

    def visit(self, node: Get, env: Symtab):
        """
        1. Buscar objeto en la tabla de simbolos (contexto actual)
        2. Buscar nombre en la tabla de simbolos (contexto actual)
        """
        self.visit(node.obj, env)
        nam = env.get(node.name)
        if nam is None:
            self.error(node, f"Checker error. Get symbol '{node.name}' is not defined")

    def visit(self, node: Set, env: Symtab):
        """
        1. Buscar objeto en la tabla de simbolos (contexto actual)
        2. Buscar nombre en la tabla de simbolos (contexto actual)
        3. Visitar expresion
        """
        self.visit(node.obj, env)
        nam = env.get(node.name)

        if nam is None:
            self.error(node, f"Checker Error. Set symbol '{node.name}' is not defined")

    def visit(self, node: This, env: Symtab):
        """
        No hacemos nada (debe de estar en un contexto de una clase)
        """
        pass

    def visit(self, node: Super, env: Symtab):
        """
        1. Buscar nombre en la tabla de simbolos (contexto actual)
        Debe de estar en el contexto de una clase
        """
        pass
