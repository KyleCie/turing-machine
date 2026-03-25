from .tokenSystem import Token, TokenType, lookup_ident
from typing import Any

class Lexer:
    
    def __init__(self, source: str) -> None:
        
        self.source             = source
        self.position:      int = -1
        self.read_position: int =  0
        self.line_no:       int =  1

        self.in_a_comment: bool = False
        self.current_char: str  = None

        self.__read_char() # init.

        return None

    def __read_char(self) -> None:

        # if we are exceeding the source
        if self.read_position >= len(self.source):
            self.current_char = None

        else:
            self.current_char = self.source[self.read_position]

        self.position = self.read_position
        self.read_position += 1

        return None

    def __peek_char_is(self, char: str) -> bool:

        # if we are exceeding the source
        if self.read_position + 1 >= len(self.source):
            return False

        else:
            return self.source[self.read_position + 1] == char

    def __skip_spaces(self) -> None:

        while self.current_char is not None and \
              self.current_char in (' ', '\t', '\r', '\n'):
            
            if self.current_char == '\n':

                if not self.__peek_char_is("\n"):
                    self.line_no += 1
                    return None

            self.__read_char()

        return None
    
    def __new_token(self, token_type: TokenType, literal: Any) -> Token:

        return Token(type=token_type, literal=literal, 
                     line_no=self.line_no, position=self.position)
    
    def __is_char(self, char : str) -> bool:

        return 'a' <= char and char <= 'z' or \
               'A' <= char and char <= 'Z' or \
               '0' <= char and char <= '9'

    def __read_identifier(self) -> str:

        start = self.position
        while self.current_char is not None and \
              self.__is_char(self.current_char):
            
            self.__read_char()

        return self.source[start:self.position]

    def next_token(self) -> Token:

        token: Token = None
        
        self.__skip_spaces()

        match self.current_char:
            
            case ':':
                token = self.__new_token(TokenType.COLON, self.current_char)

            case ',':
                token = self.__new_token(TokenType.COMMA, self.current_char)

            case '_':
                token = self.__new_token(TokenType.NONE, self.current_char)

            case '§':
                while self.current_char != "\n" and self.current_char is not None:
                    self.__read_char()
                
                self.__read_char()
                return self.next_token()

            case '\n':
                token = self.__new_token(TokenType.EOL, "\\n")

            case None:
                token = self.__new_token(TokenType.EOF, '')
            
            case _:
                if self.__is_char(self.current_char):
                    literal = self.__read_identifier()
                    token_type = lookup_ident(literal)
                    token = self.__new_token(token_type, literal)
                    return token
                else:
                    token = self.__new_token(TokenType.ILLEGAL, self.current_char)

        self.__read_char()
        return token