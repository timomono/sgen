from pathlib import Path
import shutil
from base_config import config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from logging import getLogger

logger = getLogger(__name__)


def build(srcDir: Path):
    env = Environment(
        loader=FileSystemLoader(srcDir),
        trim_blocks=True,
        autoescape=select_autoescape(),
    )
    files = srcDir.glob("*")
    exportDir = config().BASE_DIR / "build"
    if exportDir.exists():
        logger.warn("Build directory already exists. Removing...")
        shutil.rmtree(exportDir)
    exportDir.mkdir()
    for file in files:
        if file in config().IGNORE_FILES:
            continue
        template = env.get_template(str(file.name))
        # result = template.render()
        # with open(file, mode="r") as f:
        #     template = Template(f.read())
        with open(exportDir / file.name, "w") as f:
            f.write(template.render())
    logger.warn("Successfully built!")
