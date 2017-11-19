def verify_expression(a, w: str) -> bool:
    """Checks whether word s satisfy automaton a"""
    a.reset()
    for symb in w:
        if not a.put(symb):
            return False
    return a.in_final_state()
