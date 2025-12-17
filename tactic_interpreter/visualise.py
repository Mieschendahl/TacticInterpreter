from typing import Optional
from tactic_interpreter.utility import UnexpectedValueError, pad_str
from tactic_interpreter.program import Type, DescriptionStatement, CompositeStatement, EmptyStatement, Expression, FunctionDeclaration, FunctionType, PrimitiveType, Program, InjectedExpression, Statement, VariableDeclaration, ReturnStatement, Hole, Identifier

def hole_to_str(hole: Hole) -> str:
    return f"[{hole.index}{"*" if hole.selected else ""}]"

def identifier_to_str(identifier: Identifier | Hole) -> str:
    match identifier:
        case Hole():
            return hole_to_str(identifier)
        case Identifier(value):
            return value
        case _:
            raise UnexpectedValueError(identifier)

def type_to_str(type_: Type | Hole) -> str:
    match type_:
        case Hole():
            return hole_to_str(type_)
        case PrimitiveType(value):
            return value
        case FunctionType(parameter_types, return_type):
            parameter_types_str = ", ".join(type_to_str(parameter_type) for parameter_type in parameter_types)
            return_type_str = type_to_str(return_type)
            return f"Callable[[{parameter_types_str}], {return_type_str}]"
        case _:
            raise UnexpectedValueError(type_)

def expression_to_str(expression: Expression | Hole) -> str:
    match expression:
        case Hole():
            return hole_to_str(expression)
        case InjectedExpression(value):
                return value
        case _:
            raise UnexpectedValueError(expression)

def statement_to_str(statement: Statement | Hole) -> str:
    match statement:
        case Hole():
            return hole_to_str(statement)
        case EmptyStatement():
                return ""
        case DescriptionStatement(value):
            return f"{pad_str(value, "# ")}"
        case CompositeStatement(first, second):
            first_str = statement_to_str(first)
            second_str = statement_to_str(second)
            return f"{first_str}\n{second_str}"
        case FunctionDeclaration(name, function_type, parameters, statement):
            name_str = identifier_to_str(name)
            parameter_list: list[str] = []
            for parameter, parameter_type in zip(parameters, function_type.parameter_types):
                parameter_str = identifier_to_str(parameter)
                parameter_type_str = type_to_str(parameter_type)
                parameter_list.append(f"{parameter_str}: {parameter_type_str}")
            parameter_list_str = ", ".join(parameter_list)
            return_type_str = type_to_str(function_type.return_type)
            signature_str = f"def {name_str}({parameter_list_str}) -> {return_type_str}:"
            statement_str = statement_to_str(statement)
            return f"{signature_str}\n{pad_str(statement_str, "    ")}"
        case VariableDeclaration(name, type_, expression):
            name_str = identifier_to_str(name)
            type_str = type_to_str(type_)
            expression_str = expression_to_str(expression)
            return f"{name_str}: {type_str} = {expression_str}"
        case ReturnStatement(expression):
            expression_str = expression_to_str(expression)
            return f"return {expression_str}"
        case _:
            raise UnexpectedValueError(statement)

def program_to_str(program: Program) -> str:
    return statement_to_str(program.statement)