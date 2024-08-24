from abc import ABC, abstractmethod
from logging import getLogger

from base_config import config

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
        print(config.BASE_DIR)


commands: list[Command] = [Build()]
