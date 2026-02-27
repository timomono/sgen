from pathlib import Path

from sgen.components.override_decorator import OverrideStrict


class MiddlewareNotUsedError(Exception):
    """Raise when a problem is found during a check"""


class BaseMiddleware(OverrideStrict):
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

    def before(self, build_path: Path) -> None:
        """Called before build.
        - Modifying the folder structure
        - Modifying file contents
        """
        pass

    def after(self, build_path: Path) -> None:
        """Called after build.
        - Modifying the folder structure
        - Modifying file contents
        """
        pass

    def do(self, build_path: Path) -> None:
        """Called at build time.
        - Modifying the folder structure
        - Modifying file contents
        """
        pass
