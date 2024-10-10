import inspect
import re
from typing import Callable

from sgen.stdlib.smini.svg_minify import svg_minify

MINIFY_EXTS = {".html", ".css", ".js", ".svg"}


def minify(
    text: str,
    ext: str,
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
                r"(?P<js_prefix><script[\s\S]*?>)"
                r"(?P<js_body>[\s\S]*?)"
                r"(?P<js_suffix></script *>)|"
                r"(?P<r_body>" + regexp + r")",
                lambda m: (
                    (replace_str(m) if callable(replace_str) else replace_str)
                    if m.group("r_body")
                    else (
                        m.group("css_prefix")
                        + re.sub(
                            r"^(?: |\n|\r\n)*([\s\S]*)(?: |\n|\r\n)*$",
                            r"\1",
                            minify(m.group("css_body"), ".css"),
                        )
                        + m.group("css_suffix")
                        if m.group("css_body")
                        else (
                            re.sub(r"( |\n|\r\n)+", " ", m.group("js_prefix"))
                            # + re.sub(
                            #     r"^(?: |\n|\r\n)*([\s\S]*)(?: |\n|\r\n)*$",
                            #     r"\1",
                            + minify(m.group("js_body"), ".js")
                            # )
                            + m.group("js_suffix")
                        )
                    )
                ),
                from_,
            )

        res = repl_html(r" +", " ", res)
        res = repl_html(r"<!--[\s\S]*?-->", "", res)
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
        # TODO: JS @license support
        # TODO: Except string
        # TODO: Not working:
        # if(true)
        #    console.log("true")
        # else
        #    console.log("false")

        def repl_js(
            regexp: str,
            replace_str: str | Callable[[re.Match], str],
            from_: str,
        ) -> str:
            return re.sub(
                (
                    r'(?P<string>["\'].*?["\']|`[\s\S]*?`)|'
                    r"(?P<r_body>" + regexp + r")"
                ),
                lambda m: (
                    (replace_str(m) if callable(replace_str) else replace_str)
                    if m.group("r_body")
                    else m.group("string")
                ),
                from_,
            )

        # Delete comments
        # res = "\n".join([s.split("//")[0] for s in re.split("\n|\r\n", res)])
        res = repl_js(r"//.*?($|;)", "", res)
        res = repl_js(r"/\*.*?\*/", "", res)
        # First, update all line breaks to ;
        res = repl_js(r"\r\n|\n", ";", res)
        # Delete whitespace
        res = repl_js(
            r"( |\n|\r\n)*(?P<symbol>"
            r"(?:\{|\}|\(|\)|=>|=|\+|\?|,|:))( |\n|\r\n)*",
            lambda m: m.group("symbol"),
            res,
        )
        # raise ValueError(res)
        res = repl_js(r";(\n|\r\n| )*", r";", res)
        # Delete ; that cause errors
        res = repl_js(
            r"(?P<symbol>\{|\(|=>|=|,|\?|:|\[|\.)(;)*",
            lambda m: m.group("symbol"),
            res,
        )
        res = repl_js(
            r"(;)*(?P<symbol>=>|=|,|\?|:|\)|\+(?!\+)|\.)",
            lambda m: m.group("symbol"),
            res,
        )
        res = repl_js(
            r"^;",
            "",
            res,
        )
        # Remove unnecessary bracket
        # res = repl_js(
        #     r"(?P<prefix>(?:if|for)(?: |\r\n|\n)*\([\s\S]*?\)"
        #     r"(?: |\n|\r\n)*?)\{(?P<body>[\s\S]*?)\}",
        #     lambda m: (
        #         m.group("prefix") + m.group("body")
        #         if m.group("body").
        #         else m.group("prefix") + "{" + m.group("body") + "}"
        #     ),
        #     res,
        # )
        # Remove unnecessary semi-colon
        res = repl_js(r";+", r";", res)
        res = repl_js(r";}", r"}", res)
        # res = repl_js(r";(\n|\r\n| )*", r";", res)
        if JSRemoveBr:
            res = repl_js(r"(\n|\r\n)", "", res)
    elif ext == ".svg":
        res = svg_minify(res)
    else:
        res = res
    return res


if __name__ == "__main__":
    print(
        minify(
            """+[] ? function(){
                console.log("Hello.");
            } :
            function (){};
            alert("hey");++[+[]][+[]]""",
            ".js",
        )
    )
