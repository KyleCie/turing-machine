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

from .fileSystem import File

try:
    import colorama
    COL_IMPORT = True
except ImportError:
    COL_IMPORT = False

class Checker:

    def __init__(self) -> None:

        self.is_source_txt = True

        self.values: list[str] = []

        self.no_names_states: list[StateLiteral]    = []
        self.no_names_index:  list[tuple[int, int]] = []

        self.names_states : set[str] = set()
        self.states_defined: set[str] = set()

        self.initial_state: bool = False
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

        if self.values == []:
            self.error_NoValues("There are no values in the values part of the code !")

        return None
    
    def __check_body_state(self, body: list[CommandStatement], from_state: str) -> None:

        values_defined: list[str] = []

        for (index, command) in enumerate(body):

            stmts = command.statements

            if stmts[0].value in values_defined:
                self.error_Command(
                    f"In {from_state} : command {index+1}, value '{stmts[0].value}' is already defined !"
                )
                return None

            if stmts[0].value != "_" and stmts[0].value not in self.values:
                self.error_Command(
                    f"In {from_state} : command {index+1}, value {stmts[0].value} was never defined in the values part !"
                )
                return None

            values_defined.append(stmts[0].value)

            if not (stmts[1].value == "STOP" or stmts[1].value == "_") and \
                   (stmts[1].value not in self.values):
                self.error_Command(
                    f"In {from_state} : command {index+1}, value {stmts[1].value} was never defined in the values part !"
                )
                return None

            if stmts[1].value != "STOP":
                if stmts[2].type() != NodeType.IdentifierLiteral and stmts[2].value != "_":
                    self.error_Command(
                        f"In {from_state} : command {index+1}, '{stmts[2].value}' is not a state !"
                    )
                    return None

                self.names_states.add(stmts[2].value)

                if stmts[3].type() != NodeType.DirectionLiteral:
                    self.error_Command(
                        f"In {from_state} : command {index+1}, '{stmts[3].value}' is not a direction !"
                    )

        expected = set(self.values) | {"_"}
        actual = set(values_defined)

        if actual != expected:
            diffs = expected - actual
            if len(diffs) > 1:
                self.error_NoAllValuesUsed(
                    f"In {from_state}, {diffs} : those values are not defined !"
                )
            else:
                self.error_NoAllValuesUsed(
                    f"In {from_state}, {diffs} : this value is not defined !"
                )

        return None

    def __check_content_state(self, expr: StateLiteral, body: list[CommandStatement] | None) -> None:

        if expr.value in self.states_defined and expr.value != "":
            self.error_NameState(
                f"state '{expr.value} is already defined somewhere else !'"
            )
            return None

        if not body or body == []:
            self.error_NoCommands(
                f"There is no command in the initial state {expr.value} !"
            )
            return None

    def check_initial_state(self, expr: StateLiteral, body: list[CommandStatement] | None, index: tuple[int, int] = (0, 0)) -> None:

        if self.initial_state:
            self.error_InitialState(
                f"There already a initial state defined, so {expr.value} can not be too !"
            )
            return None

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

        if not body or body == []:
            self.error_Tape(
                f"There is no tape !"
            )
            return None
        
        for case in body:
            value = case.value

            if value == "_":
                continue

            if value not in self.values:
                self.error_Tape(
                    f"{value} was never defined and is in the tape !"
                )
                return None
            
        return None

    def __check_if_states_good(self) -> None:

        expected = self.names_states | {"_"}
        actual = self.states_defined

        undefined = (expected - actual) - {"_"}
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

        unused = (actual - expected) - {"_"}
        if unused:
            if len(unused) > 1:
                self.warning(
                    f"WARNING : {unused}, those states are defined but never used."
                )
            else:
                self.warning(
                    f"WARNING : {unused}, this state is defined but never used."
                )

        return None
    
    def __check_if_code_good(self) -> None:

        if not self.code:
            self.error_NoCode(
                f"There is no code part !"
            )

        return None

    def last_check(self) -> None:

        if not (self.initial_state and self.code) and self.values == []: # no program.
            return None

        self.__check_if_states_good()
        self.__check_if_code_good()

        return None