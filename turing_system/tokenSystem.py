from typing import Any

class TokenType:

    # Specials Tokens
    EOL     = 1   # END OF LINE
    EOF     = 0   # END OF FILE
    ILLEGAL = 2   # ILLEGAL THING

    # Data types
    IDENT   = 3   # IDENTIFY STATE, VALUES, ...
    NONE    = 4   # NONE TYPE

    # Symbols
    COLON   = 5   # DECLARATION STATE, VALUES
    COMMA   = 6   # SEPERATOR
    RIGHT   = 7   # GO TO RIGHT
    LEFT    = 8   # GO TO LEFT
    STOP    = 9   # STOP THE MACHINE
    END     = 10  # END PART OF CLASS

    # Keywords elements
    VALUES  = 11  # VALUES CLASS
    STATE   = 12  # STATE  CLASS
    INITIAL = 13 # INITIAL STATE
    CODE    = 14  # CODE   CLASS

class Token:

    __slots__ = ('type', 'literal', 'line_no', 'position')

    def __init__(self, type: int, literal: Any, 
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
    
KEYWORDS: dict[str, int] = {

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

REVERSED_KEYWORDS: dict[int, tuple[str, ...]] = {

    TokenType.VALUES:  ("values",),
    TokenType.STATE:   ("state",),
    TokenType.INITIAL: ("initial",),
    TokenType.CODE:    ("code",),
    TokenType.RIGHT:   ("right", "r"),
    TokenType.LEFT:    ("left", "l"),
    TokenType.STOP:    ("stop",),
    TokenType.END:     ("end",),

}

REST_KEYWORDS: dict[int, str] = {

    TokenType.COLON: ":",
    TokenType.NONE:  "_",
    TokenType.COMMA: ",",
    TokenType.EOL:   "\n",

}