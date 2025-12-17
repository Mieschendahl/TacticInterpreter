from typing import Any

class UnexpectedValueError(Exception):
    def __init__(self, value: Any):
        super().__init__(f"Got unexpected value {value!r}")
        self.value = value

class TacticError(Exception):
    pass

class TerminationException(Exception):
    pass

def pad_str(string: str, padding: str = "    ") -> str:
    lines = [f"{padding}{line}" for line in string.split("\n")]
    return "\n".join(lines)