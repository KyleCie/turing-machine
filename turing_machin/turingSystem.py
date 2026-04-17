from turing_system.astSystem import (

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

from turing_system.tokenSystem import (

    REST_KEYWORDS,
    REVERSED_KEYWORDS,
    TokenType,

)

from .tapeSystem import (

    Tape,
    Chain,

)

from dataclasses import dataclass
from sys import version_info

@dataclass(slots=True)
class Transition:
    write: str | None = None
    next_state: str | None = None
    direction: str | None = None
    stop: bool = False

class Turing:

    def __init__(self, program: Program) -> None:

        # program related informations
        self.program: Program = program

        self.values: list[str] = []
        self.states: dict[str, dict[str, Transition]] = {}
        self.initial_state: str | None = None
        self.tape: Tape | None = None

        self.__parse_program()

        # Turing machin itself
        self.name_state = self.initial_state

        if self.initial_state:
            self.on_state: dict[str, Transition] = self.states[self.initial_state]
        else: # no program.
            raise RuntimeError("There is no program !")
            
        self.end: bool = False

        self.tape.reset_indexisation() #type: ignore

        return None

    def __parse_commands(self, commands: list[CommandStatement]) -> dict[str, Transition]:
            
        command_info = {}

        for command in commands: #type: ignore
            literals = command.statements

            if len(literals) > 2:
                command_info[literals[0].value] = Transition(
                    write=literals[1].value,
                    next_state=literals[2].value,
                    direction=literals[3].value,
                    stop=False
                )

            else:
                command_info[literals[0].value] = Transition(
                    stop=True
                )

        return command_info

    if version_info >= (3, 10):
        def __parse_program(self) -> None:

            raw_statements = self.program.statements

            for stmt in raw_statements:

                match stmt.type():
                    
                    case NodeType.ValuesStatement:
                        for literal in stmt.literals: # type: ignore
                            self.values.append(literal.value)

                    case NodeType.InitialStateStatement:
                        self.initial_state = stmt.name.value #type: ignore
                        self.states[self.initial_state] = self.__parse_commands(stmt.commands) #type: ignore

                    case NodeType.StateStatement:
                        self.states[stmt.name.value] = self.__parse_commands(stmt.commands) # type: ignore

                    case NodeType.CodeStatement:
                        tape = stmt.tape #type: ignore

                        tape_sys = Tape(Chain(tape[0].value))

                        for case in tape[1:]:
                            chain = tape_sys.go_right()
                            chain.set_value(case.value)
                        
                        self.tape = tape_sys

            return None
        
    else:
        def __parse_program(self) -> None:

            raw_statements = self.program.statements

            for stmt in raw_statements:

                stmt_type = stmt.type()
  
                if stmt_type == NodeType.ValuesStatement:
                    for literal in stmt.literals: # type: ignore
                        self.values.append(literal.value)

                    continue

                if stmt_type == NodeType.InitialStateStatement:
                    self.initial_state = stmt.name.value #type: ignore
                    self.states[self.initial_state] = self.__parse_commands(stmt.commands) #type: ignore
                    continue

                if stmt_type == NodeType.StateStatement:
                    self.states[stmt.name.value] = self.__parse_commands(stmt.commands) # type: ignore
                    continue

                if stmt_type == NodeType.CodeStatement:
                    tape = stmt.tape #type: ignore

                    tape_sys = Tape(Chain(tape[0].value))

                    for case in tape[1:]:
                        chain = tape_sys.go_right()
                        chain.set_value(case.value)

                    self.tape = tape_sys

                    continue

            return None

    def __run(self) -> None:
        
        if not self.tape:
            raise RuntimeError(f"There is no tape !")

        case_value = self.tape.get_chain().get_value()
        command = self.on_state.get(case_value, None)

        if not command:
            raise RuntimeError(f"Unable to get the command for the value {case_value} (STATE: {self.name_state}).")

        if command.stop:
            self.end = True
            return None

        if command.write != case_value:
            self.tape.get_chain().set_value(command.write) #type: ignore
        
        if command.direction in REVERSED_KEYWORDS[TokenType.LEFT]:
            self.tape.go_left()

        else:
            self.tape.go_right()
        
        if command.next_state != self.name_state and \
           command.next_state != REST_KEYWORDS[TokenType.NONE] and \
           command.next_state:
            
            self.name_state = command.next_state
            self.on_state = self.states.get(self.name_state, {})

            if self.on_state == {}:
                raise RuntimeError(f"Unable to get the state {self.name_state}.")

    def run(self) -> bool:

        if not self.end:
            self.__run()

        return self.end