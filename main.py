from turing_system.parserSystem import Parser
from turing_machin.turingSystem import Turing

def main(file: str):
    with open(file, mode="r+") as f:
        print("Parsing...")
        parser = Parser(source=f, silence=False)
        program = parser.parse_program()
        print("Parsing done !")

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
    FILE_NAME = "program examples/error.txt"
    main(FILE_NAME)