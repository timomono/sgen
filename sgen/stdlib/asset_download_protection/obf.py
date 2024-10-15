from base64 import b64encode
from random import randint

from sgen.components.random_str import random_expression_to_str

js_symbol = {
    "eval": r'"\x65"[+[]][[+[]][+[]]]+["\x6e\x63\x6f\x64\x65"[+[]]&&"\x76"+[[[]==[]]+[]][+[]][++[+[]][+[]]]+"\x6c"][+[]]||"\x26\x52"',  # noqa:E501
    "space": r"[[][[[][[]]+[]][+[]][++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]]+[[][[]]+[]][+[]][++[++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]][+[]]]+[[][[]]+[]][+[]][++[+[]][+[]]]+[[][[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[[][[]]+[]][+[]]][+[]][++[++[++[++[++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]]",  # noqa:E501
    "includes": r"[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][[[[]==[]]+[]][+[]][+[]]+[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[+[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[+[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]",  # noqa:E501
}


def randBool():
    return randint(0, 1) == 0


def obfScript(
    text: str,
    iter: int | None = None,
    base64: bool | None = None,
    uint8: bool | None = None,
    debugger: bool = True,
    format: bool = True,
) -> str:
    iter = iter or randint(1, 2)
    base64 = base64 or randBool()
    uint8 = uint8 or randBool() or not base64

    res = text
    before = ""
    if debugger:
        before += (
            "setInterval(()=>(function(){return "
            + random_expression_to_str(randint(0, 100))
            + "}['constructor'](("
            + obfScript('"d"+"ebugger"', debugger=False, iter=1)
            + "))['apply']('stateObject')),0x64);"
        )
    if format:
        before += f'const c=()=>c.toString()[{js_symbol["includes"]}]({js_symbol["space"]})?(()=>{{while(++[+[]][+[]])alert("\\x45"+"\\x52"+"\\x52")}})():"";c();'  # noqa:E501
    for i in range(iter):
        if uint8:
            res = toUint8(res)
        if base64:
            res = toBase64(res)
    return "(()=>{" + toUint8(before) + "return " + res + "})()"


def toBase64(text: str) -> str:
    js_eval = js_symbol["eval"]
    return (
        f"window[{js_eval}]"
        "(" + "new TextDecoder().decode(new Uint8Array("
        'Array.prototype.map.call(atob("'
        + b64encode(text.encode()).decode()
        + '"),c=>c.charCodeAt())))'
        + ");"
    )


def toUint8(text: str) -> str:
    js_eval = js_symbol["eval"]
    script = f"window[{js_eval}](new TextDecoder().decode(new Uint8Array(["
    for char in text.encode():
        obf_str = random_expression_to_str(char)
        script += obf_str + ","
    script += "]))" + ");"
    return script


if __name__ == "__main__":
    print(
        obfScript(
            "",
        )
    )
