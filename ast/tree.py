__all__ = ["Node", "AST", "Value", "Concatenation", "Decision", "Clini"]


class Node:
    """Base class for all nodes of regexp AST."""

    def __init__(self, value: chr, left: 'Node', right: 'Node'):
        self.__value: chr = value
        self.lchild: Node = left
        self.rchild: Node = right

    def children(self) -> tuple:
        if self.lchild is not None:
            if self.rchild is not None:
                return self.lchild, self.rchild
            else:
                return self.lchild,
        return ()

    def value(self) -> chr:
        return self.__value

    def __str__(self) -> str:
        pass


class AST:
    """AST(abstract syntax tree) is a structure to represent the regular expressions."""

    def __init__(self, root: Node):
        self.__root = root

    def root(self) -> Node:
        return self.__root

    def __str__(self) -> str:
        return self.__root.__str__()


class Value(Node):
    """Value is a node that represents leaves(actual symbols)."""

    def __init__(self, s: chr):
        super().__init__(s, None, None)

    def __str__(self) -> str:
        return self.value()


class Concatenation(Node):
    """Concatenation is a node that represents + operation."""

    def __init__(self, left: Node, right: Node):
        super().__init__('+', left, right)

    def __str__(self) -> str:
        return "{}+{}".format(self.lchild.__str__(), self.rchild.__str__())


class Decision(Node):
    """Decision is a node that represents | operation."""

    def __init__(self, left: Node, right: Node):
        super().__init__('|', left, right)

    def __str__(self) -> str:
        return "({}|{})".format(self.lchild.__str__(), self.rchild.__str__())


class Clini(Node):
    """Clini is a node that represents * operation."""

    def __init__(self, child: Node):
        super().__init__('*', child, None)

    def __str__(self) -> str:
        return "({})*".format(self.lchild.__str__())
