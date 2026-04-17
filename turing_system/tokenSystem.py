from enum import Enum
from typing import Any

class TokenType(Enum):

    # Specials Tokens
    EOL     = "EOL"         # END OF LINE
    EOF     = "EOF"         # END OF FILE
    ILLEGAL = "ILLEGAL"     # ILLEGAL THING

    # Data types
    IDENT   = "IDENT"       # IDENTIFY STATE, VALUES, ...
    NONE    = "NONE"        # NONE TYPE

    # Symbols
    COLON   = "COLON"       # DECLARATION STATE, VALUES
    COMMA   = "COMMA"       # SEPERATOR
    RIGHT   = "RIGHT"       # GO TO RIGHT
    LEFT    = "LEFT"        # GO TO LEFT
    STOP    = "STOP"        # STOP THE MACHINE
    END     = "END"         # END PART OF CLASS

    # Keywords elements
    VALUES  = "VALUES"      # VALUES CLASS
    STATE   = "STATE"       # STATE  CLASS
    INITIAL = "INITIAL"     # INITIAL STATE
    CODE    = "CODE"        # CODE   CLASS

class Token:

    def __init__(self, type: TokenType, literal: Any, 
                 line_no: int, position: int) -> None:
        
        self.type = type
        self.literal = literal
        self.line_no = line_no
        self.position = position

        return None

    def __str__(self) -> str:

        return f"Token[{self.type}{' '*(10-len(str(self.type)))}: {repr(self.literal)}{' '*(9-len(repr(self.literal)))}: Line {self.line_no} : Position {self.position}]"
    
    def __repr__(self) -> str:
        
        return self.__str__()
    
KEYWORDS: dict[str, TokenType] = {

    "values":  TokenType.VALUES,
    "state":   TokenType.STATE,
    "initial": TokenType.INITIAL,
    "code":    TokenType.CODE,
    "right":   TokenType.RIGHT,
    "r":       TokenType.RIGHT,
    "left":    TokenType.LEFT,
    "l":       TokenType.LEFT,
    "stop":    TokenType.STOP,
    "end":     TokenType.END,

}

REVERSED_KEYWORDS: dict[TokenType, tuple[str, ...]] = {

    TokenType.VALUES:  ("values",),
    TokenType.STATE:   ("state",),
    TokenType.INITIAL: ("initial",),
    TokenType.CODE:    ("code",),
    TokenType.RIGHT:   ("right", "r"),
    TokenType.LEFT:    ("left", "l"),
    TokenType.STOP:    ("stop",),
    TokenType.END:     ("end",),

}

REST_KEYWORDS: dict[TokenType, str] = {

    TokenType.COLON: ":",
    TokenType.NONE:  "_",
    TokenType.COMMA: ",",
    TokenType.EOL:   "\n",

}

def lookup_ident(ident: str) -> TokenType:

    tt: TokenType | None = KEYWORDS.get(ident.lower())

    if tt is not None: # found in the keywords
        return tt
    
    return TokenType.IDENT