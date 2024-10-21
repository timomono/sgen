import contextlib
import ctypes
from typing import Callable

import time
import threading


def timeout(timeout_time: int):
    def wrapper(func: Callable):
        def wrapper2(*args, **kwargs):
            with timeout_context(timeout_time):
                return func(*args, **kwargs)

        return wrapper2

    return wrapper


@contextlib.contextmanager
def timeout_context(timeout_time):
    thread_id = ctypes.c_long(threading.get_ident())

    def raise_timeout():
        modified_thread_state_nums = (
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id, ctypes.py_object(TimeoutError)
            )
        )
        if modified_thread_state_nums == 0:
            raise ValueError(f"Invalid thread id ({thread_id})")
        elif modified_thread_state_nums > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            raise SystemError("PyThreadState_SetAsyncExc failure.")

    timer = threading.Timer(timeout_time, raise_timeout)
    timer.daemon = True
    timer.start()
    try:
        yield
    finally:
        timer.cancel()
        timer.join()


if __name__ == "__main__":

    @timeout(3)
    def main():
        print("sleeping")
        time.sleep(10)
        print("I slept well...")

    main()
