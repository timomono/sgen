import re

from sgen.components.repl import repl_css, repl_html, repl_js
from sgen.stdlib.smini.svg_minify import svg_minify

MINIFY_EXTS = {".html", ".css", ".js", ".svg"}


def minify(
    text: str,
    ext: str,
) -> str:
    res = text
    if ext == ".html":
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

        # Delete comments
        # res = "\n".join([s.split("//")[0] for s in re.split("\n|\r\n", res)])
        res = repl_js(r"//.*?$", "", res, flags=re.MULTILINE)
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
            r"(?P<symbol>\{|\(|=>|=|,|\?|:|\[|\.|&)(;)*",
            lambda m: m.group("symbol"),
            res,
        )
        res = repl_js(
            r"(;)*(?P<symbol>=>|=|,|\?|:|\)|\+(?!\+)|\.|\|\|)",
            lambda m: m.group("symbol"),
            res,
        )
        res = repl_js(
            r"^;*",
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
        res = repl_js(r";$", r"", res)
        # res = repl_js(r";(\n|\r\n| )*", r";", res)
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
