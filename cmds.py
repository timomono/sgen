from abc import ABC, abstractmethod
from logging import getLogger

logger = getLogger(__name__)


class Command(ABC):
    @property
    @abstractmethod
    def name(self): pass

    @abstractmethod
    def run(self): pass


class Build(Command):
    # pass
    name = "build"

    def run(self):
        print("build")


commands: list[Command] = [Build()]
