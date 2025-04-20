from abc import ABC
from io import BufferedWriter, BufferedReader
from pathlib import Path


class BaseRenderer(ABC):
    def render(
        self,
        render_from: BufferedReader,
        render_to: BufferedWriter,
        path: Path,
    ) -> None:
        pass
