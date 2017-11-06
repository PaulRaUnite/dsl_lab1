from ast import Node, AST
from automata import NonDetAutomata


def translate_node(node: Node) -> NonDetAutomata:
    """Creates non-deterministic automata of regular expressions using the following node recursively."""

    children: tuple = node.children()

    child_amount: int = len(children)
    if child_amount == 0:
        return NonDetAutomata.by_value(node.value())
    elif child_amount == 1:
        if node.value() == '*':
            return NonDetAutomata.by_closure(translate_node(children[0]))
        else:
            raise Exception("Only clini operation has one argument.")

    elif child_amount == 2:
        if node.value() == '|':
            return NonDetAutomata.by_decision(translate_node(children[0]), translate_node(children[1]))
        elif node.value() == '+':
            return NonDetAutomata.by_concatenation(translate_node(children[0]), translate_node(children[1]))
        else:
            raise Exception("Binary operators are only `or` and `concatenation`.")
    else:
        raise Exception("Too much arguments, only 1 and 2-ary operations are allowed.")


def translate(ast: AST) -> NonDetAutomata:
    """Translate AST to non-deterministic finite automata."""
    return translate_node(ast.root())
