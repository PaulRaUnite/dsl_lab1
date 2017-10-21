from automata import Automata


def verify_expression(m: Automata, s: str) -> bool:
    """Checks whether expression satisfy automata."""
    m.reset()
    for symb in s:
        if not m.put(symb):
            return False
    return m.is_final_state()
