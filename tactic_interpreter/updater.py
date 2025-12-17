from typing import Any, Optional
from tactic_interpreter.utility import UnexpectedCaseError, pad_str
from tactic_interpreter.program import DescriptionStatement, CompositeStatement, EmptyStatement, FunctionDeclaration, FunctionType, PrimitiveType, Program, InjectedExpression, VariableDeclaration, ReturnStatement, Hole, Identifier

class Updater:
    def __init__(self):
        self.selected_hole: Optional[Hole] = None
        self.unfilled_holes: list[Hole] = []
        
    def update_node(self, node: Any) -> str:
        match node:
            case Hole():
                if node.filler is not None:
                    if node is self.selected_hole:
                        self.selected_hole = None
                    return self.update_node(node.filler)
                if self.selected_hole is None:
                    self.selected_hole = node
                if node is self.selected_hole:
                    hole_str = f"[{len(self.unfilled_holes)}*]"
                else:
                    hole_str = f"[{len(self.unfilled_holes)}]"
                self.unfilled_holes.append(node)
                return hole_str
            case Identifier(value):
                return value
            case PrimitiveType(value):
                return value
            case FunctionType(parameter_types, return_type):
                parameter_types_str = ", ".join(self.update_node(parameter_type) for parameter_type in parameter_types)
                return_type_str = self.update_node(return_type)
                return f"Callable[[{parameter_types_str}], {return_type_str}]"
            case InjectedExpression(value):
                return value
            case EmptyStatement():
                return ""
            case DescriptionStatement(value):
                return f"{pad_str(value, "# ")}"
            case CompositeStatement(first, second):
                first_str = self.update_node(first)
                second_str = self.update_node(second)
                return f"{first_str}\n{second_str}"
            case FunctionDeclaration(name, function_type, parameters, statement):
                name_str = self.update_node(name)
                parameter_list: list[str] = []
                for parameter, parameter_type in zip(parameters, function_type.parameter_types):
                    parameter_str = self.update_node(parameter)
                    parameter_type_str = self.update_node(parameter_type)
                    parameter_list.append(f"{parameter_str}: {parameter_type_str}")
                parameter_list_str = ", ".join(parameter_list)
                return_type_str = self.update_node(function_type.return_type)
                signature_str = f"def {name_str}({parameter_list_str}) -> {return_type_str}:"
                statement_str = self.update_node(statement)
                return f"{signature_str}\n{pad_str(statement_str, "    ")}"
            case VariableDeclaration(name, type_, expression):
                name_str = self.update_node(name)
                type_str = self.update_node(type_)
                expression_str = self.update_node(expression)
                return f"{name_str}: {type_str} = {expression_str}"
            case ReturnStatement(expression):
                expression_str = self.update_node(expression)
                return f"return {expression_str}"
            case _:
                raise UnexpectedCaseError(f"Got {node!r}")

    def update_program(self, program: Program) -> None:
        self.selected_hole = program.selected_hole
        self.unfilled_holes = []
        statement_str = self.update_node(program.statement)
        if self.selected_hole is None and len(self.unfilled_holes) > 0:
            self.selected_hole = self.unfilled_holes[-1]
        program.selected_hole = self.selected_hole
        program.unfilled_holes = self.unfilled_holes
        program.implementation = statement_str