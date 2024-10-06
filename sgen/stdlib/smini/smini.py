import re
from typing import Callable

from sgen.stdlib.smini.svg_minify import svg_minify

MINIFY_EXTS = {".html", ".css", ".js", ".svg"}


def minify(
    text: str,
    ext: str,
    HTMLRemoveBr: bool = False,
    JSRemoveBr: bool = False,
) -> str:
    res = text
    if ext == ".html":

        def repl_html(
            regexp: str,
            replace_str: str | Callable[[re.Match], str],
            from_: str,
        ) -> str:
            return re.sub(
                r"(?P<css_prefix><style[\s\S]*?>)"
                r"(?P<css_body>[\s\S]*?)"
                r"(?P<css_suffix></style>)|"
                r"(?P<r_body>" + regexp + r")",
                lambda m: (
                    (replace_str(m) if callable(replace_str) else replace_str)
                    if m.group("r_body")
                    else m.group("css_prefix")
                    + re.sub(
                        r"^(?: |\n|\r\n)*([\s\S]*)(?: |\n|\r\n)*$",
                        r"\1",
                        minify(m.group("css_body"), ".css"),
                    )
                    + m.group("css_suffix")
                ),
                from_,
            )

        res = repl_html(r" +", " ", res)
        res = repl_html(r"<!--[\s\S]*?-->", "", res)
        if HTMLRemoveBr:
            res = repl_html(r"(\n|\r\n)", "", res)
        res = repl_html(
            r"(?: |\n|\r\n)*(?P<bracket>[><])(?: |\n|\r\n)*",
            lambda m: m.group("bracket"),
            res,
        )
    elif ext == ".css":
        # res = re.sub(r"(\n|\r\n)", "", res)
        # Delete break line except for in important comment
        def repl_css(
            regexp: str,
            replace_str: str | Callable[[re.Match], str],
            from_: str,
        ) -> str:
            return re.sub(
                r"(?P<comment>/\*\![\s\S]*?\*/)|(?P<r_body>" + regexp + r")",
                lambda m: (
                    (replace_str(m) if callable(replace_str) else replace_str)
                    if m.group("r_body")
                    else m.group("comment")
                ),
                from_,
            )

        res = repl_css(r"(\n|\r\n)", "", res)
        # res = re.sub(
        #     r"(/\*[\s\S]*?\*/)|(\n)",
        #     lambda m: "" if m.group(2) is "" else m.group(1),
        #     res,
        # )
        res = repl_css(r" +", " ", res)
        res = repl_css(r"/\*.*?\*/", "", res)
        res = repl_css(
            r" *(?P<symbol>[:;,!><]) *", lambda m: m.group("symbol"), res
        )
        res = repl_css(r" *{ *", "{", res)
        res = repl_css(r" *} *", "}", res)
        res = repl_css(r";}", "}", res)
    elif ext == ".js":
        res = "\n".join([s.split("//")[0] for s in re.split("\n|\r\n", res)])
        res = re.sub(r"/\*.*?\*/", "", res)
        if JSRemoveBr:
            res = re.sub(r"(\n|\r\n)", "", res)
    elif ext == ".svg":
        res = svg_minify(res)
    else:
        res = res
    return res
