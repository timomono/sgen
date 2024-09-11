import json
from pathlib import Path
from typing import override
from base_middleware import BaseMiddleware
from get_config import sgen_config
from stdlib.smini.smini import minify
import re


class LocalizationConfig:
    """Localization configuration."""

    @property
    def LOCALE_DIR(self) -> Path:
        return sgen_config.BASE_DIR / "locale"

    @property
    def DEFAULT_LANG(self) -> str:
        return "en"


class NoLangFoundException(Exception):
    def __init__(self, message="hwy") -> None:
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
            f.write(localeRedirectIndex(localesStr))

        if locales == []:
            raise NoLangFoundException()

        for locale in locales:
            localeFile = localeDir / f"{locale}.json"
            with open(localeFile, "r") as f:
                localeJson = json.load(f)
            buildLocaleDir = buildPath / locale
            if not buildLocaleDir.exists():
                buildLocaleDir.mkdir()

            for file in buildLocaleDir.glob("**/*"):
                if file.is_dir():
                    continue
                with open(file, "r") as f:
                    body = f.read()
                key_matches = re.finditer(r'[[trans (key:"<key_name>"]]', body)
                for key_match in key_matches:
                    print(key_match.groupdict())


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
