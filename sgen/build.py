import shutil
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
        shutil.rmtree(sgen_config.BUILD_DIR)
    sgen_config.BUILD_DIR.mkdir()
    TEMPLATE_EXTS = [".txt", ".text", ".html", ".htm", ".css", ".js", ".php"]
    for file in files:
        if file.is_dir():
            continue
        if file in sgen_config.IGNORE_FILES:
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
            f.write(template.render())
    for middleware in sgen_config.MIDDLEWARE:
        middleware.do(sgen_config.BUILD_DIR)
