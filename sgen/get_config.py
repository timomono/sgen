from __future__ import annotations
import sys
from typing import TYPE_CHECKING
from importlib.machinery import ModuleSpec
from pathlib import Path
import importlib.util
from time import sleep

if TYPE_CHECKING:
    from sgen.base_config import BaseConfig


def get_config() -> "BaseConfig":
    print("getting config!")
    configFile = Path("./config.py")
    # importlib.util.spec_from_file_location(name, configFile)
    spec: ModuleSpec = importlib.util.spec_from_file_location(
        "config", configFile
    )  # type: ignore
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    configClass: type = getattr(module, "Config")
    print(configClass().DEBUG)
    sleep(1)
    return configClass()


class _ConfigGlobal:
    _instance = None
    _config_instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Making config instance")
            cls._instance = super(_ConfigGlobal, cls).__new__(cls)
            cls._config_instance = get_config()
        return cls._instance

    @staticmethod
    def reload():
        print("\nReloading. Making config instance\n")
        _ConfigGlobal._config_instance = get_config()

    @property
    def config_instance(self):
        # インスタンスから config_instance にアクセスするためのプロパティ
        return _ConfigGlobal._config_instance


def reload_config():
    print("\nReloading configuration\n")
    _ConfigGlobal.reload()
    # global sgen_config
    # This.sgen_config = _ConfigGlobal().config_instance


# sgen_config = _ConfigGlobal().config_instance


class This(sys.__class__):
    @property
    def sgen_config(self):
        print(
            "sgen config:", _ConfigGlobal().config_instance.DEBUG, flush=True
        )
        sleep(0.2)
        return _ConfigGlobal().config_instance


sys.modules[__name__].__class__ = This
