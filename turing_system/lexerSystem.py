from .tokenSystem import (
    Token, 
    TokenType, 
    KEYWORDS, 
    REST_KEYWORDS
)

import re

class Lexer:

    _TOKEN_RE = re.compile(
        r'§[^\n]*'          # comment
        r'|[ \t\r]+'        # space/tabs/CR
        r'|\n+'             # newlines: EOL
        r'|[^:,\n\t\r ]+'   # ident
        r'|.'               # one char (:, ,, ILLEGAL)
    )

    def __init__(self, source: str) -> None:

        self.source   : str = source
        self.line_no  : int = 1
        self.position : int = 0

        self._tokens  : list[Token] = []
        self._index   : int = 0

        self._tokenize()

        self._len_tokens: int = len(self._tokens)

    def _tokenize(self) -> None:

        tokens     = self._tokens
        source     = self.source
        line_no    = 1

        _EOL   = REST_KEYWORDS[TokenType.EOL]    # '\n'
        _COLON = REST_KEYWORDS[TokenType.COLON]  # ':'
        _COMMA = REST_KEYWORDS[TokenType.COMMA]  # ','
        _NONE  = REST_KEYWORDS[TokenType.NONE]   # '_'

        for m in self._TOKEN_RE.finditer(source):
            s   = m.group()
            pos = m.start()
            c   = s[0]

            if c in (' ', '\t', '\r', '§'):
                continue

            if c == '\n':
                tokens.append(Token(TokenType.EOL, _EOL, line_no, pos))
                line_no += s.count('\n')
                continue

            if s == _COLON:
                tokens.append(Token(TokenType.COLON, s, line_no, pos))
                continue

            if s == _COMMA:
                tokens.append(Token(TokenType.COMMA, s, line_no, pos))
                continue

            if s == _NONE:
                tokens.append(Token(TokenType.NONE, s, line_no, pos))
                continue

            tokens.append(Token(KEYWORDS.get(s.lower(), TokenType.IDENT), s, line_no, pos))

        tokens.append(Token(TokenType.EOF, '', line_no, len(source)))

    def next_token(self) -> Token:

        if self._index < self._len_tokens:
            token         = self._tokens[self._index]
            self._index  += 1
            self.line_no  = token.line_no
            self.position = token.position
            return token

        return self._tokens[-1]  # EOF