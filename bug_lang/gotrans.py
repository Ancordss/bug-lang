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
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    else:
        return True

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BugLangCExit(BaseException):
    pass

class AttributeError(Exception):
    pass

class TACGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0

    def generate_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def add_line(self, line):
        self.code.append(line)

    def get_code(self):
        return "\n".join(self.code)

class Function:
    def __init__(self, node, env, generator):
        self.node = node
        self.env = env
        self.generator = generator

    def __call__(self, interp, *args):
        if self.node.parameters is not None and len(args) != len(self.node.parameters):
            raise Exception(f"Expected {len(self.node.parameters)} arguments, got {len(args)}")
        new_env = self.env.new_child()
        for name, arg in zip(self.node.parameters, args):
            new_env[name] = arg
        old_env = interp.env
        interp.env = new_env
        result = None
        try:
            result = interp.visit(self.node.stmts)
        except ReturnException as e:
            result = e.value
        finally:
            interp.env = old_env
        return result

    def bind(self, instance):
        env = self.env.new_child()
        env["this"] = instance
        return Function(self.node, env, self.generator)

class Class:
    def __init__(self, name, sclass, methods):
        self.name = name
        self.sclass = sclass
        self.methods = methods

    def __call__(self, *args):
        instance = Instance(self)
        init = self.find_method("init")
        if init:
            init.bind(instance)(*args)
        return instance

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        elif self.sclass:
            return self.sclass.find_method(name)
        return None

class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.data = {}

    def get(self, name):
        if name in self.data:
            return self.data[name]
        method = self.klass.find_method(name)
        if method:
            return method.bind(self)
        raise AttributeError(f"Property {name} not defined")

    def set(self, name, value):
        self.data[name] = value

class Interpreter:
    def __init__(self, ctxt):
        self.ctxt = ctxt
        self.env = ChainMap()
        self.symbol_table = {}
        self.console = Console(record=True)
        self.generator = TACGenerator()

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit method for {type(node).__name__}')

    def visit_Binary(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = self.generator.generate_temp()
        self.generator.add_line(f"{result} = {left} {node.op} {right}")
        return result


    def visit_VarDeclaration(self, node: VarDeclaration):
        expr = self.visit(node.expr) if node.expr else 'nil'
        self.generator.add_line(f"{node.name} = {expr}")
        return node.name

    def visit_Print(self, node:Print):
        expr = self.visit(node.expr)
        self.generator.add_line(f"print({expr})")

    def visit_IfStmt(self, node):
        cond_result = self.visit(node.cond)
        label_true = self.generator.generate_temp()
        label_end = self.generator.generate_temp()
        self.generator.add_line(f"if {cond_result} goto {label_true}")
        self.generator.add_line(f"goto {label_end}")
        self.generator.add_line(f"label {label_true}:")
        self.visit(node.cons)
        self.generator.add_line(f"label {label_end}:")
        if node.altr:
            self.visit(node.altr)

# Use your existing code to initialize and run the interpreter as needed.

# Example usage:
# interpreter = Interpreter(your_context)
# program = your_ast_root  # Root node of your AST
# interpreter.visit(program)
# print(interpreter.generator.get_code())
