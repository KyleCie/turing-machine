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

from .errorsSystem import (

    NoValuesError,
    ValuesError,

    NameStateError,
    InitialStateError,
    NoCommandsError,
    CommandError,
    NoAllValuesUsedError,

    NoCodeError,
    CodeError,
    TapeError,

)

from .tokenSystem import (
    
    REST_KEYWORDS,    
    TokenType,
    
)

from .fileSystem import File

try:
    import colorama
    COL_IMPORT = True
except ImportError:
    COL_IMPORT = False

class Checker:

    def __init__(self, silence: bool = False) -> None:

        self.silence: bool = silence

        self.is_source_txt: bool = True

        self.values: list[str] = []

        self.no_names_states: list[StateLiteral]    = []
        self.no_names_index:  list[tuple[int, int]] = []

        self.states: dict[str, list[CommandStatement]] = {}
        self.names_states : set[str] = set()
        self.states_defined: set[str] = set()

        self.initial_state: bool = False
        self.initial_name: str   = ""
        self.code: bool          = False

        if COL_IMPORT:
            colorama.init()

        return None

    def add_file_handler(self, file_handler: File) -> None:

        self.is_source_txt = False
        self.file = file_handler

    def error_NoValues(self, reason: str) -> None:

        raise NoValuesError(reason)

    def error_Values(self, reason: str) -> None:

        raise ValuesError(reason)

    def error_InitialState(self, reason: str) -> None:

        raise InitialStateError(reason)

    def error_NameState(self, reason: str) -> None:

        raise NameStateError(reason)

    def error_NoCommands(self, reason: str) -> None:

        raise NoCommandsError(reason)

    def error_Command(self, reason: str) -> None:

        raise CommandError(reason)

    def error_NoAllValuesUsed(self, reason: str) -> None:

        raise NoAllValuesUsedError(reason)

    def error_NoCode(self, reason: str) -> None:

        raise NoCodeError(reason)

    def error_Code(self, reason: str) -> None:

        raise CodeError(reason)

    def error_Tape(self, reason: str) -> None:

        raise TapeError(reason)

    def warning(self, reason: str) -> None:

        if COL_IMPORT:
            print(f"{colorama.Fore.YELLOW}{reason}{colorama.Fore.RESET}")
        else:
            print(f"{reason}")

    def big_warning(self, reason: str) -> None:

        if COL_IMPORT:
            print(f"{colorama.Fore.RED}{reason}{colorama.Fore.RESET}")
        else:
            print(f"{reason}")

    def check_values(self, values_statement: ValuesStatement) -> None:

        if self.values != []:
            self.error_Values("The values part is already defined !")
            return

        raw_values = values_statement.literals

        for raw_value in raw_values:

            if raw_value.value in self.values:
                self.error_Values(f"'{raw_value.value}' is already defined in the values part !")

            self.values.append(raw_value.value)

        if not self.values:
            self.error_NoValues("There are no values in the values part of the code !")

        return None
    
    def __check_body_state(self, body: list[CommandStatement], from_state: str) -> None:

        self.states[from_state] = body
        values_defined: set[str] = set()
        _Stop  = NodeType.StopLiteral
        _None  = NodeType.NoneLiteral
        _Ident = NodeType.IdentifierLiteral
        _Dir   = NodeType.DirectionLiteral

        for (index, command) in enumerate(body):

            stmts  = command.statements
            s0     = stmts[0]
            s1     = stmts[1]
            s0_val = s0.value
            s1_t   = s1.type()

            if s0_val in values_defined:
                self.error_Command(
                    f"In {from_state} : command {index+1}, value '{s0_val}' is already defined !"
                )
                return None

            if s0.type() != _None and s0_val not in self.values:
                self.error_Command(
                    f"In {from_state} : command {index+1}, value '{s0_val}' was never defined in the values part !"
                )
                return None

            values_defined.add(s0_val)

            if s1_t != _Stop and s1_t != _None and stmts[1].value not in self.values:
                self.error_Command(
                    f"In {from_state} : command {index+1}, value '{stmts[1].value}' was never defined in the values part !"
                )
                return None

            if s1_t != _Stop:
                s2   = stmts[2]
                s2_t = s2.type()

                if s2_t != _Ident and s2_t != _None:
                    self.error_Command(
                        f"In {from_state} : command {index+1}, '{s2.value}' is not a state !"
                    )
                    return None

                self.names_states.add(s2.value)

                if stmts[3].type() != _Dir:
                    self.error_Command(
                        f"In {from_state} : command {index+1}, '{stmts[3].value}' is not a direction !"
                    )

        expected = set(self.values) | {REST_KEYWORDS[TokenType.NONE]}

        if values_defined != expected:
            diffs = expected - values_defined
            if not self.silence:
                msg = "those values are not defined !" if len(diffs) > 1 else "this value is not defined !"
                self.warning(f"WARNING: in '{from_state}', {diffs} : {msg}")

        return None

    def __check_content_state(self, expr: StateLiteral, body: list[CommandStatement] | None) -> None:

        if expr.value in self.states_defined and expr.value != "":
            self.error_NameState(
                f"state '{expr.value}' is already defined somewhere else !'"
            )
            return None

        if not body:
            self.error_NoCommands(
                f"There is no command in the initial state '{expr.value}' !"
            )
            return None

    def check_initial_state(self, expr: StateLiteral, body: list[CommandStatement] | None, index: tuple[int, int] = (0, 0)) -> None:

        if self.initial_state:
            self.error_InitialState(
                f"There already a initial state defined, so '{expr.value}' can not be too !"
            )
            return None

        self.initial_state = True
        self.initial_name  = expr.value

        if expr.value == "":
            self.no_names_states.append(expr)
            self.no_names_index.append(index)

        self.__check_content_state(expr, body)

        self.states_defined.add(expr.value)

        self.__check_body_state(body, from_state=expr.value) #type: ignore

    def check_state(self, expr: StateLiteral, body: list[CommandStatement] | None, index: tuple[int, int] = (0, 0)) -> None:

        if expr.value == "":
            self.no_names_states.append(expr)
            self.no_names_index.append(index)

        self.__check_content_state(expr, body)

        self.states_defined.add(expr.value)

        self.__check_body_state(body, from_state=expr.value) #type: ignore

    def check_code(self, body: list[Literal] | None) -> None:

        if self.code:
            self.error_Code(
                f"the code was already defined !"
            )

        self.code = True

        if not body:
            self.error_Tape(
                f"There is no tape !"
            )
            return None
        
        for case in body:
            value = case.value

            if value == REST_KEYWORDS[TokenType.NONE]:
                continue

            if value not in self.values:
                self.error_Tape(
                    f"{value} was never defined and is in the tape !"
                )
                return None
            
        return None

    def __check_if_states_good(self) -> None:

        if not self.initial_state:
            self.error_InitialState(
                f"There is not initial state !"
            )
            return None

        expected = self.names_states | {REST_KEYWORDS[TokenType.NONE]}
        actual = self.states_defined

        undefined = (expected - actual) - {REST_KEYWORDS[TokenType.NONE]}
        if undefined:
            if len(undefined) == len(self.no_names_states):

                if len(undefined) == 1:
                    self.no_names_states[0].value = undefined.pop()
                    self.states_defined.add(self.no_names_states[0].value)
                    self.big_warning(
                        f"WARNING: you forgot to write the name of a state, but it was automatically added (LINE: {self.no_names_index[0][0]}), the name is '{self.no_names_states[0].value}'."
                    )
                    if not self.is_source_txt:
                        self.file.add_action(self.no_names_states[0].value, self.no_names_index[0][1]-1)
                else:
                    self.error_NameState(
                        f"There are {len(self.no_names_states)} states with no names and the names {undefined} are not defined, forgot to defined the names (LINES: {[x[1] for x in self.no_names_index]}) ?"
                    )
            else:
                self.error_NameState(
                    f"{undefined}, those states are used but were never defined !"
                )

        return None
    
    def __check_if_states_really_used(self) -> None:

        def __recursive_search(state_name: str, memory: set[str] | None = None) -> set[str]:

            states_seen: set[str] = memory if memory else set()
            commands = self.states.get(state_name, None)

            states_seen.add(state_name)

            if commands is None:
                raise RuntimeError(f"Unable to get the commands of {state_name}.")

            for command in commands:
                stmts = command.statements

                if len(stmts) <= 2:
                    continue

                if stmts[2].type() == NodeType.NoneLiteral:
                    continue

                if not stmts[2].value in states_seen:
                    states_seen.add(stmts[2].value)
                    states_seen = states_seen.union(__recursive_search(stmts[2].value, states_seen))

            return states_seen

        result = __recursive_search(self.initial_name)
        unused = self.states_defined - result

        if unused:
            if not self.silence:
                if len(unused) == 1:
                    self.warning(
                        f"WARNING: {unused}, this state will not be used by the machin."
                    )
                else:
                    self.warning(
                        f"WARNING: {unused}, those states will not be used by the machin."
                    )

        return None

    def __check_if_code_good(self) -> None:

        if not self.code:
            self.error_NoCode(
                f"There is no code part !"
            )

        return None

    def last_check(self) -> None:

        if not (self.initial_state and self.code) and self.values: # no program.
            return None

        self.__check_if_states_good()
        self.__check_if_states_really_used()
        self.__check_if_code_good()

        return None