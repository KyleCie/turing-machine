from turing_system.parserSystem import Parser
from turing_machin.turingSystem import Turing

def main(file: str):
    with open(file, encoding="utf-8") as f:
        text = f.read()

    parser = Parser(source=text)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        for err in parser.errors:
            print(err)

    machin = Turing(program)
    print(machin.tape)
    result = machin.run()

    while not result:
        result = machin.run()

    print(machin.tape)

if __name__ == "__main__":
    FILE_NAME = "program examples/invert_A_and_B.txt"
    main(FILE_NAME)