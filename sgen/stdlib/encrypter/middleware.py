from pathlib import Path
import shutil

from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override


class EncrypterMiddleware(BaseMiddleware):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def do(self, build_path: Path) -> None:
        template_dir = Path(__file__).parent / "register"
        target_dir = build_path / "encrypter" / "register"

        if target_dir.exists():
            raise FileExistsError(
                "Directory 'encrypter/register' already exists"
            )

        target_dir.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(template_dir, target_dir)
        return super().do(build_path)
