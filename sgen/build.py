import shutil
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from logging import getLogger
from sgen.get_config import sgen_config

from sgen.stdlib.localization.templatetag import (
    TransIncludeExtension,
    TransExtension,
)

logger = getLogger(__name__)


def build() -> None:
    srcDir = sgen_config.SRC_DIR
    env = Environment(
        loader=FileSystemLoader(srcDir),
        trim_blocks=True,
        autoescape=select_autoescape(),
        extensions=[TransIncludeExtension, TransExtension],
    )
    files = srcDir.glob("**/*")
    if sgen_config.BUILD_DIR.exists():
        logger.info("Build directory already exists. Removing...")
        if sys.version_info >= (3, 12):
            shutil.rmtree(
                sgen_config.BUILD_DIR, onexc=lambda _, __, ___: None
            )  # TODO: Python 3.13 don't need onexc?
        else:
            shutil.rmtree(
                sgen_config.BUILD_DIR, ignore_errors=True
            )  # TODO: Python 3.13 don't need onexc?
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
        if not (exportPath.parent.exists()):
            exportPath.parent.mkdir(parents=True)

        if file.suffix not in TEMPLATE_EXTS:
            shutil.copy(file, sgen_config.BUILD_DIR / file.relative_to(srcDir))
            continue
        templateName = str(file.relative_to(srcDir))
        template = env.get_template(templateName)
        # result = template.render()
        # with open(file, mode="r") as f:
        #     template = Template(f.read())
        with open(sgen_config.BUILD_DIR / file.relative_to(srcDir), "w") as f:
            f.write(
                template.render(
                    relative_url="/" + str(file.relative_to(srcDir))
                )
            )
    for middleware in sgen_config.MIDDLEWARE:
        middleware.do(sgen_config.BUILD_DIR)
