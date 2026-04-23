from .tokenSystem import (
    
    Token, 
    TokenType, 
    lookup_ident, 
    REST_KEYWORDS

)

from typing import Any

class Lexer:
    
    def __init__(self, source: str) -> None:
        
        self.source             = source
        self.position:      int = -1
        self.read_position: int =  0
        self.line_no:       int =  1

        self.starting_pos: int  = 0

        self.in_a_comment: bool = False
        self.current_char: str | None = None

        self.values_rest_ks = tuple(REST_KEYWORDS.values())
        self.items_rest_ks = REST_KEYWORDS.items()

        self.read_char() # init.

        return None

    def read_char(self) -> None:

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

    def __get_peek_char(self) -> str:

        # if we are exceeding the source
        if self.read_position + 1 >= len(self.source):
            return ""

        else:
            return self.source[self.read_position + 1]

    def __skip_spaces(self) -> None:

        while self.current_char is not None and \
              self.current_char in (' ', '\t', '\r', '\n'):
            
            if self.current_char == '\n':
                if not self.__peek_char_is("\n"):
                    return None

            self.read_char()

        return None
    
    def __new_token(self, token_type: TokenType, literal: Any) -> Token:

        return Token(type=token_type, literal=literal, 
                     line_no=self.line_no, position=self.position)
    
    def __is_char(self, char : str) -> bool:
        
        return char not in (self.values_rest_ks + ("\t", "\r", " ")) or char == "_"

    def __read_identifier(self) -> str:

        start = self.position
        while self.current_char is not None and \
              self.__is_char(self.current_char):
            
            self.read_char()

        return self.source[start:self.position]

    def next_token(self) -> Token | None:
        
        self.__skip_spaces()

        if self.current_char == REST_KEYWORDS[TokenType.EOL]:
            token = self.__new_token(TokenType.EOL, self.current_char)
            self.line_no += 1
            self.read_char()
            return token

        if self.current_char == '§':
            while self.current_char != REST_KEYWORDS[TokenType.EOL] and self.current_char is not None:
                self.read_char()
            self.read_char()
            self.line_no += 1
            return self.next_token()

        if self.current_char is None:
            return self.__new_token(TokenType.EOF, '')

        if self.current_char == REST_KEYWORDS[TokenType.NONE]:
            if self.__is_char(self.__get_peek_char()):
                literal = self.__read_identifier()
                token_type = lookup_ident(literal)
                self.read_char()
                return self.__new_token(token_type, literal)
            else:
                token = self.__new_token(TokenType.NONE, REST_KEYWORDS[TokenType.NONE])
                self.read_char()
                return token

        if self.__is_char(self.current_char):
            literal = self.__read_identifier()
            token_type = lookup_ident(literal)
            return self.__new_token(token_type, literal)

        for token_type, symbol in self.items_rest_ks:
            if self.current_char == symbol:
                token = self.__new_token(token_type, self.current_char)
                self.read_char()
                return token

        token = self.__new_token(TokenType.ILLEGAL, self.current_char)
        self.read_char()
        return token