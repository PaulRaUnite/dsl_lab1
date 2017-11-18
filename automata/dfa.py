from typing import *

from automata import NDFA

__all__ = []


class DetTransitions:
    """Class that implements transition table for deterministic state machine."""

    def __init__(self, d: Dict[int, Dict[str, int]] = None):
        """Constructor for transitions of DFA."""
        if d is None:
            d = dict()
        self.__graph = d

    def get_graph(self):
        """Returns transition graph."""
        return self.__graph

    def __iter__(self):
        """Returns iterator through the all transitions."""
        for origin_state, moves in self.__graph.items():
            for symb, end_state in moves.items():
                yield origin_state, symb, end_state,

    def add(self, from_state: int, symb: str, to_state: int):
        """Adds new state or replace the existing one's end state."""
        if from_state not in self.__graph:
            self.__graph[from_state] = dict()

        self.__graph[from_state][symb] = to_state

    def get_end(self, from_state: int, symb: str) -> int:
        """
        Returns end state of transition from the state by symbol or
        :raises KeyError.
        """
        return self.__graph[from_state][symb]

    def delete(self, from_state: int, symb: str, to_state: int):
        """Removes the transition or do nothing."""
        try:
            self.__graph[from_state][symb] = to_state
        finally:
            if len(self.__graph[from_state]) == 0:
                del self.__graph[from_state]

    def __str__(self) -> str:
        """Returns string representation of the graph."""
        return self.__graph.__str__()


class Mapping:
    """Mapping class provides bijection between sets of ints and ints."""

    def __init__(self):
        """Constructor of mapping."""
        self.to: List[Tuple[bool, Set[int]]] = list()
        self.inv = dict()

    def map(self, states: Tuple[bool, Set[int]]) -> int:
        """Maps the state to number."""
        for i in range(0, len(self.to)):
            if self.to[i] == states:
                return i

        to_len = len(self.to)
        self.to.append(states)
        self.inv[to_len] = states
        return to_len

    def unmap(self, number: int) -> Tuple[bool, Set[int]]:
        """Returns set that corresponds to the number."""
        return self.inv[number]

    def finals(self) -> Set[int]:
        """Returns set of number of states that are final."""
        f = set()
        for i in range(0, len(self.to)):
            if self.to[i][0]:
                f.add(i)
        return f


def group(nd: NDFA, states: Set[int]) -> Dict[chr, Tuple[bool, Set[int]]]:
    """Returns all symbols and states for which transitions exist."""
    d: Dict[chr, Tuple[bool, Set[int]]] = dict()
    raw_trans = nd.T.graph()
    for state in states:
        if state not in raw_trans:
            continue
        for s, end in raw_trans[state].items():
            finality = nd.F.intersection(end)
            try:
                d[s] = (d[s][0] or finality, d[s][1].union(end))
            except KeyError:
                d[s] = (finality, end)
    return d


def tri_matr_it_gen(m: List[List[int]]):
    """Iterator through triangled matrix."""
    for x in range(len(m)):
        for y in range(len(m[x])):
            yield x, y


# Helper function that returns equality set for some state
# using matrix of equality. It writes states that has its equal set
# but not the initial state of recursion.
def equality_set(viewed: Set[int], matrix: List[List[int]], state: int) -> Set[int]:
    """Returns equality set for the state."""
    equal: Set[int] = {state}
    for s in range(state, len(matrix)):
        if matrix[s][state] == 0:
            viewed.add(s + 1)
            equal = equal.union(equality_set(viewed, matrix, s + 1))
    return equal


class DFA:
    """The class that implements deterministic state machine."""

    def __init__(self, trans: DetTransitions, fins: Set[int]):
        """Constructor for DFA."""
        self.__state = 0
        self.T = trans
        self.F = fins
        max_state = 1

        for [orig, _, end] in self.T:
            if orig > max_state:
                max_state = orig
            if end > max_state:
                max_state = end

        self.__biggest_state: int = max_state

    def put(self, symb: str) -> bool:
        """Do one move inside the automata."""
        try:
            self.__state = self.T.get_end(self.__state, symb)
        except KeyError:
            self.__state = -1
            return False
        return True

    def reset(self) -> None:
        """Resent current states."""
        self.__state = 0

    def is_final_state(self) -> bool:
        """Checks whether the automata is into one of finite states."""
        return self.__state in self.F

    @classmethod
    def from_ndfa(cls, nd: NDFA) -> 'DFA':
        """Transforms NDFA to DFA."""
        # Mapping for current automata.
        known = Mapping()
        start_point = known.map((len((nd.I.intersection(nd.F))) > 0, nd.I.copy()))
        queue: List[int] = [start_point]
        # Set of numbers of new but processed states.
        processed: Set[int] = set()
        # transitions of new automata
        new_T = DetTransitions()
        while True:
            try:
                # Get the next state,
                orig_num = queue.pop()
                # if we already have worked with it,
                if orig_num in processed:
                    # skip it
                    continue
                # or add to the set of the processed,
                processed.add(orig_num)

                # gets set of states itself,
                origs = known.unmap(orig_num)
                # receive trasition state sets for symbols,
                tr = group(nd, origs[1])
                for symb, ends in tr.items():
                    # encrypt them by mapping,
                    end_num = known.map(ends)
                    # write as transition in new transition graph,
                    new_T.add(orig_num, symb, end_num)
                    # adds to the queue.
                    queue.append(end_num)
            except IndexError:
                # The queue is empty.
                break
        # New finals.
        new_F = known.finals()
        return cls(new_T, new_F)

    def minify(self) -> 'DFA':
        """Minifies the DFA."""
        # Generation of triangle matrix.
        # It looks like:
        # s1\s2 0 1 2 3
        #   1:  0
        #   2:  1 1
        #   3:  0 1 0
        #   4:  1 0 1 1
        # It writes 1 if one of the states is final
        # and other is not(XOR), else 0.
        m: List[List[int]] = []
        for s1 in range(1, self.__biggest_state + 1):  # lines
            m.append(list())
            for s2 in range(0, s1):
                if (s1 in self.F) ^ (s2 in self.F):  # columns
                    m[s1 - 1].append(1)
                else:
                    m[s1 - 1].append(0)

        # Receive all symbols that are used.
        vocabulary: Set[chr] = set()
        for _, symb, _ in self.T:
            vocabulary.add(symb)

        # While there is changes in the matrix
        # check all states that possibly equal
        # (0 in matrix) and get states
        # that can be accessible by the same symbol
        # from the states:
        # if they are not equal or only one of them has transition
        # than the possibly equal are not equal and 1 must be written.
        #
        # The algorithm finish it work because the matrix
        # is finite, and at each step it finds all states
        # that cannot be equal using the information of
        # the matrix. If there is not conditions that the states
        # are not equal than they are equal.
        changes = True
        while changes:
            changes = False
            for s1, s2 in tri_matr_it_gen(m):
                if m[s1][s2] == 0:
                    for symb in vocabulary:
                        exception_count = 0
                        try:
                            x_tr = self.T.get_end(s1 + 1, symb)
                        except KeyError:
                            exception_count += 1
                        finally:
                            try:
                                y_tr = self.T.get_end(s2, symb)
                                # States with the same number are
                                # are always equal.
                                if exception_count == 0 and x_tr != y_tr:
                                    # Using triangle matrix, should
                                    # be careful with indexing.
                                    if y_tr > x_tr:
                                        x_tr, y_tr = y_tr, x_tr
                                    if m[x_tr + 1][y_tr] == 1:
                                        m[s1][s2] = 1
                                        changes = True
                                        break
                            except KeyError:
                                exception_count += 1
                        # One has the transition but another
                        # hasn't means they are not equal.
                        if exception_count == 1:
                            m[s1][s2] = 1
                            changes = True
                            break

        viewed: Set[int] = set()
        eq_sets: List[Set[int]] = []
        # For all states in the automata,
        # receive their equality sets.
        for state in range(self.__biggest_state + 1):
            if state not in viewed:
                eq_sets.append(equality_set(viewed, m, state))

        # Transform rules for merging equal states.
        trans_rules: Dict[int, int] = dict()
        for eq_set in eq_sets:
            # Choose one of the states as main.
            # 0 is a special state, it is initial,
            # so equality set that can contain it
            # must have it as main.
            # In other cases it doesn't matter.
            main_state: int = 0
            if 0 not in eq_set:
                main_state = eq_set.pop()

            # Mark the state to be replaced by
            # the main state as well as the main
            # state itself.
            trans_rules[main_state] = main_state
            for state in eq_set:
                trans_rules[state] = main_state

        # Transform old transitions and finals states
        # following the rules.
        new_T = DetTransitions()
        for orig, symb, end in self.T:
            new_T.add(trans_rules[orig], symb, trans_rules[end])
        new_F: Set[int] = set()
        for state in self.F:
            new_F.add(trans_rules[state])
        return DFA(new_T, new_F)

    def __str__(self) -> str:
        """Returns string representation of the automata."""
        return "state: {}\n" \
               "trans: {}\n" \
               "final: {}\n" \
               "bigst: {}".format(self.__state, self.T, self.F, self.__biggest_state)
