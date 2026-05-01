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
from .fileSystem import File
from .tokenSystem import TokenType, Token, REST_KEYWORDS
from .errorsSystem import TypoError

from sys import version_info
from typing import Callable, TextIO

class Parser:

    def __init__(self, source: str | TextIO, silence: bool = False) -> None:
        
        self.silence: bool    = silence
        self.checker: Checker = Checker(silence=silence)

        if isinstance(source, str):
            self.lexer: Lexer = Lexer(source=source)
            self.is_source_txt = True
        else:
            self.file:  File  = File(file_handler=source)
            self.lexer: Lexer = Lexer(source=self.file.get_text())
            self.checker.add_file_handler(self.file)
            self.is_source_txt = False

        self.current_token: Token | None = self.lexer.next_token()
        self.peek_token:    Token | None = self.lexer.next_token()

        self.token_type_to_func: dict[int, Callable] = {

            TokenType.IDENT: self.__parse_identifier,
            TokenType.NONE: self.__parse_none,
            TokenType.LEFT: self.__parse_direction,
            TokenType.RIGHT: self.__parse_direction,
            TokenType.STOP: self.__parse_stop,

        }

        self.__stop_types_STATE = {TokenType.END, TokenType.EOF}
        self.__skip_types_SKIP = {TokenType.EOL, TokenType.COMMA}
        self.__important_types = {TokenType.STATE, TokenType.INITIAL, TokenType.CODE, TokenType.VALUES, TokenType.EOF}

    def __next_token(self) -> None:

        self.current_token = self.peek_token
        self.peek_token    = self.lexer.next_token()

        return None

    def __current_token_is(self, token_type: int) -> bool:

        return self.current_token.type == token_type #type: ignore
    
    def __peek_token_is(self, token_type: int) -> bool:

        return self.peek_token.type == token_type #type: ignore
    
    def __is_peek_token_important(self) -> bool:

        return self.peek_token.type in self.__important_types #type: ignore

    def __current_error(self, token_type: int) -> None:

        if self.current_token.type == TokenType.EOL or self.__peek_token_is(TokenType.EOL): #type: ignore
            raise TypoError(f"Expected current token to be {token_type}, got " + 
                                f"{self.current_token.type} instead. AT LINE {self.lexer.line_no-1}") #type: ignore
        else:
            raise TypoError(f"Expected current token to be {token_type}, got " + 
                                f"{self.current_token.type} instead. AT LINE {self.lexer.line_no}") #type: ignore

    def __peek_error(self, token_type: int) -> None:

        if self.current_token.type == TokenType.EOL or self.__peek_token_is(TokenType.EOL): #type: ignore
            raise TypoError(f"Expected next token to be {token_type}, got " + 
                                f"{self.peek_token.type} instead. AT LINE {self.lexer.line_no-1}") #type: ignore
        else:
            raise TypoError(f"Expected next token to be {token_type}, got " + 
                                f"{self.peek_token.type} instead. AT LINE {self.lexer.line_no}") #type: ignore

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

        if not self.is_source_txt:
            self.file.do_action()
            self.file.close_file()

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

        self.__parse_colon_statement()

        body = self.__parse_value_body_statement()

        values_stmt = ValuesStatement(literals=body)

        if self.__current_token_is(TokenType.END):
            self.__next_token()

        self.checker.check_values(values_stmt)

        return values_stmt

    def __parse_value_body_statement(self) -> list[IdentifierLiteral] | None:

        literals_stmt = []

        if not self.__current_token_is(TokenType.COLON):
            if not self.__current_token_is(TokenType.EOL):
                self.__current_error(TokenType.COLON)

        else:
            self.__next_token()

        done = False

        while not self.__current_token_is(TokenType.END) or \
              not self.__current_token_is(TokenType.EOF) or \
              not done:
            
            done = self.__skip_spaces_statement()

            if self.__current_token_is(TokenType.END) or done:
                self.__next_token()
                break

            stmt = self.__parse_expression()

            if stmt is not None:
                literals_stmt.append(stmt)

            self.__next_token()

        return literals_stmt

    def __parse_initial_state_statement(self) -> InitialStateStatement | None:

        self.__next_token() # skip INITIAL token.
        expr, line, pos = self.__parse_name_state_statement() #type: ignore

        if expr is None:
            self.checker.error_InitialState(
                f"The initial state have no name !. AT LINE {self.lexer.line_no}"
            )
            return None

        body = self.__parse_body_state_statement()

        if self.__current_token_is(TokenType.END):
            self.__next_token()

        self.checker.check_initial_state(expr, body, (line, pos)) #type: ignore

        return InitialStateStatement(expr, body) #type: ignore

    def __parse_state_statement(self) -> StateStatement | None:

        expr, line, pos = self.__parse_name_state_statement() #type: ignore

        if expr is None:
            self.checker.error_NameState(
                f"there is no name for the state !. AT LINE {self.lexer.line_no}"
            )
            return None

        body = self.__parse_body_state_statement()

        if self.__current_token_is(TokenType.END):
            self.__next_token()

        self.checker.check_state(expr, body, (line, pos)) #type: ignore

        return StateStatement(expr, body) #type: ignore

    def __parse_name_state_statement(self) -> tuple[IdentifierLiteral, int, int] | None:

        line = 0

        if self.peek_token.type != TokenType.IDENT: #type: ignore
            if not (self.peek_token.type != TokenType.COLON or self.peek_token.type != TokenType.EOL): #type: ignore
                self.__peek_error(TokenType.IDENT) # create error.
                return
            else:
                expr = IdentifierLiteral("")
                if self.peek_token.type != TokenType.EOL: #type: ignore
                    line = self.lexer.line_no - 1
                else:
                    line = self.lexer.line_no
        else:
            self.__next_token()
            expr = self.__parse_expression()

        return expr, line, self.lexer.position #type: ignore

    def __parse_body_state_statement(self) -> list[CommandStatement] | None:

        command_stmts: list[CommandStatement] = []

        self.__parse_colon_statement()

        if self.current_token.type == TokenType.COLON: #type: ignore
            self.__next_token()

        done       = False
        _EOL       = TokenType.EOL
        _EOF       = TokenType.EOF
        _END       = TokenType.END
        _COMMA     = TokenType.COMMA
        _stop      = self.__stop_types_STATE

        while self.current_token.type not in _stop and not done: #type: ignore

            done = self.__skip_spaces_statement()

            if self.current_token.type == _END or done: #type: ignore
                break

            command_stmt = CommandStatement()
            statements   = command_stmt.statements

            while self.current_token.type != _EOL and not done: #type: ignore

                if self.current_token.type == _COMMA: #type: ignore
                    self.__next_token()

                stmt = self.__parse_expression()

                if stmt:
                    statements.append(stmt)

                if self.current_token.type != _EOL: #type: ignore
                    self.__next_token()

                if self.current_token.type == _EOF: #type: ignore
                    break

            if not statements:
                self.__next_token()
                done = True
                break
            else:
                command_stmts.append(command_stmt)

        return command_stmts

    def __parse_code_statement(self) -> CodeStatement | None:

        self.__parse_colon_statement()
        
        body = self.__parse_body_code_statement()
        
        self.__next_token()

        self.checker.check_code(body)

        return CodeStatement(body)

    def __parse_body_code_statement(self) -> list[Literal] | None:

        tape_stmts: list[Literal] = []
        done = False

        self.__next_token()

        while self.current_token.type != TokenType.END or self.current_token.type != TokenType.EOF or not done: #type: ignore

            done = self.__skip_spaces_statement()

            if self.peek_token.type == TokenType.END or done: #type: ignore
                self.__next_token()
                break

            stmt = self.__parse_expression()

            if stmt is not None:
                tape_stmts.append(stmt) #type: ignore
            elif self.current_token.type != TokenType.EOL and self.peek_token.type not in self.__important_types: #type: ignore
                self.__current_error(TokenType.IDENT)

            self.__next_token()

        return tape_stmts
    
    def __parse_colon_statement(self) -> None:

        if not self.peek_token.type == TokenType.COLON: #type: ignore
            if self.peek_token.type == TokenType.EOL: #type: ignore
                if not self.silence:
                    self.checker.warning(
                        f"WARNING: you forgot to add a colon at line {self.lexer.line_no-1}."
                    )
                    if not self.is_source_txt:
                        self.file.add_action(REST_KEYWORDS[TokenType.COLON], self.lexer.position-1)
                    self.__next_token()
            else:
                self.__peek_error(TokenType.COLON)
        else:
            self.__next_token()

    def __skip_spaces_statement(self) -> bool:

        done = False
        last_index = self.lexer.position

        while self.current_token.type in self.__skip_types_SKIP and self.peek_token.type != TokenType.END: # type: ignore
            
            if self.peek_token.type in self.__important_types: #type: ignore
                done = True
                if not self.silence:
                    if self.peek_token.type == TokenType.EOF: #type: ignore
                        self.checker.warning(
                            f"WARNING: you forgot to add an 'END' at line {self.lexer.line_no}."
                        )
                    else:
                        self.checker.warning(
                            f"WARNING: you forgot to add an 'END' at line {self.lexer.line_no-1}."
                        )
                    if not self.is_source_txt:
                        self.file.add_action(TokenType.END, last_index-1)
                break
            self.__next_token()

        return done

    def __parse_expression(self) -> Literal | None:

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