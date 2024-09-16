from __future__ import annotations
from typing import TYPE_CHECKING
from importlib.machinery import ModuleSpec
from pathlib import Path
import importlib.util

if TYPE_CHECKING:
    from sgen.base_config import BaseConfig


def get_config() -> "BaseConfig":
    configFile = Path("./config.py")
    # importlib.util.spec_from_file_location(name, configFile)
    spec: ModuleSpec = importlib.util.spec_from_file_location(
        "config", configFile
    )  # type: ignore
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    configClass: type = getattr(module, "Config")
    return configClass()


class ConfigGlobal:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigGlobal, cls).__new__(cls)
            cls.config_instance = get_config()
        return cls._instance


sgen_config = ConfigGlobal().config_instance
