from typing import Any
import warnings

override_func = set()


def override(func):
    override_func.add(func)
    return func


class OverrideStrictMeta(type):

    def __new__(
        cls, name: str, parents: tuple[type, ...], attrs: dict[str, Any]
    ):
        new = super().__new__(cls, name, parents, attrs)
        if parents == ():
            return new
        for attr_name, attr_value in attrs.items():
            if attr_name in dir(parents[0]):
                # Attribute is override
                if attr_value not in override_func and attr_name not in (
                    "__module__",
                ):
                    warnings.warn(
                        f"{attr_name} you are overriding "
                        f"but you don't have the @override decorator"
                    )
            else:
                if attr_value in override_func:
                    warnings.warn(
                        f"{attr_name} you are not overriding "
                        f"but you have the @override decorator"
                    )
        return new


class OverrideStrict:
    __metaclass__ = OverrideStrictMeta


if __name__ == "__main__":

    class parent(OverrideStrict):
        def hello(self):
            print("Say parent")

    class child(parent):
        @override
        def hello(self):
            print("Say child")

        def non_override(self):
            print("non-override!")

    hl = child()
