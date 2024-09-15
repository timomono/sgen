import json
from pathlib import Path
import shutil
from typing import override
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.smini.smini import minify
import re
from logging import getLogger

logger = getLogger(__name__)


class LocalizationConfig:
    """Localization configuration."""

    @property
    def LOCALE_DIR(self) -> Path:
        from sgen.get_config import sgen_config

        return sgen_config.BASE_DIR / "locale"

    @property
    def DEFAULT_LANG(self) -> str:
        return "en"


class NoLangFoundException(Exception):
    def __init__(self, message="hwy") -> None:
        from sgen.get_config import sgen_config

        self.message = (
            "No language for localization found. "
            "Currently LOCALE_DIR is set to"
            f' "{sgen_config.LOCALE_CONFIG.LOCALE_DIR}".'  # type:ignore
        )
        super().__init__(self.message)


class LocalizationMiddleware(BaseMiddleware):
    @override
    def __init__(self, config: LocalizationConfig) -> None:
        self.config = config
        super().__init__()

    @override
    def do(self, buildPath: Path):
        temp_path = buildPath / "trans_temp"
        temp_path.mkdir()
        # shutil.move(buildPath, temp_path)
        for file in list(buildPath.glob("**/*")):
            if file.is_dir():
                continue
            if file.name == "trans_temp":
                continue
            copy_to = temp_path / file.relative_to(buildPath)
            copy_to.parent.mkdir(exist_ok=True)
            file.rename(copy_to)
        for path in buildPath.iterdir():
            if path.name != "trans_temp":
                path.rmdir()
        localeDir: Path = self.config.LOCALE_DIR  # type: ignore
        if not localeDir.exists():
            raise FileNotFoundError(
                "LOCALE_DIR specified in config.py does not exist"
            )
        localeFiles = localeDir.glob("*.json")
        locales = list(
            map(lambda f: ".".join(f.name.split(".")[:-1]), localeFiles)
        )
        localesStr = (
            "[" + ",".join(map(lambda s: f'"{s.upper()}"', locales)) + "]"
        )
        with open(buildPath / "index.html", "w") as f:
            f.write(localeRedirectIndex(localesStr, self.config))

        if locales == []:
            raise NoLangFoundException()

        for locale in locales:
            buildLocaleDir = buildPath / locale
            if not buildLocaleDir.exists():
                buildLocaleDir.mkdir()

            for file in temp_path.glob("**/*"):
                if file.is_dir():
                    continue
                if True in list(
                    map(
                        lambda locale: str(file.resolve()).startswith(
                            str((temp_path / locale).resolve())
                        ),
                        locales,
                    )
                ):
                    continue
                with open(file, "r") as f:
                    body = f.read()
                # Apply key translation
                body = re.sub(
                    r'\[\[trans \(key:"(?P<key_name>[a-zA-Z0-9-_.]*)"\)\]\]',
                    lambda m: get_key_trans_value(
                        m, localeDir, locale, self.config.DEFAULT_LANG
                    ),
                    body,
                )
                # Apply t_include
                body = re.sub(
                    r"\[\[trans include "
                    r'\(filename:"(?P<filename>[a-zA-Z0-9-_.]*)"\)\]\]',
                    lambda m: apply_i_include(locale, m.group("filename")),
                    body,
                )
                out_filepath = buildLocaleDir / file.relative_to(temp_path)
                out_filepath.parent.mkdir(exist_ok=True)
                with open(out_filepath, "w") as f:
                    f.write(body)
        shutil.rmtree(temp_path)


def get_key_trans_value(
    m: re.Match, localeDir: Path, locale: str, defaultLang: str
) -> str:
    key_name = m.group("key_name")
    localeFile = localeDir / f"{locale}.json"
    with open(localeFile, "r") as f:
        localeJson = json.load(f)
    try:
        return localeJson[key_name]
    except KeyError:
        # Try to load from defaultLang
        localeFile = localeDir / f"{defaultLang}.json"
        with open(localeFile, "r") as f:
            localeJson = json.load(f)
        try:
            defaultValue = localeJson[key_name]
            logger.warning(
                f'Translation for "{key_name}" not found for '
                f"{locale}. Using default language."
            )
            return defaultValue
        except KeyError:
            logger.warning(
                f'Translation for "{key_name}" not found. Using key name.'
            )
            return key_name
        # raise KeyError(f"Translation key \"{m.group("key_name")}\"")


def apply_i_include(locale: str, file: str):
    from sgen.get_config import sgen_config

    try:
        with open(sgen_config.SRC_DIR / locale / file) as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f'Included file "{file}" not found '
            "(Tried to load from "
            f"{sgen_config.SRC_DIR / locale / file})"
        )


def localeRedirectIndex(localesStr: str, config: LocalizationConfig) -> str:
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
        location.href = {config.DEFAULT_LANG}"""  # type:ignore
        f"""
    }}
    location.href = "./" + lang.toLowerCase() + "/";
    </script>
</body>
</html>
    """,
        ext=".html",
        HTMLRemoveBr=True,
        JSRemoveBr=True,
    )
