class UnexpectedCaseError(Exception):
    pass

class TacticError(Exception):
    pass

class TerminationException(Exception):
    pass

def pad_str(string: str, padding: str = "    ") -> str:
    lines = [f"{padding}{line}" for line in string.split("\n")]
    return "\n".join(lines)