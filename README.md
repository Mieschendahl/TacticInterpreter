# Tactic Interpreter

This project implements a small **tactic-based programming interpreter** whose goal is to help beginners construct programs in a **structured, guided, and sensible way**.

Instead of writing a complete program at once, users build programs step by step by applying *tactics*. Each tactic usually performs a well-defined transformation on the program and guides the user toward a complete and well-formed result.

## Approach

The main approach is to represent a program as an **abstract syntax tree (AST)** that may contain **holes**.  
Holes represent incomplete parts of the program that still need to be filled.

- Each hole knows which tactics are allowed at that position.
- Tactics fill a hole by replacing it with a concrete subtree, often introducing new holes.
- At any time, only one hole is selected and can be manipulated.
- The program is considered complete once all holes are filled.

This approach encourages users to follow a meaningful construction order (e.g. for functions: description → signature → arguments → ... → return) instead of writing arbitrary code.

## Architecture

### Program model
The program is stored as an AST containing statements, expressions, and holes.

### Holes 
Holes represent missing program fragments and restrict which tactics may be applied. (Currently filled holes are not removed, but simply act as a proxy to its filler value)

### Tactics
Tactics are textual commands (e.g. `let: x: int` or `fill: y + 1`) that:
- check whether they are allowed for the currently selected hole
- replace that hole with a concrete AST fragment
- possibly introduce new holes

### Hole Cleaner
After each tactic, the program structure is updated:
- filled holes are removed
- the next unfilled hole is selected if necessary
- the next valid tactics are determined
- the current program state is printed, if no error occured

### Interpreter
The interpreter reads tactics (from a file or interactively), validates them, applies them to the program, and terminates successfully once no holes remain.

## Tactics

### `description`
- adds a high-level explanation of what the program is meant to do
- adds a hole for a function declaration

### `signature`
- declares the name and type of a function
- creates a function definition with parameter types and a return type
- adds holes for the parameter names and function body

### `intro`
- introduces a name for an existing, previously unnamed parameter

### `let`
- declares a local typed variable inside the function body
- creates a hole for the variable’s initializer expression

### `fill`
- fills the currently selected hole with a concrete expression

### `return`
- adds a return statement to the function body
- creates a hole for the return expression

### `switch`
- changes which hole is currently selected
- takes the index of a hole as its argument

### `finish`
- attempts to finalize the program
- succeeds only if all holes have been filled

## Setup

Assuming that you are currently at the top-level of the project, you can install it via:
```sh
python3 -m pip install .
```

Aftwards, you can run this project via (add `-h` to get a help manual): 
```
python3 -m tactic_interpreter
```

You can run an example via:
```sh
python3 -m tactic_interpreter --file examples/cheap_energy.txt
```