from typing import Any, Optional
from tactic_interpreter.utility import UnexpectedValueError
from tactic_interpreter.program import DescriptionStatement, CompositeStatement, EmptyStatement, FunctionDeclaration, FunctionType, PrimitiveType, Program, InjectedExpression, VariableDeclaration, ReturnStatement, Hole, Identifier

class HoleCleaner:
    def __init__(self):
        self.selected_hole: Optional[Hole] = None
        self.holes: list[Hole] = []

    def clean_node(self, node: Any) -> Any:
        match node:
            case Hole():
                if node.filler is not None:
                    if node is self.selected_hole:
                        self.selected_hole = None
                    return self.clean_node(node.filler)
                if self.selected_hole is None:
                    self.selected_hole = node
                node.selected = False
                node.index = len(self.holes)
                self.holes.append(node)
                return node
            case Identifier():
                return node
            case PrimitiveType():
                return node
            case FunctionType(parameter_types, return_type):
                parameter_types = [self.clean_node(parameter_type) for parameter_type in parameter_types]
                return_type = self.clean_node(return_type)
                return FunctionType(parameter_types, return_type)
            case InjectedExpression():
                return node
            case EmptyStatement():
                return node
            case DescriptionStatement():
                return node
            case CompositeStatement(first, second):
                first = self.clean_node(first)
                second = self.clean_node(second)
                return CompositeStatement(first, second)
            case FunctionDeclaration(name, function_type, parameters, statement):
                name = self.clean_node(name)
                function_type = self.clean_node(function_type)
                parameters = [self.clean_node(parameter) for parameter in parameters]
                statement = self.clean_node(statement)
                return FunctionDeclaration(name, function_type, parameters, statement)
            case VariableDeclaration(name, type_, expression):
                name = self.clean_node(name)
                type_ = self.clean_node(type_)
                expression = self.clean_node(expression)
                return VariableDeclaration(name, type_, expression)
            case ReturnStatement(expression):
                expression = self.clean_node(expression)
                return ReturnStatement(expression)
            case _:
                raise UnexpectedValueError(node)

    def clean_holes(self, program: Program) -> None:
        self.selected_hole = program.selected_hole
        self.holes = []
        program.statement = self.clean_node(program.statement)
        if self.selected_hole is None and len(self.holes) > 0:
            self.selected_hole = self.holes[-1]
        if self.selected_hole is not None:
            self.selected_hole.selected = True
        program.selected_hole = self.selected_hole
        program.holes = self.holes