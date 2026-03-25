# Turing Machine Emulator (Python)

## Introduction

> ⚠️ This project is not completly functioning, it's being actively programmed.

This project is a **Turing Machine emulator** implemented in Python, featuring a custom **domain-specific language (DSL)** for defining machines in a `.txt` file.

It simulates the classical mathematical model:

* Infinite tape (both directions)
* Read/write head
* State-based transitions

The goal is to provide a **simple but flexible environment** to experiment with computation theory.

---

## Features

* Custom DSL for machine definition
* Infinite tape (auto-expands with `_`)
* Multi-state support
* Deterministic transitions
* STOP condition handling
* Easy-to-read configuration format

---

## Project Structure

```
turing-machine/
│
├── main.py                   # Entry point
├── program.txt               # DSL code example 
├── result.json               # result from the program.txt
├── turing_system
├──── astSystem.py            # formatting system
├──── lexerSystem.py          # transform file to tokens
├──── parserSystem.py         # transform tokens to usable informations
├──── tokenSystem.py          # usable block for the DSL and the system
├──── examples/
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

* If current cell = `0`
* Write `1` in the cell
* Move to state `e2`
* Move head left

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

* The tape is **infinite in both directions** (to the computer limit)
* Uninitialized cells contain `_`
* The head starts at the **first cell**
* Moving beyond bounds automatically extends the tape

---

## Execution Model

1. Read symbol under the head
2. Find matching transition in current state
3. Apply:

   * Write symbol (if defined)
   * Move head (`left` / `right`)
   * Change state
4. Repeat until `STOP`

---

## 📌 Example

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

* Python 3.8+

just `dump` from json (for now).

---

##  Troubleshooting

### No transition found

Ensure every possible symbol has a rule in the current state.

### Infinite loop

Your machine does not reach a `STOP` condition.

### Parsing errors

* Missing `END`
* Incorrect commas
* Invalid state names
* and so on
---

## Future Improvements

* the Turing machine in itself
* Tape visualization
* Breakpoints
* GUI interface

---

## Updates

* 25/03/26, [see commit](https://github.com/KyleCie/turing-machine/commit/49923ed31d4ba4d41e245da96c318be7b6e91ac8) : better system of the parser and ast to have shorter (or more compact) dictionary result (-35.16% of size, with the example program).
* 25/03/26, [see commit](https://github.com/KyleCie/turing-machine/commit/7aaeeffddcbcb251179a5a6b79278c280f35ed9b) : initial commit.

## Contributors

* creator [KyleCie]

---

## License

MIT License