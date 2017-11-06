from typing import Callable, Dict, Set, Tuple

__all__ = ["NonDetAutomata"]


class NonDetTransitions:
    """Transitions is a wrapper for a graph of moves over non-deterministic state machine."""

    def __init__(self, d: Dict[int, Dict[chr, Set[int]]] = None):
        """Constructor for a non-deterministic transitions graph."""

        if d is None:
            d = dict()
        self.__graph = d

    def graph(self) -> Dict[int, Dict[chr, Set[int]]]:
        """Returns inner structure."""

        return self.__graph

    def __iter__(self):
        """Generator of iterator though all transitions."""

        for origin_state, moves in self.__graph.items():
            for symb, end_set in moves.items():
                for end_state in end_set:
                    yield origin_state, symb, end_state,

    def add(self, from_state: int, symb: chr, to_state: int) -> None:
        """Adds transition from the state by symbol to the other state."""

        if from_state not in self.__graph:
            self.__graph[from_state] = dict()

        if symb not in self.__graph[from_state]:
            self.__graph[from_state][symb] = set()

        self.__graph[from_state][symb].add(to_state)

    def get_end_states(self, from_state: int, symb: chr) -> Set[int]:
        """
        Returns end states from some state by some symbol.
        Raise KeyError exception if nothing found.
        """

        return self.__graph[from_state][symb]

    def delete(self, transition: Tuple[int, chr, int]) -> None:
        """Deletes the following transition."""

        [from_state, symb, to_state] = transition
        try:
            self.__graph[from_state][symb].add(to_state)
        finally:
            if len(self.__graph[from_state][symb]) == 0:
                del self.__graph[from_state][symb]
            if len(self.__graph[from_state]) == 0:
                del self.__graph[from_state]

    def map(self, dst: 'NonDetTransitions', map_orig: Callable[[int], int], map_end: Callable[[int], int]) -> None:
        """
        Performs transformation(mapping) of origin and end states
        of some Transition and saves the result into another one.
        Raises exception if src == dst.
        """

        if self is dst:
            raise Exception("Can't perform transformation on the same collection.")

        for origin, symb, end in self:
            dst.add(map_orig(origin), symb, map_end(end))

    def union(self, trans: 'NonDetTransitions') -> 'NonDetTransitions':
        """Returns the union of two transitions."""
        new = self.copy()
        for origin, symb, fin in trans:
            new.add(origin, symb, fin)
        return new

    def copy(self) -> 'NonDetTransitions':
        """Copies the transition."""
        new = NonDetTransitions()
        for s1, symb, s2 in self:
            new.add(s1, symb, s2)
        return new

    def __str__(self) -> str:
        """Returns string representation of the graph."""
        return self.__graph.__str__()


class NonDetAutomata:
    """
    Automata is a class that represents non-deterministic finite automata.

    The following realization assumes that every automata can have multiple
    entry states and can have multiple final states.
    """

    def __init__(self, starts: Set[int], finals: Set[int], trans: NonDetTransitions):
        """Constructor for non-deterministic finite state machine."""

        # Init(entry) states.
        self.I: Set[int] = starts
        # Current stepping states.
        self.step_states: Set[int] = starts.copy()
        # Transition graph.
        self.T: NonDetTransitions = trans
        # Final states.
        self.F: Set[int] = finals

        # The maximum state computing.
        max_state: int = 1
        for [orig, _, end] in self.T:
            if orig > max_state:
                max_state = orig
            if end > max_state:
                max_state = end

        for state in self.I:
            if state > max_state:
                max_state = state

        for state in self.F:
            if state > max_state:
                max_state = state

        self._biggest_state: int = max_state

    def put(self, symb: chr) -> bool:
        """
        Do one move through the machine graph by the following symbol.
        The state is split if it moves through a fork with the same symbol transitions.
        """

        new_states = set()
        # Use current states as queue.
        for state in self.step_states:
            try:
                # Gets all states from states by the symbol from the state.
                for next_state in self.T.get_end_states(state, symb):
                    new_states.add(next_state)
            except KeyError:
                pass

        self.step_states = new_states
        if len(new_states) > 0:
            return True
        return False

    def reset(self) -> None:
        """Reset current states."""

        self.step_states = self.I.copy()

    def is_final_state(self) -> bool:
        """Checks whether the automata is into one of finite states."""
        # If some current state in final state.
        return len(self.step_states.intersection(self.F)) > 0

    @classmethod
    def shifting(cls, self, n: int) -> 'NonDetAutomata':
        """
        Adds the number for all states and returns new automata.
        Helps to not to intersect two different machines while merging.
        """

        # Create new transition graph with shifted states.
        new_trans: NonDetTransitions = NonDetTransitions()
        self.T.map(new_trans, lambda x: x + n, lambda x: x + n)

        # Shift start and final states.
        new_starts: Set[int] = set()
        for state in self.I:
            new_starts.add(state + n)

        new_finals: Set[int] = set()
        for state in self.F:
            new_finals.add(state + n)

        return cls(new_starts, new_finals, new_trans)

    def __len__(self) -> int:
        """Returns size of the machine(count of states)."""
        return self._biggest_state + 1

    def __str__(self) -> str:
        """Returns string representation of the automata."""
        return "Machine (\n" \
               "    I: {}\n" \
               "    T: {}\n" \
               "    F: {}\n" \
               "    Biggest state: {}\n" \
               "    Cur. states: {}\n)".format(self.I, self.T, self.F, self._biggest_state, self.step_states)

    def copy(self) -> 'NonDetAutomata':
        """Copies the automata."""

        return NonDetAutomata(self.I.copy(), self.F.copy(), self.T.copy())

    @classmethod
    def by_value(cls, s: chr) -> 'NonDetAutomata':
        """Creates the automata from the single character."""

        return cls({0}, {1}, NonDetTransitions({0: {s: {1}}}))

    @classmethod
    def by_concatenation(cls, m1: 'NonDetAutomata', m2: 'NonDetAutomata') -> 'NonDetAutomata':
        """Constructs a new automata from existing two by concatenation."""

        # Do the machines not overlapping.
        shift: int = len(m1)
        m2 = NonDetAutomata.shifting(m2, shift)

        # Start states of new automata equals
        # to the states of the first automata.
        new_I = m1.I.copy()
        # Final states of new automata equals
        # to the states of the first automata.
        new_F = m2.F.copy()

        # But if there are some states if the first automata
        # (it means there is some clini closure)
        # the part of new automata can be missed by some words
        # so start states of the second automata must be added too.
        InF = m1.I.intersection(m1.F)
        if len(InF) > 0:
            new_I = new_I.union(m2.I)

        # Connections between start states of the
        # first machine, that have transitions to
        # finals of the first machine, and init
        # states of the second machine.
        ts = NonDetTransitions()
        for orig, symb, _ in m1.T:
            for start_state in m2.I:
                ts.add(orig, symb, start_state)

        # Final transition graph.
        new_trans = m1.T.union(m2.T).union(ts)
        return cls(new_I, new_F, new_trans)

    @classmethod
    def by_decision(cls, m1: 'NonDetAutomata', m2: 'NonDetAutomata') -> 'NonDetAutomata':
        """Constructs a new automata from existing two by disjunction."""

        # Do the machines not overlapping.
        shift: int = len(m1)
        m2 = NonDetAutomata.shifting(m2, shift)

        # Simply union everything from the second
        # machine with the first one.
        new_trans = m1.T.union(m2.T)
        new_starts = m1.I.union(m2.I)
        new_finals = m1.F.union(m2.F)
        return cls(new_starts, new_finals, new_trans)

    @classmethod
    def by_closure(cls, m: 'NonDetAutomata') -> 'NonDetAutomata':
        """Constructs new automata performing Clini closure."""

        # New machine.
        new_m = m.copy()

        # Adds new transitions from all states,
        # that have transitions to the final states,
        # to all start states.
        for orig, symb, end in m.T:
            if end in m.F:
                for start_state in m.I:
                    new_m.T.add(orig, symb, start_state)

        # And union final states with start ones.
        new_m.F = new_m.F.union(new_m.I)
        return new_m
