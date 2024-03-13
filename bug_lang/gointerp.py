# cinterp.py
'''
Tree-walking interpreter
TODO:here we need to convert all to go code
'''
from collections import ChainMap
from bug_lang.go_ast    import *
from bug_lang.checker import Checker
from rich    import print
from bug_lang.utils.stdlib import *

import math



class ReturnException(Exception):
	def __init__(self, value):
		self.value = value	#it sets the value for exception

class BugLangExit(BaseException):
	pass
"""
class CallError(Exception):
	pass
"""
class AttributeError(Exception):
	pass

class Function:
	def __init__(self, node, env): #it receives the node and a context
		self.node = node
		self.env = env

	def __call__(self, interp, *args): #it receives the interpreter and a tuple
		if self.node.parameters is not None:
			if len(args) != len(self.node.parameters):
				raise CallError(f"Interp Error. Expected {len(self.node.parameters)} arguments")
		newenv = self.env.new_child() #we create a new environment
		if self.node.parameters is not None:
			for name, arg in zip(self.node.parameters, args):
				newenv[name] = arg

		oldenv = interp.env #we update the interpreter's environment
		interp.env = newenv
		try:
			interp.visit(self.node.stmts)
			result = None
		except ReturnException as e:
			result = e.value
		finally:
			interp.env = oldenv #we reset the last fully functional environment
		return result #returns Function exceptions

	def bind(self, instance): #I receive something called instance
		env = self.env.new_child() #I create a new environment
		env['this'] = instance #we add a new value for key 'this'
		return Function(self.node, env)


class Class:
	def __init__(self, name, sclass, methods): #this is a Class framework for any class
		self.name = name
		self.sclass = sclass
		self.methods = methods

	def __str__(self): #returns the string representation of the object
		return self.name

	def __call__(self, *args): #this class and can be called like a function.  Class()
		this = Instance(self)
		init = self.find_method('init')
		if init:
			init.bind(this)(*args) #I re-define the use for 'This'
		return this

	def find_method(self, name):
		meth = self.methods.get(name)
		if meth is None and self.sclass:
			return self.sclass.find_method(name)
		return meth

class Instance:
	def __init__(self, klass):
		self.klass = klass
		self.data = { }

	def __str__(self):
		return self.klass.name + " instance"

	def get(self, name):
		if name in self.data:
			return self.data[name]
		method = self.klass.find_method(name)
		if not method:
			raise AttributeError(f'interp Error, Not defined property {name}')
		return method.bind(self)

	def set(self, name, value):
		self.data[name] = value

ThereIsBreak=False
ThereIsContinue=False

class Interpreter(Visitor): #This is a visitor
	def __init__(self, ctxt):
		self.ctxt = ctxt 				#receives a Context (the project's manager)
		self.env  = ChainMap()			#generates ChainMap

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
		raise BugLangExit()

	# Punto de entrada alto-nivel
	def interpret(self, node):
		try:
			Checker.check(node, self.ctxt) #First, you must call the Checker
			if not self.ctxt.have_errors:
				#print("Starting interpreting \n")
				self.visit(node)
				#print("\nInterpreting finished")
			else:
				print("\n The interpreter could not start because the Checker returned errors")
		except BugLangExit as e:
			pass


	def visit(self, node: Program):
		#self.env = self.env.new_child()
		#########################################
		for k,v in stdlibFunctions.items():
			self.env[k]=v
		#########################################
		for d in node.decl:
			self.visit(d)
		#self.env = self.env.parents


	def visit(self, node: VarDeclaration):
		if node.expr:
			expr = self.visit(node.expr)
		else:
			expr = None
		self.env[node.name] = expr

	def visit(self, node: Print):
		{self.visit(node.expr)}
		print(f"{self.visit(node.expr)}")


	def visit(self, node: Literal):
		return node.value


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


	def visit(self, node: Variable):
		return self.env[node.name]

