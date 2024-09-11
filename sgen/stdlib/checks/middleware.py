from abc import abstractmethod
from pathlib import Path
from typing import override
from base_middleware import BaseMiddleware


class BaseCheck:
    @abstractmethod
    @property
    def name(self) -> str:
        """Check name."""
        pass

    @abstractmethod
    def check(self) -> None:
        """Do check.
        Raise FailedCheckError when a problem is found during a check
        """
        pass


class FailedCheckError(Exception):
    """Raise when a problem is found during a check"""

    def __init__(self, *, check: BaseCheck, error: str) -> None:
        super().__init__(f'Check "{check.name} failed. {error}')


class ChecksMiddleware(BaseMiddleware):
    def __init__(self, checks) -> None:
        self.checks: list[BaseCheck] = checks
        super().__init__()

    @override
    def do(self, buildPath: Path):
        for check in self.checks:
            check.check()
