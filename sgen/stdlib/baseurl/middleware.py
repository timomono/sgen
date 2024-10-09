from pathlib import Path
import re
from typing import Callable
from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override
from urllib.parse import urljoin


class BaseUrlMiddleware(BaseMiddleware):
    """Automatically updates the URL in the html.
    This is useful when delivering only images from another origin.

    Attributes:
        url_prefix (tuple[str, str] | Callable[[str, str], tuple[str, str]]):
            The base URL.
            The Callable is passed the tag name and path as arguments.
    """

    def __init__(
        self,
        url_prefix: tuple[str, str] | Callable[[str, str], tuple[str, str]],
        # url_suffix: str | Callable[[str, str], str],
    ) -> None:
        self.url_prefix = url_prefix
        # self.url_suffix = url_suffix

    @override
    def do(self, build_path: Path) -> None:
        for file in build_path.glob("**/*.html"):
            with open(file, "rb") as f:
                # Read all
                body = f.read()
            body = re.sub(
                rb"(?P<prefix>"
                rb"< *(?P<tagname>[a-zA-Z]+) +[^>]*(?:src|href)=)"
                rb"[\"\']?(?P<result>[^>\"' ]*)[\"\']?"
                rb"(?P<suffix> *[^>]*>)",
                # m.groups: (b'<a href=', b'href', b'#', b'>')
                lambda m: self._repl(m, file.relative_to(build_path)),
                body,
            )
            with open(file, "wb") as f:
                f.write(body)

    def _repl(self, m: re.Match, relative_filepath: Path):
        prefix: bytes = m.group("prefix")
        suffix: bytes = m.group("suffix")
        tagname: bytes = m.group("tagname")
        result: bytes = m.group("result")
        result = urljoin(("/" + str(relative_filepath)).encode(), result)

        baseurl = (
            self.url_prefix(tagname.decode(), result.decode())
            if callable(self.url_prefix)
            else self.url_prefix
        )
        url_prefix = baseurl[0].encode()
        url_suffix = baseurl[1].encode()

        if url_prefix.endswith(b"/"):
            url_prefix = url_prefix[:-1]

        url = url_prefix + result + url_suffix

        return prefix + b'"' + url + b'"' + suffix


BaseUrlMiddleware(url_prefix=("", ""))
