import json
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from logging import getLogger
import os
from get_config import sgen_config

from stdlib.localization.templatetag import TransIncludeExtension
from stdlib.smini.smini import minify

logger = getLogger(__name__)


def build() -> None:
    srcDir = sgen_config.SRC_DIR
    isUseLocalization = sgen_config.LOCALE_CONFIG is not None
    env = Environment(
        loader=FileSystemLoader(srcDir),
        trim_blocks=True,
        autoescape=select_autoescape(),
        extensions=[TransIncludeExtension] if isUseLocalization else [],
    )
    files = srcDir.glob("**/*")
    if sgen_config.BUILD_DIR.exists():
        logger.info("Build directory already exists. Removing...")
        shutil.rmtree(sgen_config.BUILD_DIR)
    sgen_config.BUILD_DIR.mkdir()
    for file in files:
        if file.is_dir():
            continue
        if file in sgen_config.IGNORE_FILES:
            continue
        if isUseLocalization:
            localeDir: Path = sgen_config.LOCALE_CONFIG.LOCALE_DIR  # type: ignore
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
        exportPath = sgen_config.BUILD_DIR / file.relative_to(srcDir)
        if not (exportPath.parent.exists()):
            exportPath.parent.mkdir()
        with open(sgen_config.BUILD_DIR / file.relative_to(srcDir), "w") as f:
            f.write(template.render())
    for middleware in sgen_config.MIDDLEWARE:
        middleware.do(sgen_config.BUILD_DIR)


class NoLangFoundException(Exception):
    def __init__(self, message="hwy") -> None:
        self.message = (
            "No language for localization found. "
            "Currently LOCALE_DIR is set to"
            f' "{sgen_config.LOCALE_CONFIG.LOCALE_DIR}".'  # type:ignore
        )
        super().__init__(self.message)


def buildWithLocalization(srcDir: Path, env: Environment, file: Path):
    localeDir: Path = sgen_config.LOCALE_CONFIG.LOCALE_DIR  # type: ignore
    if not localeDir.exists():
        raise FileNotFoundError(
            "LOCALE_DIR specified in config.py does not exist"
        )
    localeFiles = localeDir.glob("*.json")
    locales = list(
        map(lambda f: ".".join(f.name.split(".")[:-1]), localeFiles)
    )
    localesStr = "[" + ",".join(map(lambda s: f'"{s.upper()}"', locales)) + "]"
    with open(sgen_config.BUILD_DIR / "index.html", "w") as f:
        f.write(localeRedirectIndex(localesStr))

    if locales == []:
        raise NoLangFoundException()

    for locale in locales:
        os.environ["buildLang"] = locale
        localeFile = localeDir / f"{locale}.json"
        with open(localeFile, "r") as f:
            localeJson = json.load(f)
        buildLocaleDir = sgen_config.BUILD_DIR / locale
        if not buildLocaleDir.exists():
            buildLocaleDir.mkdir()

        templateName = str(file.relative_to(srcDir))
        template = env.get_template(templateName)
        exportPath = buildLocaleDir / file.relative_to(srcDir)
        if not (exportPath.parent.exists()):
            exportPath.parent.mkdir()
        with open(exportPath, "w") as f:
            f.write(template.render(trans=localeJson))
    if "buildLang" in os.environ:
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
        location.href = {sgen_config.LOCALE_CONFIG.DEFAULT_LANG}"""  # type:ignore
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
