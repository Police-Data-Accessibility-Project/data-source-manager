
from itertools import count

COUNTER = count(1)

def next_int() -> int:
    return next(COUNTER)