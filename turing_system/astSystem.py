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
    TapeStatement         = "TapeStatement"
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

class Literal(Node):

    def __init__(self, value: str) -> None:
        self.value = value

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

class IdentifierLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> NodeType:
        
        return NodeType.IdentifierLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class NoneLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> NodeType:
        
        return NodeType.NoneLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class StopLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> NodeType:
        
        return NodeType.StopLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class StateLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> NodeType:
        
        return NodeType.StateLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class DirectionLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> NodeType:
        
        return NodeType.DirectionLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }

class EndLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> NodeType:
        
        return NodeType.EndLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type().value,
            "value": self.value
        }
    
class ValuesStatement(Statement):

    def __init__(self, literals: list[IdentifierLiteral] | None = None) -> None:
        
        self.literals = literals if literals else []
        return None

    def type(self) -> NodeType:

        return NodeType.ValuesStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "literals": [literal.json() for literal in self.literals]
        }

class CommandStatement(Statement):

    def __init__(self, statements: list[Literal] | None = None) -> None:

        self.statements = statements if statements is not None else []
        return None

    def type(self) -> NodeType:
        
        return NodeType.CommandStatement
    
    def json(self) -> dict:

        return {
            "type":       self.type().value,
            "statements": [stmt.json() for stmt in self.statements]
        }

class StateStatement(Statement):
    def __init__(self, name: StateLiteral, 
                       commands: list[CommandStatement] | None = None) -> None:
        
        self.name = name
        self.commands: list[CommandStatement] = commands if commands else []
        return None

    def type(self) -> NodeType:

        return NodeType.StateStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "name": self.name.json(),
            "commands": [command.json() for command in self.commands]
        }

class InitialStateStatement(Statement):
    def __init__(self, name: StateLiteral, 
                       commands: list[CommandStatement] | None = None) -> None:
        
        self.name: StateLiteral = name
        self.commands: list[CommandStatement] = commands if commands else []
        return None

    def type(self) -> NodeType:

        return NodeType.InitialStateStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "name": self.name.json(),
            "commands": [command.json() for command in self.commands]
        }

class CodeStatement(Statement):
    def __init__(self, tape: list[Literal] | None = None) -> None:
        
        self.tape: list[Literal] = tape if tape else []
        return None

    def type(self) -> NodeType:

        return NodeType.CodeStatement
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "tape": [case.json() for case in self.tape]
        }