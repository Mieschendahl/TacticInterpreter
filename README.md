# Tactic Interpreter

This project implements a small **tactic-based programming interpreter** whose goal is to help beginners construct programs in a **structured, guided, and sensible way**.

Instead of writing a complete program at once, users build programs step by step by applying *tactics*. Each tactic usually performs a well-defined transformation on the program and guides the user toward a complete and well-formed result.

## Core Idea

The central idea is to represent a program as an **abstract syntax tree (AST)** that may contain **holes**.  
Holes represent incomplete parts of the program that still need to be filled.

- Each hole knows which tactics are allowed at that position.
- Tactics fill a hole by replacing it with a concrete subtree, often introducing new holes.
- At any time, only one hole is selected and can be manipulated.
- The program is considered complete once all holes are filled.

This approach encourages users to follow a meaningful construction order (e.g. for functions: description → signature → arguments → ... → return) instead of writing arbitrary code.

## Architecture

- **Program model**  
  The program is stored as an AST containing statements, expressions, and holes.

- **Holes**  
  Unfilled holes represent missing program fragments and restrict which tactics may be applied. (Currently filled holes are not removed, but simply act as a proxy to its filler value)

- **Tactics**  
  Tactics are textual commands that (e.g. `let: x: int` or `fill: y + 1`):
  - check whether they are allowed for the currently selected hole
  - replace that hole with a concrete AST fragment
  - possibly introduce new holes

- **Updater**  
  After each tactic, the program structure is updated:
  - unfilled holes are recomputed
  - the next selected hole is recopmuted if necessary
  - the next valid tactics are determined
  - the current program state is printed, if no error occured

- **Interpreter**  
  The interpreter reads tactics (from a file or interactively), validates them, applies them to the program, and terminates successfully once no holes remain.

## Goal

The final goal of the system is a **fully constructed program with no remaining holes**, built through a sequence of meaningful and guided steps rather than free-form coding.

## Setup

Install this project via:
```sh
python3 -m pip install <path/to/project>
```

Then run this project via (add `-h` to get a help manual): 
```
python3 -m tactic_interpreter
```
