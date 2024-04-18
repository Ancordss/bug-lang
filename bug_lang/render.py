# render.py
from graphviz import Digraph

from bug_lang.go_ast import *


class DotRender(Visitor):
    node_default = {
        "shape": "box",
        "color": "skyblue1",
        "style": "filled",
    }
    edge_defaults = {
        "arrowhead": "none",
    }
    color = "salmon"

    def __init__(self):
        self.dot = Digraph("AST")

        self.dot.attr("node", **self.node_default)
        self.dot.attr("edge", **self.edge_defaults)
        self.program = False
        self.seq = 0
        self.cont = 0

    def __repr__(self):
        return self.dot.source

    def __str__(self):
        return self.dot.source

    @classmethod
    def render(cls, model):
        dot = cls()
        model.accept(dot)
        return dot.dot

    def name(self):
        self.seq += 1
        return f"n{self.seq:02d}"

    def visit(self, node: VarDeclaration):
        name = self.name()
        self.dot.node(name, label=rf"VarDeclaration\nname={node.name}", color=self.color)
        if node.expr:
            self.dot.edge(name, self.visit(node.expr), label="init")
        return name

    # Statement

    def visit(self, node: Program):
        name = self.name()
        self.dot.node(name, label="Program", color=self.color)
        for d in node.decl:
            self.dot.edge(name, self.visit(d))
        return name

    def visit(self, node: Print):
        name = self.name()
        self.dot.node(name, label="Print", color=self.color)
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node: Literal):
        name = self.name()
        value = node.value
        if node.value is None:
            value = "nil"
        elif node.value is True:
            value = "true"
        elif node.value is False:
            value = "false"
        self.dot.node(name, label=rf"Literal\nvalue= {value}")
        return name

    def visit(self, node: Variable):
        name = self.name()
        self.dot.node(name, label=f"Variable {node.name}")
        return name

    def visit(self, node: Assign):
        name = self.name()
        label = "Assign" if node.op == "=" else node.op
        self.dot.node(name, label=rf"{label}\nname: '{node.name}'")
        self.dot.edge(name, self.visit(node.expr))
        return name

    ##########################################################

    def visit(self, node: List):
        name = self.name()
        self.dot.node(name, label=f"list {node.name}")
        return name
