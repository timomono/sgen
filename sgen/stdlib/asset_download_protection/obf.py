from base64 import b64encode
from random import randint

js_symbol = {
    "eval": "[[[+[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[][[[[]==[]]+[]][+[]][+[]]+[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[]][+[]][++[++[+[]][+[]]][+[]]+[++[++[++[+[]][+[]]][+[]]][+[]]]]+[[[]==[]]+[]][+[]][++[+[]][+[]]]+[[[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]][+[]]",  # noqa:E501
    "space": "[[][[[][[]]+[]][+[]][++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]]+[[][[]]+[]][+[]][++[++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]][+[]]]+[[][[]]+[]][+[]][++[+[]][+[]]]+[[][[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[[][[]]+[]][+[]]][+[]][++[++[++[++[++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]]",  # noqa:E501
    "includes": "[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][[[[]==[]]+[]][+[]][+[]]+[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[+[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[+[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]"  # noqa:E501
}


def obfScript(
    text: str,
    iter: int = 1,
    base64: bool = True,
    uint8: bool = True,
    debugger: bool = True,
    format: bool = True,
) -> str:
    res = text
    before = ""
    if debugger:
        before += "setInterval(()=>{debugger},0x64);"
    if format:
        before += (
            f'const c=()=>c.toString()[{js_symbol["includes"]}]({js_symbol["space"]})?(()=>{{while(++[+[]][+[]])alert("ERR")}})():"";c();'  # noqa:E501
        )
    for i in range(iter):
        if uint8:
            res = toUint8(res)
        if base64:
            res = toBase64(res)
    return "(()=>{" + before + "return " + res + "})()"


def toBase64(text: str) -> str:
    return (
        f"window[{js_symbol["eval"]}]"
        "(" + "new TextDecoder().decode(new Uint8Array("
        'Array.prototype.map.call(atob("'
        + b64encode(text.encode()).decode()
        + '"),c=>c.charCodeAt())))'
        + ")"
    )


def toUint8(text: str) -> str:
    script = (f"window[{js_symbol["eval"]}]("
              "(new TextDecoder()).decode(new Uint8Array([")
    for char in text.encode():
        obf_str = baseNumberToStr(char)
        script += obf_str + ","
    script += "]))" + ")"
    return script


def baseNumberToStr(integer: int) -> str:
    rand = randint(0, 3)
    obf_str = ""
    if rand == 0:
        obf_str = hex(integer)
    elif rand == 1:
        obf_str = bin(integer)
    elif rand == 2:
        obf_str = oct(integer)
    elif rand == 3:
        obf_str = str(integer)
    return obf_str


if __name__ == "__main__":
    print(
        obfScript(
            'alert("hello world")',
            base64=False,
        )
    )
