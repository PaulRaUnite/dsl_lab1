from typing import Callable, Dict, Set

__all__ = ["NDAutomata", "ValueAutomata", "ConcatenationAutomata", "DecisionAutomata", "CliniAutomata"]


class NDTransitions:
    """Transitions is a wrapper for a graph of moves over non-deterministic state machine."""

    def __init__(self, d: Dict[int, Dict[str, Set[int]]]):
        self.graph = d

    def get_graph(self):
        return self.graph

    def __iter__(self):
        for origin_state, moves in self.graph.items():
            for symb, end_set in moves.items():
                for end_state in end_set:
                    yield origin_state, symb, end_state,

    def add(self, from_state: int, symb: str, to_state: int):
        if from_state not in self.graph:
            self.graph[from_state] = dict()

        if symb not in self.graph[from_state]:
            self.graph[from_state][symb] = set()

        self.graph[from_state][symb].add(to_state)

    def get_ends(self, from_state: int, symb: str) -> Set[int]:
        return self.graph[from_state][symb]

    def delete(self, from_state: int, symb: str, to_state: int):
        try:
            self.graph[from_state][symb].add(to_state)
        finally:
            if len(self.graph[from_state][symb]) == 0:
                del self.graph[from_state][symb]
            if len(self.graph[from_state]) == 0:
                del self.graph[from_state]

    def map(self, dst, trans_orig: Callable[[int], int], trans_end: Callable[[int], int]):
        """
        Performs transformation of origin and end states
        of some Transition and saves the result into another.
        Doesn't work if src == dst.
        """

        if type(dst) != NDTransitions:
            raise TypeError("dst must be Transitions.")
        if self is dst:
            raise Exception("Can't perform transformation on the same collection.")

        for [origin, symb, end] in self:
            dst.add(trans_orig(origin), symb, trans_end(end))


class NDAutomata:
    """
    Automata is a class that represents non-deterministic finite automata.

    The following realization assumes that every automata has one entry
    point in state 0 and can have multiple final states.
    """

    def __init__(self, final: Set[int], trans: NDTransitions):
        self.states: Set[int] = {0}
        self.trans: NDTransitions = trans
        self.final: Set[int] = final
        max_state: int = 1

        for [orig, _, end] in self.trans:
            if orig > max_state:
                max_state = orig
            if end > max_state:
                max_state = end

        self.biggest_state: int = max_state

    def put(self, symb: str) -> bool:
        """Do one move inside the automata."""
        new_states = set()
        for state in self.states:
            try:
                for next_state in self.trans.get_ends(state, symb):
                    new_states.add(next_state)
            except KeyError:
                pass

        self.states = new_states
        if len(new_states) > 0:
            return True
        return False

    def reset(self):
        """Resent current states."""
        self.states = {0}

    def is_final_state(self) -> bool:
        """Checks whether the automata is into one of finite states."""
        return len(self.states.intersection(self.final)) > 0

    def __str__(self) -> str:
        """Returns string representation of the automata."""
        return "state: {}\n" \
               "trans: {}\n" \
               "final: {}\n" \
               "bigst: {}".format(self.states, self.trans, self.final, self.biggest_state)


class ValueAutomata(NDAutomata):
    """ValueAutomata represents simple automata of one transition of some symbol."""

    def __init__(self, s: str):
        super().__init__({1}, NDTransitions({0: {s: {1}}}))


class ConcatenationAutomata(NDAutomata):
    def __init__(self, left: NDAutomata, right: NDAutomata):
        """Constructs new automata using concatenation"""
        left.reset()
        right.reset()

        closed = False
        if 0 in right.final:
            for [_, _, r_end] in right.trans:
                if r_end == 0:
                    closed = True

        # value which should be added to all states of right automata
        shift: int = left.biggest_state
        # resulted automata
        result: NDTransitions = NDTransitions({})
        # Connection between two automata.
        connections: NDTransitions = NDTransitions({})

        for [r_orig, r_symb, r_end] in right.trans:
            if r_orig == 0:
                for lfin in left.final:
                    connections.add(lfin, r_symb, r_end + shift)

        # for r_symb, out_states in right.trans.get_graph()[0].items():
        #     for state in out_states:
        #         for lfin in left.final:
        #             connections.add(lfin, r_symb, state + shift)

        # copying with shift
        right.trans.map(result, lambda x: x + shift, lambda x: x + shift)

        # copying
        connections.map(result, lambda x: x, lambda x: x)
        left.trans.map(result, lambda x: x, lambda x: x)

        # merging of final states
        new_finals: Set[int] = set()
        for f in right.final:
            new_finals.add(f + shift)

        # add final states of left machine in case of clini closure
        if closed:
            for f in left.final:
                new_finals.add(f)

        super().__init__(new_finals, result)


class DecisionAutomata(NDAutomata):
    def __init__(self, left: NDAutomata, right: NDAutomata):
        """Constructs new automata using disjunction."""
        left.reset()
        right.reset()

        shift: int = left.biggest_state + 1
        result: NDTransitions = NDTransitions({})
        left.trans.map(result, lambda x: x, lambda x: x)

        right.trans.map(result, lambda x: x + shift, lambda x: x + shift)

        right.trans.map(result, lambda x: 0 if x == 0 else x + shift, lambda x: x + shift)

        new_finals: Set[int] = set()
        for f in left.final:
            new_finals.add(f)
        for f in right.final:
            new_finals.add(f + shift)

        super().__init__(new_finals, result)


class CliniAutomata(NDAutomata):
    def __init__(self, oper: NDAutomata):
        """Constructs new automata using Clini closure."""
        oper.reset()

        result: NDTransitions = NDTransitions({})
        oper.trans.map(result, lambda x: x, lambda x: 0 if x in oper.final else x)

        oper.trans.map(result, lambda x: x, lambda x: x)

        new_final: Set[int] = {0, oper.biggest_state}
        super().__init__(new_final, result)
