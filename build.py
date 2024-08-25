import json
from pathlib import Path
import shutil
from base_config import config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from logging import getLogger
import os

from localization.templatetag import TransIncludeExtension
from minify import minify

logger = getLogger(__name__)


def build() -> None:
    srcDir = config().SRC_DIR
    isUseLocalization = config().LOCALE_CONFIG is not None
    env = Environment(
        loader=FileSystemLoader(srcDir),
        trim_blocks=True,
        autoescape=select_autoescape(),
        extensions=[TransIncludeExtension] if isUseLocalization else [],
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
        if isUseLocalization:
            localeDir: Path = config().LOCALE_CONFIG.LOCALE_DIR  # type: ignore
            localeFiles = localeDir.glob("*.json")
            locales = list(
                map(lambda f: ".".join(f.name.split(".")[:-1]), localeFiles)
            )
            if True in list(
                map(
                    lambda locale: str(file.resolve()).startswith(
                        str((srcDir / locale).resolve())
                    ),
                    locales,
                )
            ):
                continue
            buildWithLocalization(srcDir, env, file)
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
            f.write(minify(template.render(), file.suffix[1:]))
    logger.warn("Successfully built!")


def buildWithLocalization(srcDir: Path, env: Environment, file: Path):
    exportDir = config().BASE_DIR / "build"
    localeDir: Path = config().LOCALE_CONFIG.LOCALE_DIR  # type: ignore
    localeFiles = localeDir.glob("*.json")
    locales = list(
        map(lambda f: ".".join(f.name.split(".")[:-1]), localeFiles)
    )
    localesStr = "[" + ",".join(map(lambda s: f'"{s.upper()}"', locales)) + "]"
    with open(exportDir / "index.html", "w") as f:
        f.write(localeRedirectIndex(localesStr))

    for locale in locales:
        os.environ["buildLang"] = locale
        localeFile = localeDir / f"{locale}.json"
        with open(localeFile, "r") as f:
            localeJson = json.load(f)
        buildLocaleDir = exportDir / locale
        if not buildLocaleDir.exists():
            buildLocaleDir.mkdir()

        templateName = str(file.relative_to(srcDir))
        template = env.get_template(templateName)
        exportPath = buildLocaleDir / file.relative_to(srcDir)
        if not (exportPath.parent.exists()):
            exportPath.parent.mkdir()
        with open(exportPath, "w") as f:
            f.write(minify(template.render(trans=localeJson), file.suffix[1:]))
    del os.environ["buildLang"]


def localeRedirectIndex(localesStr: str) -> str:
    return minify(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting...</title>
</head>
<body>
    <script>
    const lang = navigator.languages.map(
        (e) => e.toUpperCase()).map((lang) => {{
        console.log({localesStr});console.log(lang);
            for (const spLang of {localesStr}){{
                if (lang.toUpperCase().includes(spLang)){{return spLang}}
            }}
            return undefined;
        }}
    )[0];
    console.log(lang);
    if (lang == undefined){{
        location.href = {config().LOCALE_CONFIG.DEFAULT_LANG}"""  # type:ignore
        f"""
    }}
    location.href = "./" + lang.toLowerCase() + "/";
    </script>
</body>
</html>
    """,
        ext="html",
        HTMLRemoveBr=True,
    )
