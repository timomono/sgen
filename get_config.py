from __future__ import annotations
from typing import TYPE_CHECKING
from importlib.machinery import ModuleSpec
from pathlib import Path
import importlib.util

print(TYPE_CHECKING)
if TYPE_CHECKING:
    from base_config import BaseConfig


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


sgen_config = get_config()
