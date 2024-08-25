from pathlib import Path
from base_config import BaseConfig, LocalizationConfig


class Config(BaseConfig):
    DEBUG = False
    BASE_DIR = Path(__file__).resolve().parent
    LOCALE_CONFIG = LocalizationConfig()
