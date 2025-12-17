from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Sequence

@dataclass
class Hole:
    tactics: set[str] # the set of tactics that can be applied to that hole
    filler: Optional[Any] = None

@dataclass
class Type:
    pass

@dataclass
class PrimitiveType(Type):
    value: Literal["bool", "int", "float", "complex", "str"]

@dataclass
class FunctionType(Type):
    parameter_types: list[Type]
    return_type: Type

@dataclass
class Identifier:
    value: str

@dataclass
class Expression:
    pass

@dataclass
class InjectedExpression(Expression):
    value: str

@dataclass
class Statement:
    pass

@dataclass
class EmptyStatement(Statement):
    pass

@dataclass
class DescriptionStatement(Statement):
    value: str

@dataclass
class CompositeStatement(Statement):
    first: Statement
    second: Statement | Hole

@dataclass
class FunctionDeclaration(Statement):
    name: Identifier
    function_type: FunctionType
    parameters: Sequence[Identifier | Hole]
    statement: Statement | Hole

@dataclass
class VariableDeclaration(Statement):
    name: Identifier
    type_: Type
    expression: Expression | Hole

@dataclass
class ReturnStatement(Statement):
    value: Expression | Hole

@dataclass
class Program:
    statement: Statement | Hole  # Not list[Statement | Hole] such that hole filling only spawns holes inside the filled hole
    selected_hole: Optional[Hole] = None
    unfilled_holes: list[Hole] = field(default_factory=list)
    implementation: str = ""
    