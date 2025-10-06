from typing import Any


class AvoidEscape:
    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return f"AvoidEscape({self.value})"
