import shutil
import sys
from logging import getLogger
from sgen.get_config import sgen_config
import re

from sgen.stdlib.localization.templatetag import (
    TransIncludeExtension,
    TransExtension,
)

logger = getLogger(__name__)
RE_IGNORE_COMMENTS = re.compile(
    rb"<!--\s*sgen\s*:\s*ignore\s*-->", re.IGNORECASE
)


def build() -> None:
    srcDir = sgen_config.SRC_DIR
    files = srcDir.glob("**/*")
    if sgen_config.BUILD_DIR.exists():
        logger.info("Build directory already exists. Removing...")
        if sys.version_info >= (3, 12):
            shutil.rmtree(
                sgen_config.BUILD_DIR, onexc=lambda _, __, ___: None
            )  # TODO: Python 3.13 doesn't need onexc?
        else:
            shutil.rmtree(
                sgen_config.BUILD_DIR, ignore_errors=True
            )  # TODO: Python 3.13 doesn't need onexc?
    sgen_config.BUILD_DIR.mkdir()
    TEMPLATE_EXTS = [".txt", ".text", ".html", ".htm", ".css", ".js", ".php"]
    IGNORE_EXTS = [".scss", ".sass", ".ts"]
    for file in files:
        if file.is_dir():
            continue

        if file in sgen_config.IGNORE_FILES:
            continue
        if file.suffix in IGNORE_EXTS:
            continue
        exportPath = sgen_config.BUILD_DIR / file.relative_to(srcDir)

        # result = template.render()
        # with open(file, mode="r") as f:
        #     template = Template(f.read())
        with open(file, "rb") as from_:
            if RE_IGNORE_COMMENTS.match(from_.readline()) != None:
                logger.info(f"Skipping {file} due to ignore comment")
                continue

            from_.seek(0)

            if not (exportPath.parent.exists()):
                exportPath.parent.mkdir(parents=True)

            if file.suffix not in TEMPLATE_EXTS:
                shutil.copy(
                    file, sgen_config.BUILD_DIR / file.relative_to(srcDir)
                )
                continue

            with open(
                sgen_config.BUILD_DIR / file.relative_to(srcDir), "wb"
            ) as to:
                sgen_config.RENDERER.render(
                    from_, to, file.relative_to(srcDir)
                )
    for middleware in sgen_config.MIDDLEWARE:
        middleware.do(sgen_config.BUILD_DIR)
