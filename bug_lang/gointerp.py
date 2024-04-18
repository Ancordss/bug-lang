# cinterp.py
"""
Tree-walking interpreter
TODO:here we need to convert all to go code
"""
import math
import webbrowser
from collections import ChainMap

from rich import print
from rich.console import Console
from rich.table import Table

from bug_lang.checker import Checker
from bug_lang.go_ast import *
from bug_lang.utils.stdlib import *


def _is_truthy(value):
    if isinstance(value, bool):  # If the object is already a boolean
        return value
    elif value is None:  # if the object is empty
        return False
    else:
        return True  # if the object is not empty


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value  # it sets the value for exception


class MiniCExit(BaseException):
    pass


"""
class CallError(Exception):
	pass
"""


class AttributeError(Exception):
    pass


class Function:
    def __init__(self, node, env):  # it receives the node and a context
        self.node = node
        self.env = env

    def __call__(self, interp, *args):  # it receives the interpreter and a tuple
        if self.node.parameters is not None:
            if len(args) != len(self.node.parameters):
                raise CallError(f"Interp Error. Expected {len(self.node.parameters)} arguments")
        newenv = self.env.new_child()  # we create a new environment
        if self.node.parameters is not None:
            for name, arg in zip(self.node.parameters, args):
                newenv[name] = arg

        oldenv = interp.env  # we update the interpreter's environment
        interp.env = newenv
        try:
            interp.visit(self.node.stmts)
            result = None
        except ReturnException as e:
            result = e.value
        finally:
            interp.env = oldenv  # we reset the last fully functional environment
        return result  # returns Function exceptions

    def bind(self, instance):  # I receive something called instance
        env = self.env.new_child()  # I create a new environment
        env["this"] = instance  # we add a new value for key 'this'
        return Function(self.node, env)


class Class:
    def __init__(self, name, sclass, methods):  # this is a Class framework for any class
        self.name = name
        self.sclass = sclass
        self.methods = methods

    def __str__(self):  # returns the string representation of the object
        return self.name

    def __call__(self, *args):  # this class and can be called like a function.  Class()
        this = Instance(self)
        init = self.find_method("init")
        if init:
            init.bind(this)(*args)  # I re-define the use for 'This'
        return this

    def find_method(self, name):
        meth = self.methods.get(name)
        if meth is None and self.sclass:
            return self.sclass.find_method(name)
        return meth


class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.data = {}

    def __str__(self):
        return self.klass.name + " instance"

    def get(self, name):
        if name in self.data:
            return self.data[name]
        method = self.klass.find_method(name)
        if not method:
            raise AttributeError(f"interp Error, Not defined property {name}")
        return method.bind(self)

    def set(self, name, value):
        self.data[name] = value


ThereIsBreak = False
ThereIsContinue = False


class Interpreter(Visitor):  # This is a visitor
    def __init__(self, ctxt):
        self.ctxt = ctxt  # receives a Context (the project's manager)
        self.env = ChainMap()  # generates ChainMap
        self.symbol_table = {}  # Tabla de símbolos
        self.console = Console(record=True)

    def print_symbol_table(self):
        html_output = ""  # Inicializa un string vacío para acumular las salidas HTML
        for name, info in self.symbol_table.items():
            # Establecer un título colorido y con estilo
            table = Table(title=f"Symbols for {name}", title_style="bold magenta")

            # Añadir columnas con diferentes colores y estilos
            for key in info:
                if key == "type":
                    style = "bold cyan"
                elif key == "scope":
                    style = "dim"
                elif key == "name":
                    style = "bold green"
                elif key == "parameters":
                    style = "bold yellow"
                else:
                    style = "bold red"

                table.add_column(key, style=style, justify="left")

            # Añadir una fila con los valores
            table.add_row(*[str(info[key]) for key in info])

            self.console.print(table)
            html_output += self.console.export_html()

            # Guardar la salida HTML en un archivo
            with open("symbols_table.html", "w", encoding="utf-8") as html_file:
                html_file.write(html_output)

            # Abrir el archivo en el navegador
            webbrowser.open("symbols_table.html")

    def _check_numeric_operands(self, node, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True
        else:
            self.error(node, f"Interp Error. In '{node.op}' the operands must be numerical type")

    def _check_numeric_operand(self, node, value):
        if isinstance(value, (int, float)):
            return True
        else:
            self.error(node, f"Interp Error. In '{node.op}' the operand must be numerical type")

    def error(self, position, message):
        self.ctxt.error(position, message)
        raise MiniCExit()

    # Punto de entrada alto-nivel
    def interpret(self, node, sym):
        try:
            Checker.check(node, self.ctxt)  # First, you must call the Checker
            if not self.ctxt.have_errors:
                # print("Starting interpreting \n")
                self.visit(node)
                # print("\nInterpreting finished")
            else:
                print("\n The interpreter could not start because the Checker returned errors")
        except MiniCExit as e:
            pass
        finally:
            if sym:
                self.print_symbol_table()

    def visit(self, node: Block):
        # self.env = self.env.new_child() #think about it as a typewriter, it advances one row
        # and then you have to reset the pointer
        for stmt in node.stmts:
            self.visit(stmt)
            if ThereIsBreak:
                return 0
            if ThereIsContinue:
                return 1
        # self.env = self.env.parents		#you "reset" the pointer
        self.symbol_table[type(node).__name__] = {"type": Block, "scope": self.env.maps[0], "stmst": node.stmts}

    def visit(self, node: Program):
        # self.env = self.env.new_child()
        #########################################
        for k, v in stdlibFunctions.items():
            self.env[k] = v
        #########################################
        for d in node.decl:
            self.visit(d)
        self.symbol_table[type(node).__name__] = {"type": Program, "scope": self.env.maps[0], "stmst": node.decl}
        # self.env = self.env.parents

    def visit(self, node: ClassDeclaration):
        if node.sclass:
            sclass = self.visit(node.sclass)
            env = self.env.new_child()
            env["super"] = sclass  # we accommodate this framework for any User-made class
        else:
            sclass = None
            env = self.env
        methods = {}
        for meth in node.methods:
            methods[meth.name] = Function(meth, env)
        cls = Class(node.name, sclass, methods)
        self.env[node.name] = cls
        self.symbol_table[type(node).__name__] = {
            "type": ClassDeclaration,
            "scope": self.env.maps[0],
            "name": node.name,
            "sclass": node.sclass,
            "methods": list(methods.keys()),
        }

    def visit(self, node: FuncDeclaration):
        func = Function(node, self.env)
        self.env[node.name] = func
        self.symbol_table[type(node).__name__] = {
            "type": FuncDeclaration,
            "scope": self.env.maps[0],
            "name": node.name,
            "parameters": [param for param in node.parameters],
            "stmts": node.stmts,
        }

    def visit(self, node: VarDeclaration):
        if node.expr:
            expr = self.visit(node.expr)
        else:
            expr = None
        self.env[node.name] = expr
        self.symbol_table[type(node).__name__] = {
            "type": VarDeclaration,
            "scope": self.env.maps[0],
            "name": node.name,
            "Expression": node.expr,
        }

    def visit(self, node: Print):
        print(self.visit(node.expr))
        self.symbol_table["print"] = {"type": Print, "scope": self.env.maps[0], "Expression": node.expr}

    def visit(self, node: WhileStmt):
        global ThereIsContinue
        global ThereIsBreak

        while _is_truthy(self.visit(node.cond)):
            ThereIsContinue = False
            ThereIsBreak = False
            # Something will return from Block
            flowControl = self.visit(node.body)
            if flowControl == 0:
                break
            elif flowControl == 1:
                continue
            else:
                pass
        self.symbol_table["while"] = {
            "type": WhileStmt,
            "scope": self.env.maps[0],
            "Condition": node.cond,
            "Body": node.body,
        }

    ##########################################################
    def visit(self, node: Continue):
        global ThereIsContinue
        ThereIsContinue = True
        self.symbol_table[type(node).__name__] = {"type": Continue, "scope": self.env.maps[0], "name": node.name}

    def visit(self, node: Break):
        global ThereIsBreak
        ThereIsBreak = True
        self.symbol_table[type(node).__name__] = {"type": Break, "scope": self.env.maps[0], "name": node.name}

    #########################################################

    def visit(self, node: ForStmt):
        global ThereIsContinue
        global ThereIsBreak

        self.visit(node.for_init)
        while _is_truthy(self.visit(node.for_cond)):
            ThereIsContinue = False
            ThereIsBreak = False
            # Something will return from Block
            flowControl = self.visit(node.for_body)
            if flowControl == 0:
                break
            elif flowControl == 1:
                continue
            else:
                pass
            self.visit(node.for_increment)
        self.symbol_table["for"] = {
            "type": ForStmt,
            "scope": self.env.maps[0],
            "for_init": node.for_init,
            "for_cond": node.for_cond,
            "for_increment": node.for_increment,
            "for_body": node.for_body,
        }

    def visit(self, node: IfStmt):
        test = self.visit(node.cond)
        if _is_truthy(test):
            self.visit(node.cons)
        elif node.altr:
            self.visit(node.altr)
        self.symbol_table["if"] = {
            "type": IfStmt,
            "scope": self.env.maps[0],
            "condition": node.cond,
            "follow": node.cons,
            "alternative": node.altr,
        }

    def visit(self, node: Return):
        self.symbol_table["Return"] = {"type": Return, "scope": self.env.maps[0], "Expression": node.expr}
        raise ReturnException(self.visit(node.expr))

    def visit(self, node: ExprStmt):
        self.visit(node.expr)
        self.symbol_table["ExprStmt"] = {"type": ExprStmt, "scope": self.env.maps[0], "Expression": node.expr}

    def visit(self, node: Literal):
        return node.value

    def visit(self, node: Binary):
        left = self.visit(node.left)
        right = self.visit(node.right)
        self.symbol_table[type(node).__name__] = {
            "type": Binary,
            "scope": self.env.maps[0],
            "operator": node.op,
            "left": node.left,
            "right": node.right,
        }
        if node.op == "+":
            (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(node, left, right)
            return left + right
        elif node.op == "-":
            self._check_numeric_operands(node, left, right)
            return left - right
        elif node.op == "*":
            self._check_numeric_operands(node, left, right)
            return left * right
        elif node.op == "/":
            self._check_numeric_operands(node, left, right)
            return left / right
        elif node.op == "%":
            self._check_numeric_operands(node, left, right)
            return left % right
        elif node.op == "==":
            return left == right
        elif node.op == "!=":
            return left != right
        elif node.op == "<":
            self._check_numeric_operands(node, left, right)
            return left < right
        elif node.op == ">":
            self._check_numeric_operands(node, left, right)
            return left > right
        elif node.op == "<=":
            self._check_numeric_operands(node, left, right)
            return left <= right
        elif node.op == ">=":
            self._check_numeric_operands(node, left, right)
            return left >= right
        else:
            raise NotImplementedError(f"Interp Error. Wrong Operator {node.op}")

    def visit(self, node: Logical):
        left = self.visit(node.left)
        self.symbol_table[type(node).__name__] = {
            "type": Logical,
            "scope": self.env.maps[0],
            "op": node.op,
            "left": node.left,
            "right": node.right,
        }
        if node.op == "||":
            return left if _is_truthy(left) else self.visit(node.right)
        if node.op == "&&":
            return self.visit(node.right) if _is_truthy(left) else left
        raise NotImplementedError(f"Interp Error. Wrong Operator {node.op}")

    def visit(self, node: Unary):
        self.symbol_table[type(node).__name__] = {
            "type": Unary,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }
        expr = self.visit(node.expr)
        if node.op == "-":
            self._check_numeric_operand(node, expr)
            return -expr
        elif node.op == "!":
            return not _is_truthy(expr)
        else:
            raise NotImplementedError(f"Interp Error. Wrong Operator {node.op}")

    def visit(self, node: Grouping):
        self.symbol_table[type(node).__name__] = {"type": Grouping, "scope": self.env.maps[0], "Expression": node.expr}
        return self.visit(node.expr)

    def visit(self, node: Assign):
        expr = 0
        if node.op == "=":
            expr = self.visit(node.expr)
        elif node.op == "+=":
            expr = self.env[node.name] + self.visit(node.expr)
        elif node.op == "-=":
            expr = self.env[node.name] - self.visit(node.expr)
        elif node.op == "*=":
            expr = self.env[node.name] * self.visit(node.expr)
        elif node.op == "/=":
            expr = self.env[node.name] / self.visit(node.expr)
        elif node.op == "%=":
            expr = self.env[node.name] % self.visit(node.expr)
        self.env[node.name] = expr
        self.symbol_table[type(node).__name__] = {
            "type": Assign,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }

    def visit(self, node: AssignPostfix):
        temp = self.visit(node.expr)
        expr = 0
        if node.op == "++":
            expr = self.visit(node.expr) + 1
        else:
            expr = self.visit(node.expr) - 1
        self.env[node.expr.name] = expr
        self.symbol_table["AssignPostfix"] = {
            "type": AssignPostfix,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }
        return temp

    def visit(self, node: AssignPrefix):
        expr = 0
        if node.op == "++":
            expr = self.visit(node.expr) + 1
        else:
            expr = self.visit(node.expr) - 1
        self.env[node.expr.name] = expr
        self.symbol_table["AssignPrefix"] = {
            "type": AssignPrefix,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }
        return expr

    def visit(self, node: Call):
        self.symbol_table["Call"] = {"type": Call, "scope": self.env.maps[0], "func": node.func, "Arguments": node.args}
        callee = self.visit(node.func)
        if not callable(callee):
            self.error(node.func, f"Interp Error {self.ctxt.find_source(node.func)!r} is not callable")

        if node.args is not None:
            args = [self.visit(arg) for arg in node.args]
        else:
            args = []
        try:
            return callee(self, *args)
        except CallError as err:
            self.error(node.func, str(err))

    def visit(self, node: Variable):
        self.symbol_table["Variable"] = {"type": Variable, "scope": self.env.maps[0], "name": node.name}
        return self.env[node.name]

    def visit(self, node: Set):
        self.symbol_table["Set"] = {
            "type": Set,
            "scope": self.env.maps[0],
            "object": node.obj,
            "name": node.name,
            "expression": node.expr,
        }
        obj = self.visit(node.obj)
        val = self.visit(node.expr)
        if isinstance(obj, Instance):
            obj.set(node.name, val)
            return val
        else:
            self.error(node.obj, f"Interp Error{self.ctxt.find_source(node.obj)!r} is not an instance")

    def visit(self, node: Get):
        self.symbol_table["Get"] = {"type": Get, "scope": self.env.maps[0], "object": node.obj, "name": node.name}
        obj = self.visit(node.obj)
        if isinstance(obj, Instance):
            try:
                return obj.get(node.name)
            except AttributeError as err:
                self.error(node.obj, str(err))
        else:
            self.error(node.obj, f"Interp Error{self.ctxt.find_source(node.obj)!r}  is not an instance")

    def visit(self, node: This):
        return self.env["this"]

    def visit(self, node: Super):
        distance = self.localmap[id(node)]
        sclass = self.env.maps[distance]["super"]
        this = self.env.maps[distance - 1]["this"]
        method = sclass.find_method(node.name)
        if not method:
            self.error(node.object, f"Interp Error. Not defined property {node.name!r}")
        self.symbol_table["Super"] = {"type": Super, "scope": self.env.maps[0], "name": node.name}
        return method.bind(this)
