from pathlib import Path
import shutil
from base_config import config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from logging import getLogger

logger = getLogger(__name__)


def build(srcDir: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(srcDir),
        trim_blocks=True,
        autoescape=select_autoescape(),
    )
    files = srcDir.glob("**/*.html")
    exportDir = config().BASE_DIR / "build"
    if exportDir.exists():
        logger.warn("Build directory already exists. Removing...")
        shutil.rmtree(exportDir)
    exportDir.mkdir()
    for file in files:
        if file in config().IGNORE_FILES:
            continue
        templateName = str(file.relative_to(srcDir))
        template = env.get_template(templateName)
        # result = template.render()
        # with open(file, mode="r") as f:
        #     template = Template(f.read())
        exportPath = exportDir / file.relative_to(srcDir)
        if not (exportPath.parent.exists()):
            exportPath.parent.mkdir()
        with open(exportDir / file.relative_to(srcDir), "w") as f:
            f.write(template.render())
    logger.warn("Successfully built!")
