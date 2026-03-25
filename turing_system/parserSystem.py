from .astSystem import (
    ValuesStatement,
    InitialStateStatement,
    StateStatement,
    CommandStatement,
    CodeStatement,
    Literal,
    DirectionLiteral,
    IdentifierLiteral,
    StateLiteral,
    StopLiteral,
    NoneLiteral,
    Program,
    Statement,
    NodeType
)
from .lexerSystem import Lexer
from .tokenSystem import TokenType, Token

from typing import Callable

class Parser:

    def __init__(self, lexer: Lexer) -> None:
        
        self.lexer: Lexer = lexer

        # list of errors caught during parsing
        self.errors: list[str] = []

        self.current_token: Token = self.lexer.next_token()
        self.peek_token:    Token = self.lexer.next_token()

        self.prefix_parse_fns: dict[TokenType, Callable] = {

            TokenType.IDENT: self.__parse_identifier,
            TokenType.NONE: self.__parse_none,
            TokenType.LEFT: self.__parse_direction,
            TokenType.RIGHT: self.__parse_direction,
            TokenType.STOP: self.__parse_stop,

        }

    def __next_token(self) -> None:

        self.current_token = self.peek_token
        self.peek_token    = self.lexer.next_token()

        print(self.current_token)

        return None
    
    def __current_token_is(self, token_type: TokenType) -> bool:
    
        return self.current_token.type == token_type
    
    def __peek_token_is(self, token_type: TokenType) -> bool:

        return self.peek_token.type == token_type
    
    def __expect_peek(self, token_type: TokenType) -> bool:

        if self.__peek_token_is(token_type):
            self.__next_token()
            return True
        
        else:
            self.__peek_error(token_type)
            return False
    
    def __peek_error(self, token_type: TokenType) -> None:

        self.errors.append(f"Expected next token to be {token_type}, got {self.peek_token.type} instead. -> {self.lexer.position}")

    def parse_program(self) -> Program:

        program: Program = Program()

        while self.current_token.type != TokenType.EOF:

            if self.current_token.type == TokenType.EOL:
                self.__next_token()
                continue

            stmt = self.__parse_statement()

            if stmt is not None:
                program.statements.append(stmt) #type: ignore

        self.__next_token()

        return program
    
    def __parse_statement(self) -> Statement | Literal | None:

        match self.current_token.type:

            case TokenType.VALUES:
                return self.__parse_values_statement()
            
            case TokenType.STATE:
                return self.__parse_state_statement()
            
            case TokenType.INITIAL:
                return self.__parse_initial_state_statement()
            
            case TokenType.CODE:
                return self.__parse_code_statement()
            
            case _:
                return self.__parse_expression()

    def __parse_values_statement(self) -> ValuesStatement | None:

        if not self.__expect_peek(TokenType.COLON):
            return None
        
        body: list[Literal] = self.__parse_value_body_statement()

        values_stmt = ValuesStatement(literals=body)

        if not self.__current_token_is(TokenType.END):
            return None

        self.__next_token()

        return values_stmt

    def __parse_value_body_statement(self) -> list[Literal]:

        literals_stmt = []

        self.__next_token() # skip ':'

        while not self.__current_token_is(TokenType.END) and \
              not self.__current_token_is(TokenType.EOF):
            
            while (self.__current_token_is(TokenType.EOL) or \
                   self.__current_token_is(TokenType.COMMA)) and \
                not self.__peek_token_is(TokenType.END):

                self.__next_token()

            stmt = self.__parse_expression()

            if stmt is not None:
                literals_stmt.append(stmt)

            self.__next_token()

        return literals_stmt

    def __parse_initial_state_statement(self) -> InitialStateStatement | None:

        self.__next_token() # skip 'state'

        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        expr = self.__parse_expression()

        if expr is None:
            return None

        if expr.type() == NodeType.IdentifierLiteral:
            expr = StateLiteral(expr.value)

        self.__next_token() # pass the ident state

        body = self.__parse_body_state_statement()

        if body is None:
            return None

        self.__next_token() # pass the 'END'

        return InitialStateStatement(expr, body)

    def __parse_state_statement(self) -> StateStatement | None:

        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        expr = self.__parse_expression()

        if expr is None:
            return None

        if expr.type() == NodeType.IdentifierLiteral:
            expr = StateLiteral(expr.value)

        self.__next_token() # pass the ident state

        body = self.__parse_body_state_statement()

        if body is None:
            return None

        self.__next_token() # pass the 'END'

        return StateStatement(expr, body)

    def __parse_body_state_statement(self) -> list[CommandStatement] | None:

        command_stmts = []

        self.__next_token() # skip ':'

        while not self.__current_token_is(TokenType.END) or \
              not self.__peek_token_is(TokenType.END):
            
            while self.__current_token_is(TokenType.EOL):
                self.__next_token()

            if self.__current_token_is(TokenType.END):
                break

            command_stmt: CommandStatement = CommandStatement()

            while not self.__current_token_is(TokenType.EOL):

                if self.__current_token_is(TokenType.COMMA):
                    self.__next_token()

                stmt = self.__parse_expression()

                if stmt:
                    command_stmt.statements.append(stmt)

                if not self.__current_token_is(TokenType.EOL):
                    self.__next_token()

            command_stmts.append(command_stmt)

            if self.__current_token_is(TokenType.EOL) and not self.__peek_token_is(TokenType.END):
                self.__next_token()

        return command_stmts

    def __parse_code_statement(self) -> CodeStatement | None:

        if not self.__expect_peek(TokenType.COLON):
            return None
        
        body = self.__parse_body_code_statement()

        if body is None:
            return None
        
        self.__next_token()

        return CodeStatement(body)

    def __parse_body_code_statement(self) -> list[Literal] | None:

        ruban_stmts: list[Literal] = []

        self.__next_token() # skip ':'

        while not self.__current_token_is(TokenType.END) and \
              not self.__current_token_is(TokenType.EOF):

            while self.__current_token_is(TokenType.EOL) or \
                  self.__current_token_is(TokenType.COMMA):
                self.__next_token()

            stmt = self.__parse_statement()

            if stmt is not None:
                ruban_stmts.append(stmt) #type: ignore

            self.__next_token()

        return ruban_stmts
    
    def __parse_expression(self):

        func: Callable | None = self.prefix_parse_fns.get(self.current_token.type)
    
        if func is None:
            result = None
        else:
            result = func()

        return result

    def __parse_identifier(self) -> IdentifierLiteral:

        return IdentifierLiteral(self.current_token.literal)
    
    def __parse_none(self) -> NoneLiteral:

        return NoneLiteral(self.current_token.literal)
    
    def __parse_direction(self) -> DirectionLiteral:

        return DirectionLiteral(self.current_token.literal)
    
    def __parse_stop(self) -> StopLiteral:

        return StopLiteral(self.current_token.literal)