import platform
from typing import Final


TAILWIND_BINARIES: Final[dict[str, str]] = {
    "linux-x64": "tailwindcss-linux-x64",
    "linux-x64-musl": "tailwindcss-linux-x64-musl",
    "linux-arm64": "tailwindcss-linux-arm64",
    "linux-arm64-musl": "tailwindcss-linux-arm64-musl",
    "macos-x64": "tailwindcss-macos-x64",
    "macos-arm64": "tailwindcss-macos-arm64",
    "windows-x64": "tailwindcss-windows-x64.exe",
}


def detect_platform() -> str:
    system: str = platform.system().lower()
    machine: str = platform.machine().lower()

    # Normalize architecture
    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    # macOS
    if system == "darwin":
        return f"macos-{arch}"

    # Windows
    if system == "windows":
        return f"windows-{arch}"

    # Linux
    if system == "linux":
        libc_name, _ = platform.libc_ver()
        if libc_name == "musl":
            return f"linux-{arch}-musl"
        return f"linux-{arch}"

    raise RuntimeError(f"Unsupported OS: {system}")


BINARY_URL_PREFIX = (
    "https://github.com/tailwindlabs/tailwindcss/releases/download/"
)


def get_tailwind_binary_url(version: str) -> str:
    key = detect_platform()
    try:
        return BINARY_URL_PREFIX + "v" + version + "/" + TAILWIND_BINARIES[key]
    except KeyError:
        raise RuntimeError(f"No binary available for: {key}")


if __name__ == "__main__":
    print(get_tailwind_binary_url("3.4.1"))
