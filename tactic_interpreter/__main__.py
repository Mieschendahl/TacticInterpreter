from pathlib import Path
import argparse

from tactic_interpreter.interpreter import Interpreter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Run the tactic interpreter either in interactive mode "
            "or by executing a source file."
        )
    )
    parser.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        help=(
            "Path to a file to interpret. "
            "If omitted, the interpreter starts in interactive mode."
        ),
    )
    args = parser.parse_args()
    interpreter = Interpreter()
    if args.file is None:
        interpreter.interprete_interactive()
    else:
        interpreter.interprete_file(args.file)