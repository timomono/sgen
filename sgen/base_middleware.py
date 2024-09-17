from abc import ABC, abstractmethod
from pathlib import Path


class MiddlewareNotUsedError(Exception):
    """Raise when a problem is found during a check"""


class BaseMiddleware(ABC):
    """Modify files and directory structure during build.
    These operations are allowed:
    - Modifying the folder structure
    - Modifying file contents

    example:
    ```python
    class ReplaceProjectNameMiddleware(BaseMiddleware):
        def __init__(self, checks) -> None:
            self.checks: list[BaseCheck] = checks
            super().__init__()
        @override
        def do(self, buildPath: Path):
            buildPath.
    ```
    """

    @abstractmethod
    def do(self, build_path: Path) -> None:
        """Called at build time.
        These operations are allowed:
        - Modifying the folder structure
        - Modifying file contents
        """
        pass
