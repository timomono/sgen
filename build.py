from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def build(srcDir: Path):
    env = Environment(
        loader=FileSystemLoader(srcDir),
        trim_blocks=True,
    )
    files = srcDir.glob("*")
    for file in files:
        template = env.get_template(file.as_uri())
        result = template.render()
        print(result)
