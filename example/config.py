from pathlib import Path
from base_config import BaseConfig


class Config(BaseConfig):
    BASE_DIR = Path(__file__).resolve().parent
