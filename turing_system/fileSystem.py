from .tokenSystem import (
    REVERSED_KEYWORDS,
)

from typing import TextIO
from sys import version_info


class File:
    def __init__(self, file_handler: TextIO) -> None:
        
        self.file_handler = file_handler
        self.actions_file: list[tuple[int | str, int]] = []
        self.content = self.__get_content()
        self.length  = len(self.content)

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

    def add_action(self, element: int | str, position: int) -> None:
        
        self.actions_file.append((element, position))
        return None

    def __find_index(self, position: int) -> int:

        last_line     = 0
        last_was_line = False
        max_idx       = min(position, self.length)

        self.actions_file.sort(key=lambda x: x[1])

        for index in range(max_idx):
            if self.content[index] == "\n":
                if not last_was_line:
                    last_line     = index
                    last_was_line = True
            else:
                last_was_line = False

        return last_line + 1 if last_was_line else max_idx

    def do_action(self) -> None:

        if not self.actions_file:
            return None

        result   : list[str] = []
        last_pos : int       = 0

        for (element, pos) in self.actions_file:

            good_pos = self.__find_index(pos)
            result.append(self.content[last_pos:good_pos])

            if isinstance(element, int):
                info = REVERSED_KEYWORDS.get(element, None)
                if info is None:
                    self.file_handler.close()
                    raise ValueError(
                        "Error when handling the TokenType in the File handler system."
                    )
                word = info[0]
            else:
                word = str(element)

            # espace si le dernier char écrit est alphabétique
            if result and result[-1] and result[-1][-1].isalpha():
                result.append(" " + word)
            else:
                result.append(word)

            last_pos = good_pos

        result.append(self.content[last_pos:])

        final_content = "".join(result)

        self.file_handler.seek(0)

        try:
            self.file_handler.write(final_content)
            self.file_handler.truncate()
        except Exception as e:
            self.file_handler.close()
            if version_info >= (3, 11):
                e.add_note("Unable to write in the file for the parser.")
            raise e

        return None