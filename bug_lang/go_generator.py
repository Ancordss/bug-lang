"""
Go_Generator.py

Este archivo contiene la implementación del generador de código Go para un lenguaje de programación personalizado.
El generador toma un Árbol de Sintaxis Abstracta (AST) y produce el código Go correspondiente.

Clases:
    - GoCodeGenerator: Clase principal para la generación de código Go.
    - Interpreter: Clase para interpretar y generar el código Go desde el AST.

Funciones:
    - convert_ast_to_go: Función que convierte un AST a código Go usando el generador de código.

"""

from rich import print

from bug_lang.checker import Checker
from bug_lang.go_ast import *
from bug_lang.utils.stdlib import *


class GoCodeGenerator:
    def __init__(self):
        self.code = ['package main\n\nimport "fmt"\n\n']
        self.in_for_loop = False

    def generate(self, node):
        if isinstance(node, Program):
            self.generate_program(node)
        elif isinstance(node, Block):
            self.generate_block(node)
        elif isinstance(node, FuncDeclaration):
            self.generate_func_declaration(node)
        elif isinstance(node, VarDeclaration):
            return self.generate_var_declaration(node)
        elif isinstance(node, Print):
            self.generate_print(node)
        elif isinstance(node, IfStmt):
            self.generate_if_stmt(node)
        elif isinstance(node, WhileStmt):
            self.generate_while_stmt(node)
        elif isinstance(node, ForStmt):
            self.generate_for_stmt(node)
        elif isinstance(node, Return):
            self.generate_return(node)
        elif isinstance(node, Binary):
            return self.generate_binary(node)
        elif isinstance(node, Unary):
            return self.generate_unary(node)
        elif isinstance(node, Literal):
            return self.generate_literal(node)
        elif isinstance(node, Variable):
            return self.generate_variable(node)
        elif isinstance(node, Assign):
            self.generate_assign(node)
        elif isinstance(node, AssignPostfix):
            return self.generate_assign_postfix(node)
        elif isinstance(node, AssignPrefix):
            return self.generate_assign_prefix(node)
        elif isinstance(node, Call):
            return self.generate_call(node)
        elif isinstance(node, Set):
            self.generate_set(node)
        elif isinstance(node, Get):
            return self.generate_get(node)
        elif isinstance(node, This):
            return self.generate_this(node)
        elif isinstance(node, Super):
            return self.generate_super(node)
        elif isinstance(node, ExprStmt):
            return self.generate(node.expr)

    def generate_program(self, node):
        for decl in node.decl:
            self.generate(decl)
        self.code.append("\n")

    def generate_block(self, node):
        self.code.append("{\n")
        for stmt in node.stmts:
            self.generate(stmt)
        self.code.append("}\n")

    def generate_func_declaration(self, node):
        type_mapping = {"silk": "string", "ant": "int", "flutter": "float"}

        if node.parameters is None:
            params = ""
        else:
            params = ", ".join(f"{name} {type_mapping.get(type_, type_)}" for name, type_ in node.parameters)

        if isinstance(node.return_type, str):
            return_type = type_mapping.get(node.return_type, node.return_type)
        else:
            return_type = " ".join(type_mapping.get(t, t) for t in node.return_type)

        self.code.append(f"func {node.name}({params}) {return_type} ")
        self.generate(node.stmts)

    def generate_var_declaration(self, node):
        if node.expr:
            expr = self.generate(node.expr)
            if self.in_for_loop:
                return f"{node.name} := {expr}"
            else:
                self.code.append(f"{node.name} := {expr}\n")
        else:
            if self.in_for_loop:
                return f"var {node.name}"
            else:
                self.code.append(f"var {node.name}\n")

    def generate_print(self, node):
        expr = self.generate(node.expr)
        self.code.append(f"fmt.Println({expr})\n")

    def generate_if_stmt(self, node):
        cond = self.generate(node.cond)
        self.code.append(f"if {cond} ")
        self.generate(node.cons)
        if node.altr:
            self.code[-1] = self.code[-1].rstrip()  # Remove trailing newline from the end of the 'if' block
            self.code.append(" else ")
            self.generate(node.altr)

    def generate_while_stmt(self, node):
        cond = self.generate(node.cond)
        self.code.append(f"for {cond} ")
        self.generate(node.body)

    def generate_for_stmt(self, node):
        self.in_for_loop = True
        init = self.generate(node.for_init) if node.for_init else ""
        cond = self.generate(node.for_cond) if node.for_cond else ""
        incr = self.generate(node.for_increment) if node.for_increment else ""
        self.code.append(f"for {init}; {cond}; {incr} ")
        self.in_for_loop = False
        self.generate(node.for_body)

    def generate_return(self, node):
        expr = self.generate(node.expr)
        self.code.append(f"return {expr}\n")

    def generate_binary(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        return f"{left} {node.op} {right}"

    def generate_unary(self, node):
        expr = self.generate(node.expr)
        return f"{node.op}{expr}"

    def generate_literal(self, node):
        if node.value is None:
            return "nil"
        elif isinstance(node.value, bool):
            return str(node.value).lower()  # Go uses 'true' and 'false'
        elif isinstance(node.value, str):
            return f"{node.value}"
        else:
            return str(node.value)

    def generate_variable(self, node):
        return node.name

    def generate_assign(self, node):
        expr = self.generate(node.expr)
        self.code.append(f"{node.name} {node.op} {expr}\n")

    def generate_assign_postfix(self, node):
        expr = self.generate(node.expr)
        if self.in_for_loop:
            return f"{expr}{node.op}"
        else:
            self.code.append(f"{expr}{node.op}\n")

    def generate_assign_prefix(self, node):
        expr = self.generate(node.expr)
        if self.in_for_loop:
            return f"{node.op}{expr}"
        else:
            self.code.append(f"{node.op}{expr}\n")

    def generate_call(self, node):
        func = self.generate(node.func)
        if node.args is None:
            args = ""
        else:
            args = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func}({args})"

    def generate_call_stmt(self, node):
        func_name = self.generate(node.func)
        if func_name != "main":
            call = self.generate_call(node)
            self.code.append(f"{call}\n")

    def generate_set(self, node):
        obj = self.generate(node.obj)
        expr = self.generate(node.expr)
        self.code.append(f"{obj}.{node.name} = {expr}\n")

    def generate_get(self, node):
        obj = self.generate(node.obj)
        return f"{obj}.{node.name}"

    def generate_this(self, node):
        return "this"

    def generate_super(self, node):
        # La traducción de "super" puede ser compleja y depende de la implementación específica en Go
        return f"super.{node.name}"

    # Añadir más métodos de generación según sea necesario


def convert_ast_to_go(ast_root):
    generator = GoCodeGenerator()
    generator.generate(ast_root)
    return "".join(generator.code)
