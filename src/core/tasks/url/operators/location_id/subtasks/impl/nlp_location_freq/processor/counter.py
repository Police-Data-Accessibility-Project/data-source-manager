


class RequestCounter:

    def __init__(self):
        self._counter: int = 0

    def next(self) -> int:
        self._counter += 1
        return self._counter