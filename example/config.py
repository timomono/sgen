from pathlib import Path
from base_config import BaseConfig, LocalizationConfig


class Config(BaseConfig):
    DEBUG = False
    """Debug mode.

    Set it to False when deploying.
    """
    BASE_DIR = Path(__file__).resolve().parent
    """Project base directory."""
    LOCALE_CONFIG = LocalizationConfig()
    """Localization configuration.

    Set none to turn off localization.

    ### Example
    ```python
    class Config(BaseConfig):
        BASE_DIR = Path(__file__).resolve().parent
        LOCALE_CONFIG = LocalizationConfig()
    ```
    """
