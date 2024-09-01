import re

from base_config import config


def minify(
    text: str,
    ext: str,
    HTMLRemoveBr: bool = config().MINIFY_CONFIG.HTMLRemoveBr,  # type:ignore
    JSRemoveBr: bool = config().MINIFY_CONFIG.JSRemoveBr,  # type:ignore
) -> str:
    if config().MINIFY_CONFIG is None:
        return text
    res = text
    if ext == "html":
        res = re.sub(r" +", " ", res)
        res = re.sub(r"<!--.*?-->", "", res)
        if HTMLRemoveBr:
            res = re.sub(r"(\n|\r\n)", "", res)
        res = re.sub(r">( |\n|\r\n)+<", "><", res)
    elif ext == "css":
        res = "".join([s.strip() for s in res])
        res = re.sub(r"/\*.*?\*/", "", res)
        res = re.sub(r": +?", ":", res)
        res = re.sub(r" +?{ +?", "{", res)
        res = re.sub(r" +?} +?", "}", res)
        res = re.sub(r"(\n|\r\n)", "", res)
    elif ext == "js":
        res = "\n".join([s.split("//")[0] for s in re.split("\n|\r\n", res)])
        res = re.sub(r"/\*.*?\*/", "", res)
        if JSRemoveBr:
            res = re.sub(r"(\n|\r\n)", "", res)
    else:
        res = res
    return res
