from typing import Callable
import warnings


def deprecated(message_or_func: str | Callable):
    message: str | None = (
        None if callable(message_or_func) else message_or_func
    )

    def deprecated_decorator(f: Callable):
        # if isinstance(f, type):
        #     class WrappedClass(f):
        #         def __init__(self, *args, **kwargs):
        #             warnings.warn(
        #                 (
        #                     f"'{f.__name__}' is deprecated "
        #                     "and shouldn't be used. " + message
        #                     if message is not None
        #                     else ""
        #                 ),
        #                 DeprecationWarning,
        #                 2,
        #             )
        #             print("warning!")
        #             super().__init__(*args, **kwargs)

        #     return WrappedClass

        # def new_init(self, *args, **kwargs):
        #     f.__init__(self, *args, **kwargs)  # type:ignore

        #     warnings.warn(
        #         f"'{f.__name__}' is deprecated and shouldn't be used. "
        #         + message,
        #         DeprecationWarning,
        #         2,
        #     )
        # f.__init__ = new_init  # type:ignore

        def _wrapper(*args, **keywords):
            if message is None:
                raise TypeError("Message should not be callable")
            warnings.warn(
                f"'{f.__name__}' is deprecated and shouldn't be used. "
                + message,
                DeprecationWarning,
                2,
            )
            v = f(*args, **keywords)
            return v

        return _wrapper

    if callable(message_or_func):
        return deprecated_decorator(message_or_func)
    else:
        return deprecated_decorator
