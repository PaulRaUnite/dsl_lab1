from ast import Node, AST
from automata import Automata, ValueAutomata, CliniAutomata, ConcatenationAutomata, DecisionAutomata


def translate_node(node: Node) -> Automata:
    """"""
    children: tuple = node.children()

    args_len: int = len(children)
    if args_len == 0:
        return ValueAutomata(node.value())
    elif args_len == 1:
        if node.value() == '*':
            return CliniAutomata(translate_node(children[0]))
        else:
            raise Exception("Only clini operation has one argument.")

    elif args_len == 2:
        if node.value() == '|':
            return DecisionAutomata(translate_node(children[0]), translate_node(children[1]))
        elif node.value() == '+':
            return ConcatenationAutomata(translate_node(children[0]), translate_node(children[1]))
        else:
            raise Exception("Binary operators are only `or` and `concatenation`.")
    else:
        raise Exception("Too much arguments, only 1 and 2-ary operations are allowed.")


def translate(ast: AST) -> Automata:
    """Translate AST to non-deterministic finite automata."""
    return translate_node(ast.root())
