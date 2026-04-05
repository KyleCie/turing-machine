
from turing_system.lexerSystem import Lexer
from turing_system.parserSystem import Parser
from turing_system.checkerSystem import Checker
from json import dump

def main(fichier: str):
    with open(fichier, encoding="utf-8") as f:
        text = f.read()

    debug_lex = Lexer(source=text)
    
    while debug_lex.current_char is not None:
      print(debug_lex.next_token())

    print("####")

    parser = Parser(source=text)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        for err in parser.errors:
            print(err)

    print(program.json())

    with open("new_result.json", mode="w", encoding="utf-8") as f:
        dump(program.json(), f, indent=2)


if __name__ == "__main__":
    NOM_DE_FICHIER = "test_program.txt"
    main(NOM_DE_FICHIER)