import re

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
        res = re.sub(r"(\n|\r\n)", "", res)
        res = re.sub(r" +", " ", res)
        res = re.sub(r"/\*.*?\*/", "", res)
        res = re.sub(r" *([:;]) *", r"\1", res)
        res = re.sub(r" *{ *", "{", res)
        res = re.sub(r" *} *", "}", res)
        res = re.sub(r";}", "}", res)
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
