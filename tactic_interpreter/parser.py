import ast
import re
from dataclasses import dataclass
from typing import Any, Optional

from tactic_interpreter.program import Expression, FunctionType, Identifier, InjectedExpression, PrimitiveType, Type
from tactic_interpreter.utility import TacticError
import re
from dataclasses import dataclass
from typing import Optional, Any
import re
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Token:
    kind: str
    value: Optional[Any] = None

TOKEN_REGEX = re.compile(
    r"""
    (?P<WHITESPACE>\s+) |
    (?P<ARROW>->) |
    (?P<LPAREN>\() |
    (?P<RPAREN>\)) |
    (?P<COMMA>,) |
    (?P<PRIMITIVE>bool|int|float|complex|str)
    """,
    re.VERBOSE,
)

def lex_type(type_str: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    for match_ in TOKEN_REGEX.finditer(type_str):
        if match_.start() != pos:
            raise TacticError(f"Unexpected character at position {pos} {type_str[pos]!r}")
        kind = match_.lastgroup
        text = match_.group()
        match kind:
            case "WHITESPACE":
                pass
            case "PRIMITIVE":
                tokens.append(Token("primitive", text))
            case "LPAREN":
                tokens.append(Token("("))
            case "RPAREN":
                tokens.append(Token(")"))
            case "COMMA":
                tokens.append(Token(","))
            case "ARROW":
                tokens.append(Token("->"))
        pos = match_.end()
    if pos != len(type_str):
        raise TacticError(f"Unexpected character at position {pos} {type_str[pos]!r}")
    return tokens

class TokenStream:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, kind: str | None = None) -> Token:
        token = self.peek()
        if token is None:
            raise TacticError(f"Unexpected end of input")
        if kind is not None and token.kind != kind:
            raise TacticError(f"Expected {kind!r}, found {token.kind!r}")
        self.pos += 1
        return token

def parse_tuple(stream: TokenStream) -> list[Type]:
    entries: list[Type] = []
    stream.consume("(")
    if stream.peek() is not None and stream.peek().kind == ")": # type:ignore
        stream.consume(")")
        return entries
    while True:
        entries.append(parse_type(stream))
        token = stream.peek()
        if token is None:
            raise TacticError("Unclosed '('")
        if token.kind == ",":
            stream.consume(",")
            continue
        if token.kind == ")":
            stream.consume(")")
            break
        raise TacticError(f"Unexpected token {token.kind!r}")
    return entries

def parse_type(stream: TokenStream) -> Type:
    token = stream.peek()
    if token is None:
        raise TacticError(f"Missing a type")
    if token.kind == "primitive":
        stream.consume()
        left: list[Type] = [PrimitiveType(token.value)] # type:ignore
    elif token.kind == "(":
        left = parse_tuple(stream)
    else:
        raise TacticError(f"Misplaced token {token.kind!r}")
    if stream.peek() is not None and stream.peek().kind == "->": # type:ignore
        stream.consume("->")
        right = parse_type(stream)
        return FunctionType(left, right)
    if len(left) != 1:
        raise TacticError("Unexpected tuple type")
    return left[0]

def parse_type_str(type_str: str) -> Type:
    tokens = lex_type(type_str)
    stream = TokenStream(tokens)
    result = parse_type(stream)
    if stream.peek() is not None:
        raise TacticError(f"Unexpected trailing tokens")
    return result
    
def parse_expression(expression_str: str) -> Expression:
    expression_str = expression_str.strip()
    try:
        ast.parse(expression_str)
        return InjectedExpression(expression_str)
    except SyntaxError:
        pass
    raise TacticError(f"Invalid expression {expression_str!r}")

def parse_identifier(identifier_str: str) -> Identifier:
    identifier_str = identifier_str.strip()
    try:
        match ast.parse(identifier_str).body[0].value: # type:ignore
            case ast.Name(value):
                return Identifier(value)
    except SyntaxError:
        pass
    raise TacticError(f"Invalid identifier {identifier_str!r}")

def parse_integer(integer_str: str) -> int:
    integer_str = integer_str.strip()
    try:
        match ast.parse(integer_str).body[0].value: # type:ignore
            case ast.Constant(int(value)):
                return value
    except SyntaxError:
        pass
    raise TacticError(f"Invalid integer {integer_str!r}")