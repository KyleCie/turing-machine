class NoValuesError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class ValuesError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class InitialStateError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class NameStateError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class NoCommandsError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None
    
class CommandError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None
    
class NoAllValuesUsedError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class NoCodeError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class CodeError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None

class TapeError(Exception):

    def __init__(self, message: str) -> None:

        self.message = message
        super().__init__(self.message)

        return None