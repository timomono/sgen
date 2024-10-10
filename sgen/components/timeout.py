import signal
from typing import Callable

from sgen.components.override_decorator import OverrideStrict, override


def timeout(timeout_time: int):
    def wrapper(func: Callable):
        def wrapper2(*args, **kwargs):
            start_timeout(timeout_time)
            res = func(*args, **kwargs)
            finish_timeout()
            return res

        return wrapper2

    return wrapper


def start_timeout(timeout_time: int):
    signal.signal(
        signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError())
    )
    signal.alarm(timeout_time)


def finish_timeout():
    signal.alarm(0)


class Timeout(OverrideStrict):
    @override
    def __init__(self, timeout_time: int) -> None:
        self.timeout_time = timeout_time
        super().__init__()

    def __enter__(self):
        start_timeout(self.timeout_time)
        return

    def __exit__(self, *args):
        finish_timeout()
