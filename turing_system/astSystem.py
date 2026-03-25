from abc import ABC, abstractmethod
from enum import Enum

class NodeType(Enum):

    Program               = "Program"

    # Statements
    ValuesStatement       = "ValuesStatement"
    StateStatement        = "StateStatement"
    InitialStateStatement = "InitialStateStatement"
    CommandStatement      = "CommandStatement"
    CodeStatement         = "CodeStatement"
    RubanStatement        = "RubanStatement"
    BlockStatement        = "BlockStatement"
    ExpressionStatement   = "ExpressionStatement"

    # Literals
    IdentifierLiteral     = "IdentifierLiteral"
    NoneLiteral           = "NoneLiteral"
    StopLiteral           = "StopLiteral"
    StateLiteral          = "StateLiteral"
    DirectionLiteral      = "DirectionLiteral"
    EndLiteral            = "EndLiteral"

class Node(ABC):

    @abstractmethod
    def type(self) -> NodeType:
        """return the NodeType"""
        pass

    @abstractmethod
    def json(self) -> dict:
        """return the JSON represention of the AST Node"""
        pass

class Statement(Node):
    pass

class Expression(Node):
    pass

class Program(Node):
    """Root AST Node"""

    def __init__(self) -> None:
        
        self.statements: list[Statement] = []
        return None
    
    def type(self) -> NodeType:

        return NodeType.Program
    
    def json(self) -> dict:

        return {
            "type":       self.type().value,
            "statements": [
                           {stmt.type().value: stmt.json()} 
                           for stmt in self.statements
                          ]
        }

class ExpressionStatement(Statement):
    
    def __init__(self, expr: Expression = None) -> None:
        
        self.expr: Expression = expr

    def type(self) -> NodeType:
        
        return NodeType.ExpressionStatement
    
    def json(self) -> dict:
        
        return {
            "type": self.type().value,
            "expr": self.expr.json()
        }

class BlockStatement(Statement):

    def __init__(self, statements: list[Statement] = None) -> None:

        self.statements = statements if statements is not None else []
        return None

    def type(self) -> NodeType:
        
        return NodeType.BlockStatement
    
    def json(self) -> dict:

        return {
            "type":       self.type().value,
            "statements": [stmt.json() for stmt in self.statements]
        }

class ValuesStatement(Statement):

    def __init__(self, body: BlockStatement = None) -> None:
        
        self.body: BlockStatement = body
        return None

    def type(self) -> NodeType:

        return NodeType.ValuesStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "body": self.body.json()
        }
    
class StateStatement(Statement):
    def __init__(self, expr: Expression = None, 
                       body: BlockStatement = None) -> None:
        
        self.expr: Expression = expr
        self.body: BlockStatement = body
        return None

    def type(self) -> NodeType:

        return NodeType.StateStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "expr": self.expr.json(),
            "body": self.body.json()
        }
    
class InitialStateStatement(Statement):
    def __init__(self, state: StateStatement = None) -> None:
        
        self.state: StateStatement = state
        return None

    def type(self) -> NodeType:

        return NodeType.InitialStateStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "state": self.state.json()
        }
    
class CommandStatement(Statement):

    def __init__(self, statements: list[Statement] = None) -> None:

        self.statements = statements if statements is not None else []
        return None

    def type(self) -> NodeType:
        
        return NodeType.CommandStatement
    
    def json(self) -> dict:

        return {
            "type":       self.type().value,
            "statements": [stmt.json() for stmt in self.statements]
        }
    
class CodeStatement(Statement):
    def __init__(self, body: BlockStatement = None) -> None:
        
        self.body: BlockStatement = body
        return None

    def type(self) -> NodeType:

        return NodeType.CodeStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "body": self.body.json()
        }

class RubanStatement(Statement):

    def __init__(self, statements: list[Statement] = None) -> None:

        self.statements = statements if statements is not None else []
        return None

    def type(self) -> NodeType:
        
        return NodeType.RubanStatement
    
    def json(self) -> dict:

        return {
            "type":       self.type().value,
            "statements": [stmt.json() for stmt in self.statements]
        }

class IdentifierLiteral(Expression):

    def __init__(self, value: str = None) -> None:
        
        self.value: str = value
    
    def type(self) -> NodeType:
        
        return NodeType.IdentifierLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class NoneLiteral(Expression):

    def __init__(self, value: str = None) -> None:
        
        self.value: str = value
    
    def type(self) -> NodeType:
        
        return NodeType.NoneLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class StopLiteral(Expression):

    def __init__(self, value: str = None) -> None:
        
        self.value: str = value
    
    def type(self) -> NodeType:
        
        return NodeType.StopLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class StateLiteral(Expression):

    def __init__(self, value: str = None) -> None:
        
        self.value: str = value
    
    def type(self) -> NodeType:
        
        return NodeType.StateLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class DirectionLiteral(Expression):

    def __init__(self, value: str = None) -> None:
        
        self.value: str = value
    
    def type(self) -> NodeType:
        
        return NodeType.DirectionLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class EndLiteral(Expression):

    def __init__(self, value: str = None) -> None:
        
        self.value: str = value
    
    def type(self) -> NodeType:
        
        return NodeType.EndLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }