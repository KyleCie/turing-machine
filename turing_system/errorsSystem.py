# checkerSystem Errors and Exceptions

class NoValuesError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class ValuesError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class InitialStateError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class NameStateError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class NoCommandsError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None
    
class CommandError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None
    
class NoAllValuesUsedError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class NoCodeError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class CodeError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

class TapeError(Exception):

    def __init__(self, message: str) -> None:

        super().__init__(message)
        return None

# parserSystem Errors and Exceptions

class TypoError(Exception):

    def __init__(self, message: str) -> None:
        
        super().__init__(message)
        return None