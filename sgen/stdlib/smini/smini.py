import re


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
        res = "".join([s.strip() for s in res])
        res = re.sub(r"/\*.*?\*/", "", res)
        res = re.sub(r": +?", ":", res)
        res = re.sub(r" +?{ +?", "{", res)
        res = re.sub(r" +?} +?", "}", res)
        res = re.sub(r"(\n|\r\n)", "", res)
    elif ext == ".js":
        res = "\n".join([s.split("//")[0] for s in re.split("\n|\r\n", res)])
        res = re.sub(r"/\*.*?\*/", "", res)
        if JSRemoveBr:
            res = re.sub(r"(\n|\r\n)", "", res)
    else:
        res = res
    return res
