__all__ = ["ExpressionError", "EmptySubExpressionError",
           "ParenthesisError", "BadEscapedSymbolError",
           "UnexpectedEndError"]


class ExpressionError(Exception):
    """Type for all errors which can happen while parsing."""
    pass


class EmptySubExpressionError(ExpressionError):
    pass


class ParenthesisError(ExpressionError):
    pass


class BadEscapedSymbolError(ExpressionError):
    pass


class UnexpectedEndError(ExpressionError):
    pass
