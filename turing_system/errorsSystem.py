from abc import ABC, abstractmethod
from enum import Enum

class NodeType(Enum):

    # Values errors
    NoValuesError        = "NoValuesError"
    ValuesError          = "ValuesError"
    NotAValueError       = "NotAValueError"
    
    # Initial errors
    NoInitialStateError  = "NoInitialStateError"

    # State errors
    NameStateError       = "NameStateError"
    NoAllValuesUsedError = "NoAllValuesUsedError"
    InfiniteLoopError    = "InfiniteLoopError"
    NoCommandsError      = "NoCommandsError"
    CommandError         = "CommandError"

    # Code errors
    NoCodeError          = "NoCodeError"
    RubanError           = "RubanError"

class Node(ABC):

    @abstractmethod
    def type(self) -> NodeType:
        """return the NodeTyoe"""
        pass

    @abstractmethod
    def json(self) -> dict:
        """return the JSON representation of the AST Node"""
        pass

class Error(Node):
    pass

class NoValuesError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NoValuesError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class ValuesError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.ValuesError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class NoInitialStateError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NoInitialStateError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class NameStateError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NameStateError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class NoCommandsError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NoCommandsError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }
    
class CommandError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.CommandError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }
    
class NoAllValuesUsedError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NoAllValuesUsedError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class NotAValueError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NotAValueError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class InfiniteLoopError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.InfiniteLoopError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class NoCodeError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.NoCodeError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }

class RubanError(Error):

    def __init__(self, reason: str) -> None:
        
        self.reason: str = reason

        return None
    
    def type(self) -> NodeType:

        return NodeType.RubanError
    
    def json(self) -> dict:

        return {
            "type": self.type().value,
            "reason": self.reason
        }