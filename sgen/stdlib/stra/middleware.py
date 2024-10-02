from pathlib import Path
import shutil
from typing import override
from urllib.parse import urljoin, urlparse
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.smini.smini import minify
import re
from logging import getLogger

from sgen.stdlib.stra.file_parser import Stra

logger = getLogger(__name__)


class StraConfig:
    """Stra localization configuration."""

    @property
    def locale_dir(self) -> Path:
        from sgen.get_config import sgen_config

        return sgen_config.BASE_DIR / "stra"

    @property
    def t_include_dir(self) -> Path:
        from sgen.get_config import sgen_config

        return sgen_config.SRC_DIR / "locale"

    def __init__(
        self, default_lang: str = "en", localize_file: list[str] = [".html"]
    ) -> None:
        self.default_lang = default_lang
        self.localize_file = localize_file


class NoLangFoundException(Exception):
    def __init__(self, config: StraConfig) -> None:
        self.message = (
            "No language for localization found. "
            "Currently locale_dir is set to"
            f' "{config.locale_dir}".'  # type:ignore
        )
        super().__init__(self.message)


class StraMiddleware(BaseMiddleware):
    @override
    def __init__(self, config: StraConfig) -> None:
        self.config = config
        super().__init__()

    @override
    def do(self, buildPath: Path):
        temp_path = buildPath / "stra_temp"
        temp_path.mkdir()
        # shutil.move(buildPath, temp_path)
        for file in list(buildPath.glob("**/*")):
            if file.is_dir():
                continue
            if file.name == "stra_temp":
                continue
            if file.suffix not in self.config.localize_file:
                continue
            copy_to = temp_path / file.relative_to(buildPath)
            copy_to.parent.mkdir(exist_ok=True, parents=True)
            file.rename(copy_to)
        for path in buildPath.iterdir():
            if (
                path.name != "stra_temp"
                and file.suffix not in self.config.localize_file
                and file.is_dir()
            ):
                shutil.rmtree(path)
        localeDir: Path = self.config.locale_dir  # type: ignore
        if not localeDir.exists():
            raise FileNotFoundError(
                "LOCALE_DIR specified in config.py does not exist"
            )
        localeFiles = localeDir.glob("*.stra")
        locales = list(
            map(lambda f: ".".join(f.name.split(".")[:-1]), localeFiles)
        )
        localesStr = (
            "[" + ",".join(map(lambda s: f'"{s.upper()}"', locales)) + "]"
        )
        with open(buildPath / "index.html", "w") as f:
            f.write(localeRedirectIndex(localesStr, self.config))

        if locales == []:
            raise NoLangFoundException(self.config)

        for locale in locales:
            buildLocaleDir = buildPath / locale
            if not buildLocaleDir.exists():
                buildLocaleDir.mkdir()

            for file in temp_path.glob("**/*"):
                if file.is_dir():
                    continue
                # if True in list(
                #     map(
                #         lambda locale: str(file.resolve()).startswith(
                #             str((temp_path / locale).resolve())
                #         ),
                #         locales,
                #     )
                # ):
                with open(file, "rb") as ff:
                    body = ff.read()
                # Apply key translation
                body = re.sub(
                    rb'\[\[trans \(key:"(?P<key_name>[a-zA-Z0-9-_. ]*)"\)\]\]',
                    lambda m: get_key_trans_value(
                        m, localeDir, locale, self.config.default_lang
                    ),
                    body,
                )
                # Apply t_include
                body = re.sub(
                    rb"\[\[trans include "
                    rb'\(filename:"(?P<filename>[a-zA-Z0-9-_./]*)"\)\]\]',
                    lambda m: apply_t_include(
                        self.config,
                        locale,
                        m.group("filename").decode("utf-8"),
                    ),
                    body,
                )
                # Change link
                body = re.sub(
                    rb"(< *[a-zA-Z]+ +[^>]*(src|href)=)"
                    rb"[\"\']?([^>\"' ]*)[\"\']?"
                    rb"( *[^>]*>)",
                    # m.groups: (b'<a href=', b'href', b'#', b'>')
                    lambda m: change_to_localized_link(
                        m, locale, file, temp_path, self.config
                    ),
                    body,
                )
                out_filepath = buildLocaleDir / file.relative_to(temp_path)
                out_filepath.parent.mkdir(exist_ok=True, parents=True)
                with open(out_filepath, "wb") as ff:
                    ff.write(body)
        shutil.rmtree(temp_path)


def change_to_localized_link(
    match: re.Match,
    locale: str,
    file: Path,
    base_dir: Path,
    config: StraConfig,
):
    prefix: str = match.group(1).decode("utf-8")
    suffix: str = match.group(4).decode("utf-8")
    result: str = match.group(3).decode("utf-8")
    filename = result.split("/")[-1]
    ext: str | None = (
        "." + filename.split(".")[-1] if "." in filename else None
    )

    # Ignore other site and non-localized files
    if (
        (urlparse(result).netloc != "")
        or (ext not in config.localize_file and ext is not None)
        or (result.startswith("#"))
    ):
        return rf'{prefix}"{result}"{suffix}'.encode("utf-8")

    relative_path = file.relative_to(base_dir)
    absolute_url = urljoin(str(relative_path), urlparse(result).path)
    result = f"/{locale}" + absolute_url
    return rf'{prefix}"{result}"{suffix}'.encode("utf-8")
    # return rf'\1"{result}"\4'.encode("utf-8")


def get_key_trans_value(
    m: re.Match, localeDir: Path, locale: str, defaultLang: str
) -> bytes:
    key_name: bytes = m.group("key_name")
    locale_file = localeDir / f"{locale}.stra"
    locale_data = Stra.from_load_file(locale_file)
    try:
        res = locale_data[key_name.decode("utf-8")].encode("utf-8")
        if res == b"":
            return load_from_default_lang(
                key_name, localeDir, locale, defaultLang
            )
        return res
    except KeyError:
        with open(locale_file, "ab") as f:
            f.write(b"\n> " + key_name + b"\npass")
        return load_from_default_lang(key_name, localeDir, locale, defaultLang)
        # raise KeyError(f"Translation key \"{m.group("key_name")}\"")


def load_from_default_lang(
    key_name: bytes, localeDir: Path, locale: str, defaultLang: str
):
    # Try to load from defaultLang
    locale_file = localeDir / f"{defaultLang}.stra"
    locale_data = Stra.from_load_file(locale_file)
    try:
        defaultValue: str = locale_data[key_name.decode("utf-8")]
        logger.warning(
            f'Translation for "{key_name.decode("utf-8")}" not found for '
            f"{locale}. Using default language."
        )
        if defaultValue == "":
            raise KeyError()
        return defaultValue.encode("utf-8")
    except KeyError:
        logger.warning(
            f'Translation for "{key_name.decode("utf-8")}" not found. '
            "Using key name."
        )
        return key_name


def apply_t_include(config: StraConfig, locale: str, file: str):
    filepath = config.t_include_dir / locale / file
    if not filepath.exists():
        raise FileNotFoundError(
            f'Included file "{file}" not found '
            "(Tried to load from "
            f"{filepath})"
        )
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f'Included file "{file}" not found '
            "(Tried to load from "
            f"{filepath})"
        )


def localeRedirectIndex(localesStr: str, config: StraConfig) -> str:
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
        location.href = {config.default_lang}"""  # type:ignore
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
