from urllib.request import urlopen
from urllib.error import HTTPError
from pathlib import Path
from sys import stdout
from logging import getLogger

logger = getLogger(__name__)


def download(url: str, dest: Path, show_progress: bool = True) -> None:
    try:
        with urlopen(url) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"HTTP error while downloading {url}: {response.status}"
                )

            logger.info(f"Downloading {url} to {dest}...\n")
            with open(dest, "wb") as f:
                chunk_size = 1024 * 10
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                for chunk in iter(lambda: response.read(chunk_size), b""):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if show_progress and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        stdout.write(
                            f"\rDownloaded: {progress: 5.1f}%",
                        )
                        stdout.flush()
                if show_progress:
                    stdout.write("[Download done]\n")

    except HTTPError as e:
        raise RuntimeError(f"Download failed: {e}") from e


if __name__ == "__main__":
    download(
        "https://example.com/sample.zip",
        Path("sample.zip"),
    )
