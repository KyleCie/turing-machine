from abc import ABC, abstractmethod

class NodeType:

    Program               = 0

    # Statements
    ValuesStatement       = 1
    StateStatement        = 2
    InitialStateStatement = 3
    CommandStatement      = 4
    CodeStatement         = 5
    TapeStatement         = 6
    BlockStatement        = 7
    ExpressionStatement   = 8

    # Literals
    IdentifierLiteral     = 9
    NoneLiteral           = 10
    StopLiteral           = 11
    StateLiteral          = 12
    DirectionLiteral      = 13
    EndLiteral            = 14

class Node(ABC):

    @abstractmethod
    def type(self) -> int:
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
    
    def type(self) -> int:

        return NodeType.Program
    
    def json(self) -> dict:

        return {
            "type":       self.type(),
            "statements": [
                           {stmt.type(): stmt.json()} 
                           for stmt in self.statements
                          ]
        }

class IdentifierLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> int:
        
        return NodeType.IdentifierLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type(),
            "value": self.value
        }

class NoneLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> int:
        
        return NodeType.NoneLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type(),
            "value": self.value
        }

class StopLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> int:
        
        return NodeType.StopLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type(),
            "value": self.value
        }

class StateLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> int:
        
        return NodeType.StateLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type(),
            "value": self.value
        }

class DirectionLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> int:
        
        return NodeType.DirectionLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type(),
            "value": self.value
        }

class EndLiteral(Literal):

    def __init__(self, value: str) -> None:
        
        self.value: str = value
        return None
    
    def type(self) -> int:
        
        return NodeType.EndLiteral
    
    def json(self) -> dict:
        
        return {
            "type":  self.type(),
            "value": self.value
        }
    
class ValuesStatement(Statement):

    def __init__(self, literals: list[IdentifierLiteral] | None = None) -> None:
        
        self.literals = literals if literals else []
        return None

    def type(self) -> int:

        return NodeType.ValuesStatement
    
    def json(self) -> dict:

        return {
            "type": self.type(),
            "literals": [literal.json() for literal in self.literals]
        }

class CommandStatement(Statement):

    def __init__(self, statements: list[Literal] | None = None) -> None:

        self.statements = statements if statements is not None else []
        return None

    def type(self) -> int:
        
        return NodeType.CommandStatement
    
    def json(self) -> dict:

        return {
            "type":       self.type(),
            "statements": [stmt.json() for stmt in self.statements]
        }

class StateStatement(Statement):
    def __init__(self, name: IdentifierLiteral, 
                       commands: list[CommandStatement] | None = None) -> None:
        
        self.name: IdentifierLiteral = name
        self.commands: list[CommandStatement] = commands if commands else []
        return None

    def type(self) -> int:

        return NodeType.StateStatement
    
    def json(self) -> dict:

        return {
            "type": self.type(),
            "name": self.name.json(),
            "commands": [command.json() for command in self.commands]
        }

class InitialStateStatement(Statement):
    def __init__(self, name: IdentifierLiteral, 
                       commands: list[CommandStatement] | None = None) -> None:
        
        self.name: IdentifierLiteral = name
        self.commands: list[CommandStatement] = commands if commands else []
        return None

    def type(self) -> int:

        return NodeType.InitialStateStatement
    
    def json(self) -> dict:

        return {
            "type": self.type(),
            "name": self.name.json(),
            "commands": [command.json() for command in self.commands]
        }

class CodeStatement(Statement):
    def __init__(self, tape: list[Literal] | None = None) -> None:
        
        self.tape: list[Literal] = tape if tape else []
        return None

    def type(self) -> int:

        return NodeType.CodeStatement
    
    def json(self) -> dict:

        return {
            "type": self.type(),
            "tape": [case.json() for case in self.tape]
        }