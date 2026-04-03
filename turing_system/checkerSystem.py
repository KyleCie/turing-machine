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

    Error,

    NoValuesError,
    ValuesError,
    NotAValueError,

    NameStateError,
    NoInitialStateError,
    NoCommandsError,
    CommandError,
    NoAllValuesUsedError,
    InfiniteLoopError,

    NoCodeError,
    RubanError,

)

from sys import version_info

class Checker:

    def __init__(self, program: Program) -> None:
        
        self.program: list[Statement] = program.statements
        self.errors: list[Error] = []
        
        self.known_values:    set[str] = set()

        self.values_in_state: set[str] = set()
        self.states_in_state: set[str] = set()
        self.known_states:    set[str] = set()

        return None

    def __get_statement(self, node_type: NodeType) -> Statement | None:

        for element in self.program:
            if element.type() == node_type:
                return element

        return None

    def __get_all_statement(self, node_type: NodeType) -> list[Statement]:

        result: list[Statement] = []

        for element in self.program:
            if element.type() == node_type:
                result.append(element)

        return result

    def check_program(self) -> bool:
        """return True if errors else False"""

        self.__check_values()
        self.__check_initial_state()
        self.__check_states()
        self.__check_code()

        return self.errors != []
    
    def __check_values(self) -> None:

        stmt = self.__get_statement(NodeType.ValuesStatement)

        if stmt is None:
            self.errors.append(NoValuesError(
                "There is no values at all !"
                ))
            
            return None
            
        raw_values: list[dict] = stmt.json()["literals"]

        for raw_val in raw_values:
            value = raw_val.get("value", None)

            if value is None:
                self.errors.append(ValuesError(
                    "Unable to get a value in the values !"
                    ))
                continue

            self.known_values.add(value)

    def __check_initial_state(self) -> None:

        stmt = self.__get_statement(NodeType.InitialStateStatement)

        if stmt is None:
            self.errors.append(NoInitialStateError(
                "There is no initiate state at all !"
            ))

            return None
        
        self.known_states.add(stmt.json()["name"]["value"])

        self.__check_state(stmt)

    def __check_states(self) -> None:
        
        stmts = self.__get_all_statement(NodeType.StateStatement)

        for stmt in stmts:
            self.__check_state(stmt)

            state_name = stmt.json()["name"]["value"]

            if state_name in self.known_states:
                self.errors.append(NameStateError(
                    f"{state_name} is already defined !"
                ))

            self.known_states.add(state_name)
            print("> " + state_name)
        
        if self.values_in_state != self.known_values:
            diffs = self.values_in_state - self.known_values
            self.errors.append(ValuesError(
                f"{diffs}, those values are used in states and are not initiated !"
            ))

        if self.states_in_state != self.known_states:
            diffs = self.states_in_state - self.known_states
            self.errors.append(ValuesError(
                f"{diffs}, those states are used but are not defined !"
            ))

    def __check_state(self, stmt: Statement | None = None) -> None:

        if stmt is None:
            stmt = self.__get_statement(NodeType.StateStatement)

            if stmt is None:
                return None

        commands: list[dict] | None = stmt.json().get("commands", None)

        if commands is None:
            self.errors.append(NoCommandsError(
                "No commands in the initial state !"
            ))

            return None

        self.values_in_state = set()
        self.states_in_state = set()

        for command in commands:
            coms = command.get("statements", None)

            if coms is None:
                self.errors.append(CommandError(
                    "Unable to get the command content !"
                ))

                continue

            if not (2 <= len(coms) <= 4):
                self.errors.append(CommandError(
                    "Error with the length of the command !"
                ))

                continue

            for idx, com in enumerate(coms):
                self.__check_literals_command(com, idx)  

        print(f"> {self.values_in_state}")
        print(f"> {self.states_in_state}")

    if version_info >= (3, 10):
        def __check_literals_command(self, command: dict, n: int) -> None:

            type_com = command.get("type", None)
            value_com = command.get("value", None)

            if type_com is None:
                self.errors.append(CommandError(
                    "Unable to get the type of literal in the command !"
                ))

                return None

            if value_com is None:
                self.errors.append(CommandError(
                    "Unable to get the type of literal in the command !"
                ))

                return None

            match n:
                
                case 0 | 1:

                    if (type_com == NodeType.NoneLiteral.value or
                        type_com == NodeType.StopLiteral.value and n == 1
                        ):
                        return None

                    if type_com == NodeType.IdentifierLiteral.value:
                        if value_com not in self.known_values:
                            self.errors.append(ValuesError(
                                f"{value_com} was never initiated and is used in a command !"
                            ))
                        elif n == 0:
                            self.values_in_state.add(value_com)

                    else:
                        self.errors.append(ValuesError(
                            f"{type_com} is in a command !"
                        ))

                case 2:
                    if type_com not in (NodeType.IdentifierLiteral.value,
                                        NodeType.NoneLiteral.value):
                        self.errors.append(CommandError(
                            f"{type_com} is not a identifier in a command !"
                        ))
                    else:
                        self.states_in_state.add(value_com)

                case 3:
                    if type_com != NodeType.DirectionLiteral.value:
                        self.errors.append(CommandError(
                            f"{type_com} is not a direction in a command !"
                        ))

                case _:
                    self.errors.append(CommandError(
                        "Error with the length of the command !"
                    ))
    else:
        def __check_literals_command(self, command: dict, n: int) -> None:

            type_com = command.get("type", None)
            value_com = command.get("value", None)

            if type_com is None:
                self.errors.append(CommandError(
                    "Unable to get the type of literal in the command !"
                ))

                return None

            if value_com is None:
                self.errors.append(CommandError(
                    "Unable to get the type of literal in the command !"
                ))

                return None
                
            if n == 0 or n == 1:

                if (type_com == NodeType.NoneLiteral.value or
                    type_com == NodeType.StopLiteral.value and n == 1
                    ):
                    return None

                if type_com == NodeType.IdentifierLiteral.value:
                    if value_com not in self.known_values:
                        self.errors.append(ValuesError(
                            f"{value_com} was never initiated and is used in a command !"
                        ))
                    elif n == 0:
                        self.values_in_state.add(value_com)

                else:
                    self.errors.append(ValuesError(
                        f"{type_com} is in a command !"
                    ))

            elif n == 2:
                if type_com not in (NodeType.IdentifierLiteral.value,
                                    NodeType.NoneLiteral.value):
                    self.errors.append(CommandError(
                        f"{type_com} is not a identifier in a command !"
                    ))
                else:
                    self.states_in_state.add(value_com)

            elif n == 3:
                if type_com != NodeType.DirectionLiteral.value:
                    self.errors.append(CommandError(
                        f"{type_com} is not a direction in a command !"
                    ))

            else:
                self.errors.append(CommandError(
                    "Error with the length of the command !"
                ))

    def __check_code(self) -> None:

        stmt = self.__get_statement(NodeType.CodeStatement)

        if stmt is None:
            self.errors.append(NoCodeError(
                "There is no code at all !"
            ))

            return None

        if self.known_values != []:
            ruban: list[dict] = stmt.json()["ruban"]

            for case in ruban:
                type_val = case.get("type", None)

                if type_val is None:
                    self.errors.append(RubanError(
                        "Unable to get a type of value in the ruban !"
                    ))
                
                    continue

                if type_val == NodeType.NoneLiteral.value:
                    continue

                if type_val == NodeType.IdentifierLiteral.value:
                    value_val = case.get("value", None)

                    if value_val is None:
                        self.errors.append(RubanError(
                            "Unable to get a value in the ruban !"
                        ))

                        continue

                    if value_val in self.known_values:
                        continue
                    else:
                        self.errors.append(NotAValueError(
                            f"{value_val} was never initiated and is in the ruban !"
                        ))
