from .tokenSystem import (
    
    KEYWORDS, 
    REST_KEYWORDS,
    TokenType,
    
)

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
        
        self.actions_file.insert(0, (element, position))

        if len(self.actions_file) > 2 and position < self.actions_file[1][1]:
            self.actions_file.sort(key=lambda x: x[1], reverse=True)

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
        
        keywords_values = KEYWORDS.values()

        self.file_handler.seek(0)
        content = self.content

        last_pos = 0
        delta_len = 0

        for (element, pos) in self.actions_file:

            if isinstance(element, TokenType):
                if element in keywords_values:
                    info = REST_KEYWORDS.get(element, None)
                    
                    if info is None:
                        self.file_handler.close()
                        raise ValueError("Error when handling the TokenType in the File handler system.")
                    
                    word = info[0]
                else:
                    self.file_handler.close()
                    raise ValueError("Error with the token got from the parser.") 
            else:
                word = element

            if pos == last_pos:
                index = self.__find_index(content=content, position=pos+delta_len)
            else:
                index = self.__find_index(content=content, position=pos)

            last_char = content[index-1]

            if last_char.isalpha():
                content = content[:index] + " " + str(word) + content[index:]
                delta_len = len(str(word))+1
            else:
                content = content[:index] + str(word) + content[index:]
                delta_len = len(str(word))
        
            last_pos = pos

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