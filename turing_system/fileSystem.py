from .tokenSystem import (
    
    REVERSED_KEYWORDS,
    TokenType,
    
)

from .lexerSystem import Lexer

from typing import TextIO
from sys import version_info


class File:
    def __init__(self, file_handler: TextIO) -> None:
        
        self.file_handler = file_handler
        self.actions_file: list[tuple[TokenType | str, int]] = []

        self.content = self.__get_content()
        self.length = len(self.content)

        return None

    def close_file(self) -> None:

        self.file_handler.close()
        return None 

    def __get_content(self) -> str:

        try:
            text = self.file_handler.read()
        except Exception as e:
            self.file_handler.close()
            if version_info >= (3, 11):
                e.add_note("Unable to read the file for the parser.")
            raise e

        return text   

    def get_text(self) -> str:

        return self.content
    
    def add_action(self, element: TokenType | str, position: int) -> None:
        
        self.actions_file.append((element, position))

        if len(self.actions_file) > 2 and position < self.actions_file[1][1]:
            self.actions_file.sort(key=lambda x: x[1], reverse=False)

        return None

    def __find_index(self, content: str, position: int) -> int:

        last_line = 0
        last_was_line = False

        max_idx = min(position, self.length)

        for index in range(0, max_idx):
            if content[index] == "\n":
                if not last_was_line:
                    last_line = index
                    last_was_line = True
            else:
                last_was_line = False

        return last_line+1 if last_was_line else index+1

    def do_action(self) -> None:

        if self.actions_file == []:
            return None

        lexer = Lexer(source=self.content)
        content = ""

        for (element, pos) in self.actions_file:

            good_pos = self.__find_index(self.content, pos)

            while lexer.position < good_pos:
                if lexer.current_char:
                    content += lexer.current_char
                    lexer.read_char()

            if isinstance(element, TokenType):

                info = REVERSED_KEYWORDS.get(element, None)
                
                if info is None:
                    self.file_handler.close()
                    raise ValueError("Error when handling the TokenType in the File handler system.")
                
                word = info[0]

            else:
                word = element

            if content[-1].isalpha():
                content += " " + str(word)
            else:
                content += str(word)

        while lexer.current_char:
            content += lexer.current_char
            lexer.read_char()

        self.file_handler.seek(0)

        try:
            self.file_handler.write(content)
            self.file_handler.truncate()
        except Exception as e:
            self.file_handler.close()
            if version_info >= (3, 11):
                e.add_note("Unable to write in the file for the parser.")
            raise e

        return None