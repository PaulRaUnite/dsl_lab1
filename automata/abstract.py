from typing import Callable


def map(src, dst, map_orig: Callable[[int], int], map_end: Callable[[int], int]):
    if src is dst:
        raise Exception

    for origin, symb, end in src:
        dst.add(map_orig(origin), symb, map_end(end))
