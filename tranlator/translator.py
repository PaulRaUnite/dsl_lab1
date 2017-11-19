from ast import Node, AST
from automaton import NDFA
from automaton.ndfa import NonDetTransitions


def translate_node(node: Node) -> NDFA:
    """
    Creates non-deterministic automaton of regular
    expressions using the following node recursively.
    """

    children: tuple = node.children()

    child_amount: int = len(children)
    if child_amount == 0:
        return NDFA.by_value(node.value())
    elif child_amount == 1:
        if node.value() == '*':
            return NDFA.by_closure(translate_node(children[0]))
        else:
            raise Exception("Only clini operation has one argument.")

    elif child_amount == 2:
        if node.value() == '|':
            return NDFA.by_decision(translate_node(children[0]), translate_node(children[1]))
        elif node.value() == '+':
            return NDFA.by_concatenation(translate_node(children[0]), translate_node(children[1]))
        else:
            raise Exception("Binary operators are only `or` and `concatenation`.")
    else:
        raise Exception("Too much arguments, only 1 and 2-ary operations are allowed.")


def translate(ast: AST) -> NDFA:
    """Translate AST to non-deterministic finite automaton."""

    if ast.root() is None:
        return NDFA({0}, {0}, NonDetTransitions())
    return translate_node(ast.root())
