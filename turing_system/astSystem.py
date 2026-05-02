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
    def json(self) -> dict:
        """return the JSON representation of the AST Node"""
        pass


class Statement(Node):
    pass


class Literal(Node):
    __slots__ = ('value', 'node_type')

    def __init__(self, value: str, node_type: int) -> None:
        self.value     = value
        self.node_type = node_type

    def json(self) -> dict:
        return {"type": self.node_type, "value": self.value}


def IdentifierLiteral(value: str) -> Literal:
    return Literal(value, NodeType.IdentifierLiteral)

def NoneLiteral(value: str) -> Literal:
    return Literal(value, NodeType.NoneLiteral)

def StopLiteral(value: str) -> Literal:
    return Literal(value, NodeType.StopLiteral)

def StateLiteral(value: str) -> Literal:
    return Literal(value, NodeType.StateLiteral)

def DirectionLiteral(value: str) -> Literal:
    return Literal(value, NodeType.DirectionLiteral)

def EndLiteral(value: str) -> Literal:
    return Literal(value, NodeType.EndLiteral)


class Program(Node):
    __slots__ = ('statements', 'node_type')

    def __init__(self) -> None:
        self.statements: list[Statement] = []
        self.node_type = NodeType.Program

    def json(self) -> dict:
        return {
            "type":       self.node_type,
            "statements": [
                {stmt.node_type: stmt.json()} #type: ignore
                for stmt in self.statements
            ]
        }


class CommandStatement(Statement):
    __slots__ = ('statements', 'node_type')

    def __init__(self, statements: list[Literal] | None = None) -> None:
        self.statements = statements if statements is not None else []
        self.node_type  = NodeType.CommandStatement

    def json(self) -> dict:
        return {
            "type":       self.node_type,
            "statements": [stmt.json() for stmt in self.statements]
        }


class ValuesStatement(Statement):
    __slots__ = ('literals', 'node_type')

    def __init__(self, literals: list[Literal] | None = None) -> None:
        self.literals  = literals if literals else []
        self.node_type = NodeType.ValuesStatement

    def json(self) -> dict:
        return {
            "type":     self.node_type,
            "literals": [literal.json() for literal in self.literals]
        }


class StateStatement(Statement):
    __slots__ = ('name', 'commands', 'node_type')

    def __init__(self, name: Literal,
                       commands: list[CommandStatement] | None = None) -> None:
        self.name     = name
        self.commands = commands if commands else []
        self.node_type = NodeType.StateStatement

    def json(self) -> dict:
        return {
            "type":     self.node_type,
            "name":     self.name.json(),
            "commands": [command.json() for command in self.commands]
        }


class InitialStateStatement(Statement):
    __slots__ = ('name', 'commands', 'node_type')

    def __init__(self, name: Literal,
                       commands: list[CommandStatement] | None = None) -> None:
        self.name      = name
        self.commands  = commands if commands else []
        self.node_type = NodeType.InitialStateStatement

    def json(self) -> dict:
        return {
            "type":     self.node_type,
            "name":     self.name.json(),
            "commands": [command.json() for command in self.commands]
        }


class CodeStatement(Statement):
    __slots__ = ('tape', 'node_type')

    def __init__(self, tape: list[Literal] | None = None) -> None:
        self.tape      = tape if tape else []
        self.node_type = NodeType.CodeStatement

    def json(self) -> dict:
        return {
            "type": self.node_type,
            "tape": [case.json() for case in self.tape]
        }