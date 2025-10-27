from abc import ABC
from io import BufferedWriter, BufferedReader
from pathlib import Path
from typing import BinaryIO


class BaseRenderer(ABC):
    def render(
        self,
        render_from: BufferedReader | BinaryIO,
        render_to: BufferedWriter | BinaryIO,
        path: Path,
    ) -> None:
        pass
