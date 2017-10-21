from ast.errors import EmptySubExpressionError, ParenthesisError, ExpressionError
from ast.scanner import Special, scan
from ast.tree import Node, Concatenation, Decision, Clini, Value, AST

__all__ = ["parse"]


def is_spec_symb(token, symb: str) -> bool:
    """Checks is token a Special symbol symb or not."""
    return type(token) is Special and token.s == symb


def parenthesis_test(tokens: list) -> bool:
    """Checks do tokens have equal amount of parenthesis or not."""
    parenthesis = 0
    for token in tokens:
        if is_spec_symb(token, '('):
            parenthesis += 1
        elif is_spec_symb(token, ')'):
            parenthesis -= 1

    return parenthesis == 0


def get_or_op(tokens: list) -> (int, bool):
    """Returns position of `|` symbol that is not in parenthesis."""
    i: int = 0
    par: int = 0

    for t in tokens:
        if is_spec_symb(t, '('):
            par += 1
        elif is_spec_symb(t, ')'):
            par -= 1
        if is_spec_symb(t, '|') and par == 0:
            return i, True
        i += 1

    return 0, False


def next_op(tokens: list) -> (list, str, list):
    """Returns next operation and subexpressions to which the operation is performed."""

    if len(tokens) == 0:
        raise EmptySubExpressionError("Whole expression or its subset in parenthesis is empty.")
    if len(tokens) == 1:
        if type(tokens[0]) is str:
            return tokens, "v", []
        else:
            raise ExpressionError("Subexpression is an operator.")

    op_pos, ok = get_or_op(tokens)
    if ok:
        return tokens[:op_pos], '|', tokens[op_pos + 1:]

    pos = 0
    if is_spec_symb(tokens[0], '('):
        i = 0
        par = 0
        for t in tokens:
            i += 1
            if is_spec_symb(t, '('):
                par += 1
            elif is_spec_symb(t, ')'):
                par -= 1
            if par == 0:
                break
        pos = i
    elif type(tokens[0]) is str:
        pos = 1

    for i in range(pos, len(tokens)):
        if not is_spec_symb(tokens[i], '*'):
            pos = i
            break
    else:
        pos = len(tokens)

    parenthesis_level = 0
    for i in range(len(tokens)):
        if is_spec_symb(tokens[i], '('):
            parenthesis_level += 1

    if parenthesis_level == 1 and is_spec_symb(tokens[0], '(') and is_spec_symb(tokens[-1], ')'):
        return next_op(tokens[1:-1])

    left = tokens[:pos]
    if len(left) == len(tokens):
        return left[:-1], "*", []
    if is_spec_symb(tokens[pos], '|'):
        return left, "|", tokens[pos + 1:]

    return left, "+", tokens[pos:]


def parse_node(tokens: list) -> Node:
    """Returns AST tree that represents the tokens."""
    left, op_type, right = next_op(tokens)

    if op_type == "+":
        return Concatenation(parse_node(left), parse_node(right))
    elif op_type == "|":
        return Decision(parse_node(left), parse_node(right))
    elif op_type == "*":
        return Clini(parse_node(left))
    elif op_type == "v":
        return Value(left[0])
    else:
        raise ExpressionError("FATAL: Unexpected operation: ", op_type, '.')


def optimize_node(node: Node) -> Node:
    """Returns optimized subtree. Performs deletion of nested Clini operations."""
    children: tuple = node.children()
    args_len: int = len(children)
    if args_len == 1:
        if node.value() == '*':
            if children[0].value() == '*':
                return optimize_node(children[0])
        else:
            raise Exception("Operation with one argument is not Clini operation.")

    return node


def optimize(tree: AST) -> AST:
    """Returns optimized AST. See `optimize_node` for optimization information."""
    return AST(optimize_node(tree.root()))


def parse(regexp: str) -> AST:
    """Returns AST with additional checks and optimizations."""
    tokens = scan(regexp)

    if not parenthesis_test(tokens):
        raise ParenthesisError("Amount of parenthesis isn't equal.")

    return optimize(AST(parse_node(tokens)))
