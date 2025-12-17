from pathlib import Path
from typing import Any

from tactic_interpreter.parser import *
from tactic_interpreter.program import DescriptionStatement, CompositeStatement, FunctionDeclaration, FunctionType, Hole, Identifier, Program, InjectedExpression, ReturnStatement, VariableDeclaration
from tactic_interpreter.utility import TerminationException, TacticError, pad_str
from tactic_interpreter.updater import Updater


class Interpreter:
    def __init__(self):
        self.program = Program(Hole({"description"}))
        self.updater = Updater()
        self.updater.update_program(self.program)
        self.print_program("Initial program")

    def print_program(self, status: str, print_options: bool = True) -> None:
        self.updater.update_program(self.program) # not necessary, but a good safety guard
        print(f"{status}:")
        print(pad_str(self.program.implementation, "| "))
        if print_options:
            tactics: set[str] = set()
            if len(self.program.unfilled_holes) == 0:
                tactics.update({"finish"})
            if len(self.program.unfilled_holes) > 1:
                tactics.update({"switch"})
            if self.program.selected_hole is not None:
                tactics.update(self.program.selected_hole.tactics)
            tactics_str = ", ".join(tactics) if len(tactics) > 0 else "None"
            print(pad_str(f"Options: {tactics_str}", "> "))

    def check_selected_hole(self, keyword: str) -> None:
        if self.program.selected_hole is None:
            raise TacticError(f"No hole is selected")
        if keyword not in self.program.selected_hole.tactics:
            raise TacticError(f"Tactic {keyword!r} not allowed for the selected hole")
    
    def get_selected_hole(self) -> Hole:
        if self.program.selected_hole is None:
            raise TacticError(f"No hole is selected")
        return self.program.selected_hole
    
    def fill_selected_hole(self, filler: Any) -> None:
        self.get_selected_hole().filler = filler
        self.updater.update_program(self.program)
    
    def select_hole(self, index: int) -> None:
        if index < 0 or index >= len(self.program.unfilled_holes):
            raise TacticError(f"There is no unfilled hole with the index {index!r}")
        if self.program.selected_hole is self.program.unfilled_holes[index]:
            raise TacticError(f"Hole is already selected")
        self.program.selected_hole = self.program.unfilled_holes[index]
        self.updater.update_program(self.program)

    def interprete_tactic(self, tactic: str) -> None:
        if tactic.strip() == "":
            raise TacticError(f"No tactic keyword specified")
        if ":" not in tactic:
            raise TacticError(f"Missing {":"!r} after tactic keyword")
        keyword, data = tactic.split(":", 1)
        keyword = keyword.strip()
        match keyword:
            case "description":
                if data.strip() == "":
                    raise TacticError(f"No description specified")
                self.check_selected_hole(keyword)
                description = data.strip()
                self.fill_selected_hole(
                    CompositeStatement(
                        DescriptionStatement(description),
                        Hole({"signature"})
                    )
                )
                self.print_program(f"Added description")
            case "signature":
                self.check_selected_hole(keyword)
                if data.strip() == "":
                    raise TacticError(f"No signature name specified")
                if ":" not in data:
                    raise TacticError(f"Missing {":"!r} after signature name")
                name, function_type_str = data.split(":", 1)
                identifier = parse_identifier(name)
                if function_type_str == "":
                    raise TacticError(f"No function type specified")
                function_type: FunctionType = parse_type_str(function_type_str) # type:ignore
                if not isinstance(function_type, FunctionType):
                    raise TacticError(f"Only function types are allowed for the signature")
                self.fill_selected_hole(
                    FunctionDeclaration(
                        identifier,
                        function_type,
                        [Hole({"intro"}) for _ in function_type.parameter_types],
                        Hole({"let", "return"})
                    )
                )
                self.print_program(f"Added signature")
            case "intro":
                self.check_selected_hole(keyword)
                if data.strip() == "":
                    raise TacticError(f"No variable names specified")
                identifier = parse_identifier(data)
                self.fill_selected_hole(identifier)
                self.print_program(f"Introduced name")
            case "let":
                self.check_selected_hole(keyword)
                if data.strip() == "":
                    raise TacticError(f"No variable name specified")
                if ":" not in data:
                    raise TacticError(f"Missing {":"!r} after variable name")
                name, type_str = data.split(":", 1)
                name = parse_identifier(name)
                if type_str == "":
                    raise TacticError(f"No variable type specified")
                type_ = parse_type_str(type_str)
                self.fill_selected_hole(
                    CompositeStatement(
                        VariableDeclaration(
                            name,
                            type_,
                            Hole({"fill"})
                        ),
                        Hole(self.get_selected_hole().tactics)
                    )
                )
                self.print_program(f"Added variable declaration")
            case "fill":
                self.check_selected_hole(keyword)
                if data.strip() == "":
                    raise TacticError(f"No expression specified")
                expression = parse_expression(data.strip())
                self.fill_selected_hole(expression)
                self.print_program(f"Added expression")
            case "return":
                self.check_selected_hole(keyword)
                self.fill_selected_hole(ReturnStatement(Hole({"fill"})))
                self.print_program(f"Added return statement")
            case "switch":
                if data.strip() == "":
                    raise TacticError(f"No index specified")
                index = parse_integer(data)
                self.select_hole(index)
                self.print_program(f"Switched hole")
            case "finish":
                if len(self.program.unfilled_holes) > 0:
                    raise TacticError(f"There are still unfilled holes")
                self.print_program(f"Finished the program", False)
                raise TerminationException
            case _:
                raise TacticError(f"Unknown tactic keyword {keyword!r}")
        
    def interprete_file(self, file_path: str | Path) -> None:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError("File not found")
        tactics = file_path.read_text()
        for tactic in tactics.split("\n\n"):
            print(f"\nInput a tactic:")
            print(f"{pad_str(tactic + "\n", "| ")}\n")
            try:
                self.interprete_tactic(tactic)
            except TacticError as e:
                print(f"Error: {e}")
            except TerminationException:
                return None
    
    def interprete_interactive(self) -> None:
        while True:
            tactic_lines = []
            print(f"\nInput a tactic:")
            while True:
                tactic_line = input("| ")
                if tactic_line == "":
                    print()
                    break
                tactic_lines.append(tactic_line)
            tactic = "\n".join(tactic_lines)
            try:
                self.interprete_tactic(tactic)
            except TacticError as e:
                print(f"Error: {e}")
            except TerminationException:
                return None