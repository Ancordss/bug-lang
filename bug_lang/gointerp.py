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


class TACGenerator:
    def __init__(self):
        self.code = []  # Lista para almacenar las líneas de código TAC
        self.temp_count = 0  # Contador para variables temporales

    def generate_temp(self):
        """Genera un nuevo nombre de variable temporal."""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def add_line(self, line):
        """Añade una línea de código TAC."""
        self.code.append(line)

    def get_code(self):
        """Devuelve todas las líneas de código TAC acumuladas."""
        print(self.code)
        return "\n".join(self.code)


class Function:
    def __init__(self, node, env,generator):  # it receives the node and a context
        self.node = node
        self.env = env
        self.generator = generator

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
        function_label = self.generator.generate_temp()
        try:
            try:
                parameters = { "parameters": [param for param in self.node.parameters],}
                #print(self.node)
            except:
                parameters = ""
            
            self.generator.add_line(f"label {function_label} starts call {self.node.name}, {parameters}")
            interp.visit(self.node.stmts)
            self.generator.add_line(f"label {function_label} ends call {self.node.name}")
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
        self.generator = TACGenerator()  # Instancia de TACGenerator
        self.loop_labels = []  # Pila para gestionar las etiquetas de los bucles

    def push_loop_labels(self, start_label, end_label):
        """ Empuja un nuevo conjunto de etiquetas de bucle a la pila. """
        self.loop_labels.append((start_label, end_label))

    def pop_loop_labels(self):
        """ Retira el conjunto de etiquetas de bucle actual de la pila. """
        return self.loop_labels.pop() if self.loop_labels else (None, None)

    def current_loop_labels(self):
        """ Obtiene el conjunto de etiquetas de bucle actual sin retirarlo. """
        return self.loop_labels[-1] if self.loop_labels else (None, None)
        

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
            tac_code = self.get_tac_code()
            with open('tac-code', 'w') as file:
                file.write(tac_code)
            print(f"Código TAC escrito en tac-code")
            

    def visit(self, node: Block):
        # self.env = self.env.new_child() #think about it as a typewriter, it advances one row
        # and then you have to reset the pointer
        #print(node.stmts)
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

    def visit(self, node: ClassDeclaration): ## TODO: tac generator
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
        class_name = node.name
        self.env[node.name] = cls
        self.symbol_table[type(node).__name__] = {
            "type": ClassDeclaration,
            "scope": self.env.maps[0],
            "name": node.name,
            "sclass": node.sclass,
            "methods": list(methods.keys()),
        }
        self.generator.add_line(f"define class {class_name} extends {sclass if sclass else 'None'} with methods {list(methods.keys())}")

    def visit(self, node: FuncDeclaration): ## TODO: tac generator
        # func_label = f"func_{node.name}"
        # self.generator.add_line(f"label func {func_label}:")

        # # Agregar código TAC para la entrada de la función, p. ej., configuración del stack
        # self.generator.add_line(f"# Setup for function {node.name}")

        # # Visitar y generar TAC para cada declaración/operación en el cuerpo de la función
        # print(node.stmts)
        # for stmt in node.stmts:
        #     self.visit(stmt)

        # # Agregar código TAC para la salida de la función, p. ej., limpiar el stack
        # self.generator.add_line(f"# Teardown for function {node.name}")
        # self.generator.add_line("return")


        func = Function(node, self.env, self.generator)
        self.env[node.name] = func
        try: 
            self.symbol_table[type(node).__name__] = {
                "type": FuncDeclaration,
                "scope": self.env.maps[0],
                "name": node.name,
                "parameters": [param for param in node.parameters],
                "stmts": node.stmts,
            }
        except:
            self.symbol_table[type(node).__name__] = {
            "type": FuncDeclaration,
            "scope": self.env.maps[0],
            "name": node.name,
            "stmts": node.stmts,
        }

    def visit(self, node: VarDeclaration): ### need tac generator
        if node.expr:
            print(f"node var d {node}, {node.expr}")
            if isinstance(node.expr, Literal):
                expr = self.visit(node.expr)
            else:
                expr = self.visit_tac(node.expr)
            tac_line = f"label var {node.name} = {expr}"
        else:
            expr = None
            expr1 = 'nil'  # O '0' si prefieres representar una inicialización a cero
            tac_line = f"{node.name} = {expr1}"
        
        self.generator.add_line(tac_line)
        self.env[node.name] = expr
        self.symbol_table[type(node).__name__] = {
            "type": VarDeclaration,
            "scope": self.env.maps[0],
            "name": node.name,
            "Expression": node.expr,
        }

    def visit(self, node: Print): #TODO: tac generator
        try:
            print(f"asdffs {node.expr}")
            expr_value = self.visit(node.expr)
        except:
            expr_value = 'nil'
        # Generar una línea de TAC que representa la operación de impresión
        # Asumiendo que tenemos una función o instrucción 'print' en el destino de TAC
        self.generator.add_line(f"label print {expr_value}")
        self.symbol_table["print"] = {"type": Print, "scope": self.env.maps[0], "Expression": node.expr}

    def visit(self, node: WhileStmt): ## TODO: need tac genetarot
        label_loop_start = self.generator.generate_temp()
        label_loop_end = self.generator.generate_temp()
        
        self.generator.add_line(f"label while {label_loop_start}:v")

        # Evaluar la condición del bucle
        condition = self.visit_tac(node.cond)
        
        self.generator.add_line(f"if not {condition} goto {label_loop_end}")

        # Visitar el cuerpo del bucle
        self.visit(node.body)

        # Verificar si hay instrucciones de control de flujo (break o continue)
        # Aquí se debe manejar el control del flujo, pero en TAC se manejará a nivel de optimización de saltos
        # Puesto que no implementamos directamente el control aquí, simplificamos el flujo para TAC
        
        


        
        global ThereIsContinue
        global ThereIsBreak

        
        while _is_truthy(self.visit(node.cond)):
            ThereIsContinue = False
            ThereIsBreak = False
            flowControl = self.visit(node.body)
            if flowControl == 0:
                break
            elif flowControl == 1:
                continue
            else:
                pass
        
        self.generator.add_line(f"goto {label_loop_start}")

        # Marcar el final del bucle
        self.generator.add_line(f"label while end {label_loop_end}")
        
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
        if self.loop_start_label:
            self.generator.add_line(f"goto {self.loop_start_label}")
        else:
            raise Exception("Syntax error: 'continue' not within a loop")
        self.symbol_table[type(node).__name__] = {"type": Continue, "scope": self.env.maps[0], "name": node.name}

    def visit(self, node: Break): # TODO:### need tac generator
        global ThereIsBreak
        ThereIsBreak = True
        if self.loop_end_label:
            self.generator.add_line(f"goto {self.loop_end_label}")
        else:
            raise Exception("Syntax error: 'break' not within a loop")
        self.symbol_table[type(node).__name__] = {"type": Break, "scope": self.env.maps[0], "name": node.name}

    #########################################################

    def visit(self, node: ForStmt): ## TODO: need tac genereator
        print('llegue aqui')
        self.visit(node.for_init)
        
        # Generar etiquetas para el control del bucle
        label_loop_start = self.generator.generate_temp()  # Etiqueta para el inicio del bucle
        label_continue = self.generator.generate_temp()    # Etiqueta para la parte de incremento
        label_loop_end = self.generator.generate_temp()    # Etiqueta para el final del bucle
        
        

        # Empujar las etiquetas a la pila para manejar 'break' y 'continue'
        self.push_loop_labels(label_continue, label_loop_end)

        # Marcar el inicio del bucle con la etiqueta correspondiente
        self.generator.add_line(f"{label_loop_start} for:")

        # Evaluar la condición del bucle for y preparar el salto basado en ella
        print(node.for_cond)
        condition = self.visit(node.for_cond)
        condition = self.visit_tac(node.for_cond)
        self.generator.add_line(f"if not {condition} goto {label_loop_end}")

        # Visitar el cuerpo del bucle
       
        self.visit(node.for_body)
        

        # Etiqueta para 'continue', se coloca antes del incremento
        self.generator.add_line(f"label continue {label_continue}:")

        # Generar código para el incremento
        print(node.for_increment)
        self.visit(node.for_increment)

        # Salto al inicio del bucle para continuar la iteración
        self.generator.add_line(f"goto {label_loop_start}")

        # Marcar el final del bucle con la etiqueta correspondiente
        self.generator.add_line(f"label for end {label_loop_end}:")

        # Retirar las etiquetas de la pila al salir del bucle
        self.pop_loop_labels()
    
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
    
    def get_tac_code(self):
        return self.generator.get_code()


    def visit(self, node: IfStmt):## TODO: need tack generator
        #print(node.cond)
        
        label_start = self.generator.generate_temp() 
        label_true = self.generator.generate_temp()  # Etiqueta para la ejecución verdadera
        label_end = self.generator.generate_temp()  # Etiqueta final
        test1 = self.visit_tac(node.cond)
        self.visit(node.cond)
        print(f"asdf {node.altr}")
        # Condición y salto si es verdadero
        self.generator.add_line(f"{label_start} if {test1} goto {label_true}")
            
        #if _is_truthy(test):
        
        self.generator.add_line(f"{label_true}:v")
        self.visit(node.cons)
            
        # elif node.altr:
        self.generator.add_line(f"else goto {label_end}")
        self.generator.add_line(f"{label_end}:v")
        self.visit(node.altr)
            
            
        self.generator.add_line(f"label if end {label_start}:")
         
        self.symbol_table["if"] = {
            "type": IfStmt,
            "scope": self.env.maps[0],
            "condition": node.cond,
            "follow": node.cons,
            "alternative": node.altr,
        }

    def visit(self, node: Return): #TODO: tac generator
        self.generator.add_line(f"return {self.visit(node.expr)}")
        self.symbol_table["Return"] = {"type": Return, "scope": self.env.maps[0], "Expression": node.expr}
        #raise ReturnException(self.visit(node.expr))

    def visit(self, node: ExprStmt):
        self.visit(node.expr)
        self.symbol_table["ExprStmt"] = {"type": ExprStmt, "scope": self.env.maps[0], "Expression": node.expr}

    def visit(self, node: Literal):
        return node.value

    def visit(self, node: Binary): ############ need tac generator
        left = self.visit(node.left)
        right = self.visit(node.right)
        #result = self.generator.generate_temp()
        #self.generator.add_line(f"{result} = {node.left} {node.op} {node.right}")
        # result = self.generator.generate_temp()
        # self.generator.add_line(f"{result} = {left} {node.op} {right}")

        
        self.symbol_table[type(node).__name__] = {
            "type": Binary,
            "scope": self.env.maps[0],
            "operator": node.op,
            "left": node.left,
            "right": node.right,
        }
        # if node.op == "+":
        #     (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(node, left, right)
        #     return left + right
        # elif node.op == "-":
        #     self._check_numeric_operands(node, left, right)
        #     return left - right
        # elif node.op == "*":
        #     self._check_numeric_operands(node, left, right)
        #     return left * right
        # elif node.op == "/":
        #     self._check_numeric_operands(node, left, right)
        #     return left / right
        # elif node.op == "%":
        #     self._check_numeric_operands(node, left, right)
        #     return left % right
        # elif node.op == "==":
        #     return left == right
        # elif node.op == "!=":
        #     return left != right
        # elif node.op == "<":
        #     self._check_numeric_operands(node, left, right)
        #     return left < right
        # elif node.op == ">":
        #     self._check_numeric_operands(node, left, right)
        #     return left > right
        # elif node.op == "<=":
        #     self._check_numeric_operands(node, left, right)
        #     return left <= right
        # elif node.op == ">=":
        #     self._check_numeric_operands(node, left, right)
        #     return left >= right
        # else:
        #     raise NotImplementedError(f"Interp Error. Wrong Operator {node.op}")
        

    def visit(self, node: Logical):
        left = self.visit(node.left)
        # Preparamos una variable temporal para el resultado de la operación lógica
        result = self.generator.generate_temp()

        # Generamos etiquetas para control de flujo condicional
        label_true = self.generator.generate_temp()
        label_end = self.generator.generate_temp()
        self.symbol_table[type(node).__name__] = {
            "type": Logical,
            "scope": self.env.maps[0],
            "op": node.op,
            "left": node.left,
            "right": node.right,
        }
        if node.op == "||":
             # Si 'left' es verdadero, entonces el resultado es verdadero
            self.generator.add_line(f"if {left} goto {label_true}")
            # Si no, evaluamos 'right'
            right = self.visit(node.right)
            self.generator.add_line(f"{result} = {right}")
            self.generator.add_line(f"goto {label_end}")
            self.generator.add_line(f"label {label_true}:")
            self.generator.add_line(f"{result} = 1")  # True
            #return left if _is_truthy(left) else self.visit(node.right)
        if node.op == "&&":
             # Si 'left' es falso, entonces el resultado es falso
            self.generator.add_line(f"if not {left} goto {label_true}")
            # Si no, evaluamos 'right'
            right = self.visit(node.right)
            self.generator.add_line(f"{result} = {right}")
            self.generator.add_line(f"goto {label_end}")
            self.generator.add_line(f"label {label_true}:")
            self.generator.add_line(f"{result} = 0")  # False
            
            #return self.visit(node.right) if _is_truthy(left) else left
        raise NotImplementedError(f"Interp Error. Wrong Operator {node.op}")

    def visit(self, node: Unary): #### need tac generator
        self.symbol_table[type(node).__name__] = {
            "type": Unary,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }
        expr = self.visit(node.expr)
        result = self.generator.generate_temp()
        if node.op == "-":
            self._check_numeric_operand(node, expr)
            self.generator.add_line(f"label unary {result} = -{expr}")
            #return -expr
        elif node.op == "!":
            self.generator.add_line(f"label unary {result} = !{expr}")
            #return not _is_truthy(expr)
        
        else:
            raise NotImplementedError(f"Interp Error. Wrong Operator {node.op}")

    def visit(self, node: Grouping):
        self.symbol_table[type(node).__name__] = {"type": Grouping, "scope": self.env.maps[0], "Expression": node.expr}
        #return self.visit(node.expr)

    def visit(self, node: Assign): #### need tac generator
        expr = 0
        self.visit(node.expr)
        try:
            expr_value = self.visit_tac(node.expr)
        except:
            expr_value = self.visit(node.expr)
        tag = self.generator.generate_temp()
        self.generator.add_line(f"{tag} assign {node.name} {node.op} {expr_value}")

    # Crear una variable temporal para el resultado de la expresión
        # result_temp = self.generator.generate_temp()
        # if node.op == "=":
        #     #self.generator.add_line(f"label assign {node.name} = {expr_value}")
        #     expr = self.visit(node.expr)
        # elif node.op == "+=":
        #     #self.generator.add_line(f"label assign {result_temp} = {node.name} + {expr_value}")
        #     #self.generator.add_line(f"label assign {node.name} = {result_temp}")
        #     expr = self.env[node.name] + self.visit(node.expr)
        # elif node.op == "-=":
        #     #self.generator.add_line(f"label assign {result_temp} = {node.name} - {expr_value}")
        #     #self.generator.add_line(f"label assign {node.name} = {result_temp}")
        #     expr = self.env[node.name] - self.visit(node.expr)
        # elif node.op == "*=":
        #     #self.generator.add_line(f"label assign {result_temp} = {node.name} * {expr_value}")
        #     #self.generator.add_line(f"label assign {node.name} = {result_temp}")
        #     expr = self.env[node.name] * self.visit(node.expr)
        # elif node.op == "/=":
        #     #self.generator.add_line(f"label assign {result_temp} = {node.name} / {expr_value}")
        #     #self.generator.add_line(f"label assign {node.name} = {result_temp}")
        #     expr = self.env[node.name] / self.visit(node.expr)
        # elif node.op == "%=":
        #     #self.generator.add_line(f"label assign {result_temp} = {node.name} % {expr_value}")
        #     #self.generator.add_line(f"label assign {node.name} = {result_temp}")
        #     expr = self.env[node.name] % self.visit(node.expr)
        self.env[node.name] = expr
        self.symbol_table[type(node).__name__] = {
            "type": Assign,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }

    def visit(self, node: AssignPostfix): ## need tac generator
        temp = self.visit(node.expr)
        tag = self.generator.generate_temp()
        expr = 0
        self.generator.add_line(f"{tag} {node.expr} {node.op} ")
        # if node.op == "++":
        #     expr = self.visit(node.expr) + 1
        # else:
        #     expr = self.visit(node.expr) - 1
        self.env[node.expr.name] = expr
        self.symbol_table["AssignPostfix"] = {
            "type": AssignPostfix,
            "scope": self.env.maps[0],
            "op": node.op,
            "Expression": node.expr,
        }
        #return temp

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
        #return expr

    def visit(self, node: Call): ## TODO: tac generator
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

    def visit(self, node: Set): #TODO: tac generator
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

    def visit(self, node: Get): #TODO: tac generator
        self.symbol_table["Get"] = {"type": Get, "scope": self.env.maps[0], "object": node.obj, "name": node.name}
        obj = self.visit(node.obj)
        if isinstance(obj, Instance):
            try:
                return obj.get(node.name)
            except AttributeError as err:
                self.error(node.obj, str(err))
        else:
            self.error(node.obj, f"Interp Error{self.ctxt.find_source(node.obj)!r}  is not an instance")

    def visit(self, node: This): #TODO: tac generator
        return self.env["this"]

    def visit(self, node: Super):#TODO: tac generator
        distance = self.localmap[id(node)]
        sclass = self.env.maps[distance]["super"]
        this = self.env.maps[distance - 1]["this"]
        method = sclass.find_method(node.name)
        if not method:
            self.error(node.object, f"Interp Error. Not defined property {node.name!r}")
        self.symbol_table["Super"] = {"type": Super, "scope": self.env.maps[0], "name": node.name}
        return method.bind(this)
    
    
    def visit_tac(self, node: Binary): ############ need tac generator
        left = self.visit(node.left)
        right = self.visit(node.right)
        #self.generator.add_line(f"{result} = {left} {node.op} {right}")
        print(f"node.op {node.left}")
        return f"{left} {node.op} {right}"
    