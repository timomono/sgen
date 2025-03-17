from typing import Callable
import re


def repl_js(
    regexp: str,
    replace_str: str | Callable[[re.Match], str],
    from_: str,
    flags: int = 0,
) -> str:
    return re.sub(
        (
            r'(?P<string>(["\']).*?\2|`[\s\S]*?`)|'
            r"(?P<r_body>" + regexp + r")"
        ),
        lambda m: (
            (
                replace_str(m)
                if callable(replace_str)
                else re.sub(
                    r"\\([0-9])",
                    lambda num: m.group(int(num.group(1))),
                    replace_str,
                )
            )
            if m.group("r_body")
            else m.group("string")
        ),
        from_,
        flags=flags,
    )


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


def repl_html(
    regexp: str,
    replace_str: str | Callable[[re.Match], str],
    from_: str,
) -> str:
    from sgen.components.minify import minify

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
