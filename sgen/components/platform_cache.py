from pathlib import Path
import os
import platform

APP_NAME = "sgen"


def get_cache_dir() -> Path:
    system: str = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Caches" / APP_NAME

    if system == "Windows":
        local_appdata: str = os.environ.get("LOCALAPPDATA", "")
        return Path(local_appdata) / APP_NAME

    # Linux / others (XDG)
    xdg: str | None = os.environ.get("XDG_CACHE_HOME")
    base: Path = Path(xdg) if xdg else Path.home() / ".cache"
    return base / APP_NAME
