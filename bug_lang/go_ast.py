'''
cast.py

Estructura del árbol de síntaxis abstracto
'''
#from ast import Str
from dataclasses import *
from typing import Any, List
#from unicodedata import name
from multimethod import multimeta

#---------------------------------------------------------------
#clases abstractas
#---------------------------------------------------------------

@dataclass
class Visitor(metaclass=multimeta):
    pass


#################################################
@dataclass
class Node():
    def accept(self, vis: Visitor): #no son punteros como en C
        return vis.visit(self)

@dataclass
class Statement(Node):
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class Declaration(Statement):
    pass


#---------------------------------------------------------------
#  Nodos del Tipo Declaration, son Statement especiales que declaran la existencia de algo
#---------------------------------------------------------------

@dataclass
class VarDeclaration(Declaration):
    name   : str
    expr   : Expression


#---------------------------------------------------------------
# Statement representan acciones sin valores asociados
#---------------------------------------------------------------

@dataclass
class Program(Statement):
    decl   : List[Statement] = field(default_factory=list)

@dataclass
class Print(Statement):
    expr   : Expression


#---------------------------------------------------------------
# Expression representan valores
#---------------------------------------------------------------

@dataclass
class Literal(Expression):
    #todo lo de primary
    value  : Any

@dataclass
class Variable(Expression):
    name   : str

@dataclass
class Assign(Expression):
    op     : str
    name   : str
    expr   : Expression



#---------------------------------------------------------------
#---------------------------------------------------------------

#más aelante usaremos el Visitor para imprimir el AST de forma bonita usando tree.py
#repositorio de rich en github, el archivo tree
