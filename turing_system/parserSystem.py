from .astSystem import (

    Program,

    Statement,
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

    NodeType,

)

from .lexerSystem import Lexer
from .checkerSystem import Checker
from .tokenSystem import TokenType, Token

from sys import version_info
from typing import Callable

class Parser:

    def __init__(self, source: str) -> None:
        
        self.lexer:   Lexer   = Lexer(source=source)
        self.checker: Checker = Checker()

        # list of errors caught during parsing
        self.errors: list[str] = []

        self.current_token: Token | None = self.lexer.next_token()
        self.peek_token:    Token | None = self.lexer.next_token()

        self.token_type_to_func: dict[TokenType, Callable] = {

            TokenType.IDENT: self.__parse_identifier,
            TokenType.NONE: self.__parse_none,
            TokenType.LEFT: self.__parse_direction,
            TokenType.RIGHT: self.__parse_direction,
            TokenType.STOP: self.__parse_stop,

        }

    def __next_token(self) -> None:

        self.current_token = self.peek_token
        self.peek_token    = self.lexer.next_token()

        return None

    def __current_token_is(self, token_type: TokenType) -> bool:

        return self.current_token.type == token_type #type: ignore
    
    def __peek_token_is(self, token_type: TokenType) -> bool:

        return self.peek_token.type == token_type #type: ignore
    
    def __expect_peek(self, token_type: TokenType) -> bool:

        if self.__peek_token_is(token_type):
            self.__next_token()
            return True
        
        else:
            self.__peek_error(token_type)
            return False

    def __expect_current(self, token_type: TokenType) -> bool:

        if self.__current_token_is(token_type):
            self.__next_token()
            return True
        
        else:
            self.__current_error(token_type)
            return False

    def __current_error(self, token_type: TokenType) -> None:

        self.errors.append(f"Expected current token to be {token_type}, got " + 
                           f"{self.current_token.type} instead. -> {self.lexer.position}") #type: ignore

    def __peek_error(self, token_type: TokenType) -> None:

        self.errors.append(f"Expected next token to be {token_type}, got " +
                           f"{self.peek_token.type} instead. -> {self.lexer.position}") #type: ignore

    def parse_program(self) -> Program:

        program: Program = Program()

        while self.current_token.type != TokenType.EOF: #type: ignore

            if self.current_token.type == TokenType.EOL: #type: ignore
                self.__next_token()
                continue

            stmt = self.__parse_statement()

            if stmt is not None:
                program.statements.append(stmt) #type: ignore

        self.__next_token()

        self.checker.last_check()

        return program
    
    if version_info >= (3, 10):
        def __parse_statement(self) -> Statement | Literal | None:

            match self.current_token.type: #type: ignore

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
    else:
        def __parse_statement(self) -> Statement | Literal | None:

            if self.current_token.type == TokenType.VALUES: #type: ignore
                return self.__parse_values_statement()
            
            if self.current_token.type == TokenType.STATE: #type: ignore
                return self.__parse_state_statement()
            
            if self.current_token.type == TokenType.INITIAL: #type: ignore
                return self.__parse_initial_state_statement()
            
            if self.current_token.type == TokenType.CODE: #type: ignore
                return self.__parse_code_statement()
            
            return self.__parse_expression()

    def __parse_values_statement(self) -> ValuesStatement | None:

        if not self.__expect_peek(TokenType.COLON):
            return None
        
        body = self.__parse_value_body_statement()

        values_stmt = ValuesStatement(literals=body)

        if not self.__expect_current(TokenType.END):
            return None

        self.checker.check_values(values_stmt)

        return values_stmt

    def __parse_value_body_statement(self) -> list[IdentifierLiteral] | None:

        literals_stmt = []

        if not self.__expect_current(TokenType.COLON):
            return None

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


        if not self.__expect_peek(TokenType.STATE):
            return None

        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        expr = self.__parse_expression()

        if expr is None:
            self.checker.error_InitialState(
                f"The initial state have no names !"
            )
            return None

        if expr.type() == NodeType.IdentifierLiteral:
            expr = StateLiteral(expr.value)

        self.__next_token() # pass the ident state

        body = self.__parse_body_state_statement()

        if not self.__expect_current(TokenType.END):
            return None

        self.checker.check_initial_state(expr, body)

        return InitialStateStatement(expr, body)

    def __parse_state_statement(self) -> StateStatement | None:

        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        expr = self.__parse_expression()

        if expr is None:
            self.checker.error_NameState(
                f"there is no name for the state !"
            )
            return None

        if expr.type() == NodeType.IdentifierLiteral:
            expr = StateLiteral(expr.value)

        self.__next_token() # pass the ident state

        body = self.__parse_body_state_statement()

        if not self.__expect_current(TokenType.END):
            return None

        self.checker.check_state(expr, body)

        return StateStatement(expr, body)

    def __parse_body_state_statement(self) -> list[CommandStatement] | None:

        command_stmts = []

        if not self.__expect_current(TokenType.COLON):
            return None

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
        
        self.__next_token()

        self.checker.check_code(body)

        return CodeStatement(body)

    def __parse_body_code_statement(self) -> list[Literal] | None:

        ruban_stmts: list[Literal] = []

        if not self.__expect_current(TokenType.COLON):
            return None

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

        func: Callable | None = self.token_type_to_func.get(self.current_token.type) #type: ignore
    
        if func is None:
            result = None
        else:
            result = func()

        return result

    def __parse_identifier(self) -> IdentifierLiteral:

        return IdentifierLiteral(self.current_token.literal) #type: ignore
    
    def __parse_none(self) -> NoneLiteral:

        return NoneLiteral(self.current_token.literal) #type: ignore
    
    def __parse_direction(self) -> DirectionLiteral:

        return DirectionLiteral(self.current_token.literal) #type: ignore
    
    def __parse_stop(self) -> StopLiteral:

        return StopLiteral(self.current_token.literal) #type: ignore