from ast.errors import BadEscapedSymbolError, UnexpectedEndError

__all__ = ["scan"]

special = {'|', '*', '(', ')'}

escapedSymbols = ['\\', '(', ')', '*', '|']


class Special:
    """Represents all special symbols"""

    def __init__(self, seq: str):
        self.s = seq

    def __str__(self) -> str:
        return "special{" + self.s + "}"


def scan(s: str) -> list:
    """
    Returns list of tokens.
    Can raise exceptions.
    """
    tokens: list = []

    escaped = False
    for char in s:
        if escaped:
            if char in escapedSymbols:
                tokens.append(char)
                escaped = False
            else:
                raise BadEscapedSymbolError("\\" + char + " is not allowed.")
        else:
            if char == '\\':
                escaped = True
            elif char in special:
                tokens.append(Special(char))
            else:
                tokens.append(char)
                escaped = False
    if escaped:
        raise UnexpectedEndError("Escape cannot be at the end of expression.")

    return tokens
