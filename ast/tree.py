__all__ = ["Node", "AST", "Value", "Concatenation", "Decision", "Clini"]


class Node:
    """Base class for all nodes of AST."""
    def __init__(self, value: str, left, right):
        self.__value: str = value
        self._lchild: Node = left
        self._rchild: Node = right

    def children(self) -> tuple:
        if self._lchild is not None:
            if self._rchild is not None:
                return self._lchild, self._rchild
            else:
                return self._lchild,
        return ()

    def value(self) -> str:
        return self.__value

    def __str__(self):
        pass


class AST:
    def __init__(self, root: Node):
        self.__root: Node = root

    def root(self) -> Node:
        return self.__root

    def __str__(self):
        return self.__root.__str__()


class Value(Node):
    """Value is a node that represents leaves."""
    def __init__(self, s: str):
        super().__init__(s, None, None)

    def __str__(self):
        return self.value()


class Concatenation(Node):
    """Concatenation is a node that represents + operation."""
    def __init__(self, left: Node, right: Node):
        super().__init__('+', left, right)

    def __str__(self):
        return "{}+{}".format(self._lchild.__str__(), self._rchild.__str__())


class Decision(Node):
    """Decision is a node that represents | operation."""
    def __init__(self, left: Node, right: Node):
        super().__init__('|', left, right)

    def __str__(self):
        return "({}|{})".format(self._lchild.__str__(), self._rchild.__str__())


class Clini(Node):
    """Clini is a node that represents * operation."""
    def __init__(self, child: Node):
        super().__init__('*', child, None)

    def __str__(self):
        return "({})*".format(self._lchild.__str__())
