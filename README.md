# Turing Machine Emulator (Python)

## Introduction

This project is a **Turing Machine emulator** implemented in Python, featuring a custom **domain-specific language (DSL)** for defining machines in a `.txt` file.

It simulates the classical mathematical model:

- Infinite tape (both directions)
- Read/write head
- State-based transitions

The goal is to provide a **simple but flexible environment** to experiment with computation theory.

---

## Features

- Custom DSL for machine definition
- Infinite tape (auto-expands with `_`)
- Multi-state support
- Deterministic transitions
- STOP condition handling
- Easy-to-read configuration format

---

## Project Structure

```
turing-machine/
│
├── main.py                   # Entry point
│
├── turing_system
├──── astSystem.py            # formatting system
├──── tokenSystem.py          # usable 'block' for the DSL and the system
├──── lexerSystem.py          # transform file to tokens
├──── parserSystem.py         # transform tokens to usable informations
├──── fileSystem.py           # file (TextIOWrapper) handler.
├──── checkerSystem.py        # check the result of the parser
├──── errorsSystem.py         # errors formatting system
│
├── turing_machin
├──── GraphicSystem.py        # the graphic logic.
├──── turingSystem.py         # the 'core' of the machin.
├──── tapeSystem.py           # the tape (double-linked chain) system.
│
├── program examples
├──── invert_A_and_B.txt      # simple inverter system.
├──── is_a_multiple_of_2.txt  # add a 'Y' or 'N' at the end of the number to say if the number is indeed a multiple of 2.
├──── shift_by_one_case.txt   # shift one case to the right the binary number in the tape.
├──── binary_increment.txt    # increment by 1 a binary number in the tape.
├──── copy.txt                # copy (and add an '#' to separate) any binary number in the tape.
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## Installation

```bash
git clone <repo_link>
cd turing-machine
python main.py
```

---

## Usage

```bash
python main.py
```

---

## Configuration File Format

A machine is defined using 4 sections:

---

### 1. Values (Alphabet)

Defines all symbols used by the machine.

```
values:
    0, 1, 10, 12, 14
END
```

the values can be in list format (like the example) or in a vertical list (each line = a symbol)

---

### 2. Initial State

Defines the starting state and its transitions.

```
initial state e1:
    _, _, e1, right
    0, 1, e2, left
    10, STOP
END
```

each line is a "command", separated with commas.

---

### 3. States

Each state defines a set of transitions.

```
state e2:
    12, STOP
    10, 1, e1, right
END
```

---

### 4. Tape (Code)

Initial content of the tape:

```
code:
    _, _, _, _
END
```

You can add after the tape, an "start: X" with X the starting position of the machin :

```
code:
    _, _, _, _
    start : 2
END
```

The machin will start at position 2 of the tape.

---

## Transition Rules

### Standard Transition

```
<read>, <write>, <next_state>, <direction>
```

Example:

```
0, 1, e2, left
```

Meaning:

- If current cell = `0`
- Write `1` in the cell
- Move to state `e2`
- Move head left

---

### Stop Rule

```
<read>, STOP
```

Example:

```
10, STOP
```

Stops execution when `10` is read.

### bonus:

you can add comments by starting it with '§'

---

## Tape Behavior

- The tape is **infinite in both directions** (to the computer limit)
- Uninitialized cells contain `_`
- The head starts at the **first cell** (the leftest one)
- Moving beyond bounds automatically extends the tape

---

## Execution Model

1. Read symbol under the head
2. Find matching transition in current state
3. See if the machin have to stop.
4. Apply:
   - Write symbol (if different than the case of the tape)
   - Move head (`left` / `right`)
   - Change state (if have to)

---

## Example

```
values:
    0, 1, 10, 12, 14
END

initial state e1:
    _, _, e1, right
    0, 1, e2, left
    10, STOP
END

state e2:
    12, STOP
    10, 1, e1, right
END

code:
    _, _, _, _
END
```

---

## Dependencies

Python 3.8+

    * `dump` from json.
    * `Callable` from typing.
    * `version_info` from sys.
    * colorama (optionally).

Python 3.10+

    * the use of match / case.

---

## Troubleshooting

### Parsing warnings

- Missing `END` or colons, a keyword.

### Checker warnings

- A state with no names.

### Parser Errors

#### Typo Error

Occurs when the parser wanted a specific word or typo and have not seen it.

### Checker Errors

#### No Values Error

Occurs when no values are defined in the values section.

#### Values Error

Occurs when the values section is defined more than once.

#### Initial State Error

Occurs when more than one initial state is defined.

#### Name State Error

Occurs when :

- Multiple states share the same name.
- A state is referenced in commands but has never been defined.
- There is the same number of undefined state names and states with no names.

#### No Commands Error

Occurs when a state has no commands.

#### Command Error

Occurs when:

- A value is used more than once in the same state.
- A value is used but has never been defined.
- A value is not recognized as a valid state in the state part of the command.
- A value is not recognized as a valid direction in the direction part of the command.

#### No All Values Used Error

Occurs when some values are not used in the state.

#### No Code Error

Occurs when there is no code section.

#### Code Error

Occurs when the code section is defined more than once.

#### Tape Error

Occurs when:

- No tape is defined in the code section.
- A value is used on the tape but has never been defined.

### Turing machin Errors

#### Runtime Error

Occurs when :

- the program is empty.
- Unable to do a command.
- The tape is empty, or not existing.

---

## Auto Typo fix

When the parser have the TextIOWrapper, it will automaticly resolve the warnings (typos) after it parsed the program.

---

## Future Improvements

- Optimizing

---

## Updates

- 03/05/26, [see commit](https://github.com/KyleCie/turing-machine/commit/757d15a3e225a9271881ddda3465b3bc786d2aa0) : Added a keyword to choose an index starting position for the machin in the code part.
- 02/O5/26, [see commit](https://github.com/KyleCie/turing-machine/commit/dd22ee100251a38bc3abd5998def30d2fd3d474a) : bugfix with the logic of the checker system with no name's states and the recursive states search.
- 02/05/26, [see commit 1](https://github.com/KyleCie/turing-machine/commit/b02b8cb06e31aa7799f0620bd1ffab44e1c92e09), [see commit 2](https://github.com/KyleCie/turing-machine/commit/0600aa712a4215114f25e26514eee7cbf8507332) : some more optimizations but no real results.
- 01/05/26, [see commit](https://github.com/KyleCie/turing-machine/commit/49976340adbe4fb5094f79d9d42142f2742fccc4) : Redone the lexer and a lot of thing to optimize the parsing system ; with the same file, 0.065sec to 0.011sec, 234940 functions calls down to 37057. More than 80% difference in speed.
- 30/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/02a45576fefe7b80192ff28aa1a672403340024f) : First version of a graphic system for the Turing machin.
- 17/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/79445b7ea119c07a1ded61630ba3466f57dfb5b9) : Implemented a new logic for the keywords so it can be more modular, and can fixes bugs into the future of the project.
- 17/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/9ef90080ad86c8dc2ef2c5ec5bb6fa06b2b84b75) : Added an system to find if there is a possibility (or "path") to go on all the states, if not it's because the states will technically never be used. Added the silencer on the checker from the parser. Better errors handler in the machin.
- 15/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/202a7568ef815d277b532d208fbb8d3af29b6e5c) : Added an auto typos corrector in program files, bugfix for the parser with the 'end of file' handling, even better handler of TypoError.
- 14/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/aa6a22cd0a3cd4a03215243e5802e56e1b0f40f1) : First version of a better system to handle TypoError, and auto-troubleshoot it, and create warning + bugfix in the lexer with the logic of the variable 'line_no'.
- 12/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/e405669b61dd4ee2ba46ed4b07a72eefcc5e8f14) : Fixed bugs in the logic of the parser when handling the body of some parts, created a new type of error for the parser + checker, better logic for IDENT (literals, names, ...) handling (now it can handle pretty much anything).
- 06/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/d7c0e38eea4bfdaa022c1d8ebe5b868ec27d99b3) : the first version of the Turing machin was created, it use a double-linked chain method, and you can visualised by printing the tape. Also added a .lower() to the lexer when adding a keywords for easier uses of thoses values.
- 05/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/03840bd1d608d9831ef7faed95c935bb59f8b6ba): Reworked the entire checker system to integrate it into the parser, and introduced proper exceptions. [See discussion](https://github.com/KyleCie/turing-machine/issues/1)
- 03/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/d7f9eb16604c26d4bf370989c8b7766a3f6216df) : completly added the support for python's language where there are no support for match / case, for all files.
- 03/04/26, [see commit](https://github.com/KyleCie/turing-machine/commit/48826700a684036219f8bc567ac3eddabf86c0cd) : added a first version of the checker system, and find many types errors (like values, name of states, and so on ...).
- 26/03/26, [see commit](https://github.com/KyleCie/turing-machine/commit/42ff5740a21e483953ce059d4b7e5baddd3857c3) : added a checking python's version for the match / case system (else it use if statements).
- 25/03/26, [see commit](https://github.com/KyleCie/turing-machine/commit/8d46db319339a12e4f629eb5efd36cb2175746ec) : fixing some typos in the code, and added more checks while parsing.
- 25/03/26, [see commit](https://github.com/KyleCie/turing-machine/commit/49923ed31d4ba4d41e245da96c318be7b6e91ac8) : better system of the parser and ast to have shorter (or more compact) dictionary result (-35.16% of size, with the example program).
- 25/03/26, [see commit](https://github.com/KyleCie/turing-machine/commit/7aaeeffddcbcb251179a5a6b79278c280f35ed9b) : initial commit.

## Contributors

- creator [KyleCie]

---

## License

MIT License
