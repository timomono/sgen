from pathlib import Path
import shutil
from typing import Iterable
from sgen.components.override_decorator import OverrideStrict, override
from urllib.parse import urljoin, urlparse
from sgen.base_middleware import BaseMiddleware
from sgen.components.minify import minify
import re
from logging import getLogger

from sgen.stdlib.stra.file_parser import Stra

logger = getLogger(__name__)


class StraConfig(OverrideStrict):
    """Stra localization configuration."""

    @property
    def locale_dir(self) -> Path:
        from sgen.get_config import sgen_config

        return sgen_config.BASE_DIR / "stra"

    @property
    def t_include_dir(self) -> Path:
        from sgen.get_config import sgen_config

        return sgen_config.SRC_DIR / "locale"

    @override
    def __init__(
        self,
        default_lang: str = "en",
        localize_file: list[str] = [".html"],
        files_to_copy_to_root: Iterable[Path] = {
            Path("404.html"),
        },
    ) -> None:
        self.default_lang = default_lang
        self.localize_file = localize_file
        self.files_to_copy_to_root = files_to_copy_to_root


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
    def do(self, build_path: Path):
        temp_path = build_path / "stra_temp"
        temp_path.mkdir()

        # Move to the sub directory
        # shutil.move(buildPath, temp_path)
        for file in list(build_path.glob("**/*")):
            if file.is_dir():
                continue
            if file.name == "stra_temp":
                continue
            if file.suffix not in self.config.localize_file:
                continue
            copy_to = temp_path / file.relative_to(build_path)
            copy_to.parent.mkdir(exist_ok=True, parents=True)
            file.rename(copy_to)

        locale_dir: Path = self.config.locale_dir
        if not locale_dir.exists():
            raise FileNotFoundError(
                "LOCALE_DIR specified in config.py does not exist"
            )

        localeFiles = locale_dir.glob("*.stra")
        locales = list(
            map(lambda f: ".".join(f.name.split(".")[:-1]), localeFiles)
        )
        localesStr = (
            "[" + ",".join(map(lambda s: f'"{s.upper()}"', locales)) + "]"
        )
        with open(build_path / "index.html", "w") as f:
            f.write(localeRedirectIndex(localesStr, self.config))

        if locales == []:
            raise NoLangFoundException(self.config)

        for locale in locales:
            buildLocale_dir = build_path / locale
            if not buildLocale_dir.exists():
                buildLocale_dir.mkdir()

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
                    rb'\[\[trans \(key:"(?P<key_name>[^"]*)"\)\]\]',
                    lambda m: get_key_trans_value(
                        m, locale_dir, locale, self.config.default_lang
                    ),
                    body,
                )
                # Apply t_include
                body = re.sub(
                    rb"\[\[trans include "
                    rb'\(filename:"(?P<filename>[^"]*)"\)\]\]',
                    lambda m: apply_t_include(
                        self.config, locale, m.group("filename").decode()
                    ),
                    body,
                )
                # Change link
                body = re.sub(
                    rb"(?P<tag>(?P<prefix>< *[a-zA-Z]+ +[^>]*(?:src|href)=)"
                    rb"[\"\']?(?P<result>[^>\"' ]*)[\"\']?"
                    rb"(?P<suffix> *[^>]*>))",
                    # m.groups: (b'<a href=', b'href', b'#', b'>')
                    lambda m: change_to_localized_link(
                        m, locale, file, temp_path, self.config
                    ),
                    body,
                )
                out_filepath = buildLocale_dir / file.relative_to(temp_path)
                out_filepath.parent.mkdir(exist_ok=True, parents=True)
                with open(out_filepath, "wb") as ff:
                    ff.write(body)
        shutil.rmtree(temp_path)
        for directory in build_path.glob("**/*"):
            # Is empty directory?
            if directory.is_dir() and not any(
                d for d in directory.glob("**/*") if d.is_file()
            ):
                shutil.rmtree(directory)
        for rel_file in self.config.files_to_copy_to_root:
            file = build_path / self.config.default_lang / rel_file
            copy_to = build_path / rel_file
            if not file.exists():
                continue
            shutil.copyfile(file, copy_to)


def change_to_localized_link(
    match: re.Match[bytes],
    locale: str,
    file: Path,
    base_dir: Path,
    config: StraConfig,
) -> bytes:
    prefix: str = match.group("prefix").decode("utf-8")
    suffix: str = match.group("suffix").decode("utf-8")
    result: str = match.group("result").decode("utf-8")
    tag: bytes = match.group("tag")
    filename = result.split("/")[-1]
    ext: str | None = (
        "." + filename.split(".")[-1] if "." in filename else None
    )

    # Ignore other site and non-localized files
    if (
        (urlparse(result).netloc != "")
        or (ext not in config.localize_file and ext is not None)
        or (result.startswith("#"))
        or result.startswith("data:")
    ):
        return tag

    relative_path = file.relative_to(base_dir)
    absolute_url = urljoin(str(relative_path), urlparse(result).path)
    result = f"/{locale}" + absolute_url
    return rf'{prefix}"{result}"{suffix}'.encode("utf-8")
    # return rf'\1"{result}"\4'.encode("utf-8")


def get_key_trans_value(
    m: re.Match, locale_dir: Path, locale: str, default_lang: str
) -> bytes:
    key_name: bytes = m.group("key_name")
    locale_file = locale_dir / f"{locale}.stra"
    locale_data = Stra.from_load_file(locale_file)
    try:
        res = locale_data[key_name.decode("utf-8")].encode("utf-8")
        if res == b"":
            return load_from_default_lang(
                key_name, locale_dir, locale, default_lang
            )
        return res
    except KeyError:
        with open(locale_file, "ab") as f:
            f.write(
                b"\n> "
                + b"\n".join((line.lstrip() for line in key_name.splitlines()))
                .replace(b"\r\n", b"\r\n> ")
                .replace(b"\n", b"\n> ")
                + b"\npass"
            )
        return load_from_default_lang(
            key_name, locale_dir, locale, default_lang
        )
        # raise KeyError(f"Translation key \"{m.group("key_name")}\"")


def load_from_default_lang(
    key_name: bytes, locale_dir: Path, locale: str, default_lang: str
):
    # Try to load from default_lang
    locale_file = locale_dir / f"{default_lang}.stra"
    locale_data = Stra.from_load_file(locale_file)
    try:
        defaultValue: str = locale_data[key_name.decode("utf-8")]
        logger.debug(
            f'Translation for "{key_name.decode("utf-8")}" not found for '
            f"{locale}. Using default language."
        )
        if defaultValue == "":
            raise KeyError()
        return defaultValue.encode("utf-8")
    except KeyError:
        logger.debug(
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
        location.href = "{config.default_lang}"
    }}
    location.href = "./" + lang.toLowerCase() + "/";
    </script>
</body>
</html>
    """,
        ext=".html",
    )
