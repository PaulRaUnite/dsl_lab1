from typing import *

__all__ = []


class DetTransitions:
    """Class that implements transition table for deterministic state machine."""

    def __init__(self, d: Dict[int, Dict[str, int]]):
        self.graph = d

    def get_graph(self):
        return self.graph

    def __iter__(self):
        for origin_state, moves in self.graph.items():
            for symb, end_state in moves.items():
                yield origin_state, symb, end_state,

    def add(self, from_state: int, symb: str, to_state: int):
        if from_state not in self.graph:
            self.graph[from_state] = dict()

        self.graph[from_state][symb] = to_state

    def get_end(self, from_state: int, symb: str) -> int:
        return self.graph[from_state][symb]

    def delete(self, from_state: int, symb: str, to_state: int):
        try:
            self.graph[from_state][symb] = to_state
        finally:
            if len(self.graph[from_state]) == 0:
                del self.graph[from_state]

    def map(self, dst, trans_orig: Callable[[int], int], trans_end: Callable[[int], int]):
        """
        Performs transformation of origin and end states
        of some Transition and saves the result into another.
        Doesn't work if src == dst.
        """

        if type(dst) != DetTransitions:
            raise TypeError("dst must be Transitions.")
        if self is dst:
            raise Exception("Can't perform transformation on the same collection.")

        for [origin, symb, end] in self:
            dst.add(trans_orig(origin), symb, trans_end(end))


class DetAutomata:
    """The class that implements deterministic state machine."""

    def __init__(self, trans: DetTransitions, fins: Set[int]):
        self.__state = 0
        self.__trans = trans
        self.__finals = fins
        max_state: int = 1

        for [orig, _, end] in self.__trans:
            if orig > max_state:
                max_state = orig
            if end > max_state:
                max_state = end

        self.__biggest_state: int = max_state

    def put(self, symb: str) -> bool:
        """Do one move inside the automata."""
        try:
            self.__state = self.__trans.get_end(self.__state, symb)
        except KeyError:
            self.__state = -1
            return False
        return True

    def reset(self) -> None:
        """Resent current states."""
        self.__state = 0

    def is_final_state(self) -> bool:
        """Checks whether the automata is into one of finite states."""
        return self.__state in self.__finals

    def __str__(self) -> str:
        """Returns string representation of the automata."""
        return "state: {}\n" \
               "trans: {}\n" \
               "final: {}\n" \
               "bigst: {}".format(self.__state, self.__trans, self.__finals, self.__biggest_state)
