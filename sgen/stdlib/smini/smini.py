import re
from typing import Callable

from sgen.stdlib.smini.svg_minify import svg_minify


def minify(
    text: str,
    ext: str,
    HTMLRemoveBr: bool,
    JSRemoveBr: bool,
) -> str:
    res = text
    if ext == ".html":
        res = re.sub(r" +", " ", res)
        res = re.sub(r"<!--[\s\S]*?-->", "", res)
        if HTMLRemoveBr:
            res = re.sub(r"(\n|\r\n)", "", res)
        res = re.sub(r">( |\n|\r\n)+<", "><", res)
        res = re.sub(r"( |\n|\r\n)*(<|>)( |\n|\r\n)*", r"\2", res)
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
            r" *(?P<symbol>[:;,!\*><]) *", lambda m: m.group("symbol"), res
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
