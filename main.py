from turing_system.parserSystem import Parser
from turing_machine.turingSystem import Turing

from json import dump

def main(fichier: str):
    with open(fichier, encoding="utf-8") as f:
        text = f.read()

    parser = Parser(source=text)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        for err in parser.errors:
            print(err)

    with open("result_example.json", mode="w", encoding="utf-8") as f:
        dump(program.json(), f, indent=2)

    machin = Turing(program)
    print(machin.tape)
    result = machin.run()

    while not result:
        result = machin.run()

    print(machin.tape)

if __name__ == "__main__":
    NOM_DE_FICHIER = "program_example.txt"
    main(NOM_DE_FICHIER)