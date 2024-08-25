from abc import ABC, abstractmethod
from logging import getLogger
from base_config import config
from build import build  # type: ignore

logger = getLogger(__name__)


class Command(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def run(self):
        pass


class Build(Command):
    # pass
    name = "build"

    def run(self):
        build(config().SRC_DIR)


commands: list[Command] = [Build()]
