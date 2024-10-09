from base64 import b64encode
from random import randint

js_symbol = {
    "eval": "(()=>{var _0x423e8d=_0x2ea2;function _0x2ea2(_0x9c8927,_0x19d296){var _0x544d62=_0x333a();return _0x2ea2=function(_0x1e83f5,_0x15d78c){_0x1e83f5=_0x1e83f5-0x0;var _0x333a16=_0x544d62[_0x1e83f5];return _0x333a16;},_0x2ea2(_0x9c8927,_0x19d296);}(function(_0x4d0680,_0x2f01af){var _0x539b76=_0x2ea2,_0x33f085=_0x4d0680();while(!![]){try{var _0x5d1ce7=-parseInt(_0x539b76(0x0))/0x1*(-parseInt(_0x539b76(0x1))/0x2)+parseInt(_0x539b76(0x2))/0x3*(parseInt(_0x539b76(0x3))/0x4)+-parseInt(_0x539b76(0x4))/0x5+-parseInt(_0x539b76(0x5))/0x6*(parseInt(_0x539b76(0x6))/0x7)+parseInt(_0x539b76(0x7))/0x8*(-parseInt(_0x539b76(0x8))/0x9)+parseInt(_0x539b76(0x9))/0xa*(parseInt(_0x539b76(0xa))/0xb)+-parseInt(_0x539b76(0xb))/0xc*(-parseInt(_0x539b76(0xc))/0xd);if(_0x5d1ce7===_0x2f01af)break;else _0x33f085['push'](_0x33f085['shift']());}catch(_0x53af72){_0x33f085['push'](_0x33f085['shift']());}}}(_0x333a,0xd94c2));var _0x1e83f5=(function(){var _0x4bcc54=!![];return function(_0x3c5173,_0x5e6931){var _0x198bc9=_0x4bcc54?function(){var _0x561773=_0x2ea2;if(_0x5e6931){var _0x865a81=_0x5e6931[_0x561773(0xd)](_0x3c5173,arguments);return _0x5e6931=null,_0x865a81;}}:function(){};return _0x4bcc54=![],_0x198bc9;};}()),_0x544d62=_0x1e83f5(this,function(){var _0x1eeade=_0x2ea2,_0x7212fc;try{var _0x298505=Function(_0x1eeade(0xe)+_0x1eeade(0xf)+');');_0x7212fc=_0x298505();}catch(_0x42429e){_0x7212fc=window;}var _0x2e6bf2=_0x7212fc[_0x1eeade(0x10)]=_0x7212fc[_0x1eeade(0x10)]||{},_0x5a9709=[_0x1eeade(0x11),_0x1eeade(0x12),_0x1eeade(0x13),_0x1eeade(0x14),_0x1eeade(0x15),_0x1eeade(0x16),_0x1eeade(0x17)];for(var _0x56883d=0x0;_0x56883d<_0x5a9709[_0x1eeade(0x18)];_0x56883d++){var _0x49f13a=_0x1e83f5[_0x1eeade(0x19)][_0x1eeade(0x1a)][_0x1eeade(0x1b)](_0x1e83f5),_0x7df921=_0x5a9709[_0x56883d],_0x1286bc=_0x2e6bf2[_0x7df921]||_0x49f13a;_0x49f13a[_0x1eeade(0x1c)]=_0x1e83f5[_0x1eeade(0x1b)](_0x1e83f5),_0x49f13a[_0x1eeade(0x1d)]=_0x1286bc[_0x1eeade(0x1d)][_0x1eeade(0x1b)](_0x1286bc),_0x2e6bf2[_0x7df921]=_0x49f13a;}});_0x544d62();function _0x333a(){var _0x2bcf14=['info','error','exception','table','trace','length','constructor','prototype','bind','__proto__','toString','eval','13QYcyIO','121306wzJdUw','6uTVyZq','567156eEayaa','5110200FQYUHW','6fzKUor','9617349ciIHoy','8FWrNOv','12109869PfDIiW','10695290cYrvFq','11nrLDLM','12NJgMDO','32369246RWfVRf','apply','return\x20(function()\x20','{}.constructor(\x22return\x20this\x22)(\x20)','console','log','warn'];_0x333a=function(){return _0x2bcf14;};return _0x333a();}return _0x423e8d(0x1e);})()",  # noqa:E501
    "space": "[[][[[][[]]+[]][+[]][++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]]+[[][[]]+[]][+[]][++[++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]][+[]]]+[[][[]]+[]][+[]][++[+[]][+[]]]+[[][[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[[][[]]+[]][+[]]][+[]][++[++[++[++[++[++[++[++[+[]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]][+[]]]",  # noqa:E501
    "includes": "[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][[[[]==[]]+[]][+[]][+[]]+[[+[]==[]]+[+[]]+[][+[]]+[]][+[]][++[+[]][+[]]+[+[]]]+[[+[]==[]]+[][+[]]][+[]][++[+[]][+[]]+[+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[+[]==[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[][+[]]+[]][+[]][++[++[+[]][+[]]][+[]]]+[[+[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]+[[[]==[]]+[]][+[]][++[++[++[+[]][+[]]][+[]]][+[]]]",  # noqa:E501
}


def obfScript(
    text: str,
    iter: int | None = None,
    base64: bool = True,
    uint8: bool = True,
    debugger: bool = True,
    format: bool = True,
) -> str:
    if iter is None:
        iter = randint(1, 5)
    res = text
    before = ""
    if debugger:
        before += "setInterval(()=>{debugger},0x64);"
    if format:
        before += f'const c=()=>c.toString()[{js_symbol["includes"]}]({js_symbol["space"]})?(()=>{{while(++[+[]][+[]])alert("ERR")}})():"";c();'  # noqa:E501
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
    script = (
        f"window[{js_eval}](" "(new TextDecoder()).decode(new Uint8Array(["
    )
    for char in text.encode():
        obf_str = baseNumberToStr(char)
        script += obf_str + ","
    script += "]))" + ");"
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
