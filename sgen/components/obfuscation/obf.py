import re
import random
import string
from typing import Iterable, NotRequired, TypedDict, Unpack

from sgen.components.repl import repl_js


try:
    from sgen.components.minify import minify
except ImportError:
    from ..minify import minify

similar_texts = (("l", "I"), ("1", "l"), ("1", "I"), ("i", "j"), ("o", "c"))


# Contains incorrect symbols
# SYMBOL_MAP = {
#     "0": "+[]",
#     "1": "+!![]",
#     "2": "!![]+!![]",
#     "3": "!![]+!![]+!![]",
#     "4": "!![]+!![]+!![]+!![]",
#     "5": "!![]+!![]+!![]+!![]+!![]",
#     "6": "!![]+!![]+!![]+!![]+!![]+!![]",
#     "7": "!![]+!![]+!![]+!![]+!![]+!![]+!![]",
#     "8": "!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]",
#     "9": "!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]",
#     "a": "(![]+[])[1]",
#     "b": "([]+{})[2]",
#     "c": "([]+{})[5]",
#     "d": "(!![]+[])[2]",
#     "e": "(!![]+[])[3]",
#     "f": "(![]+[])[0]",
#     "g": "(+(!![]+!![]+!![])+[])[0]",
#     "h": "(+(!![]+!![]+!![])+[])[1]",
#     "i": "((+!![]/+[])+[])[3]",
#     "j": "([]+{})[3]",
#     "k": "(+{}+[])[2]",
#     "l": "(+{}+[])[3]",
#     "m": "(+{}+[])[4]",
#     "n": "((+!![]/+[])+[])[4]",
#     "o": "([][[]]+[])[1]",
#     "p": "([]+{})[1]",
#     "q": "(+{}+[])[1]",
#     "r": "(!![]+[])[1]",
#     "s": "(!![]+[])[4]",
#     "t": "(!![]+[])[0]",
#     "u": "(!![]+[])[2]",
#     "v": "([]+{})[6]",
#     "w": "(+{}+[])[0]",
#     "x": "(+{}+[])[6]",
#     "y": "(+{}+[])[7]",
#     "z": "(+{}+[])[8]",
# }
# for k, v in SYMBOL_MAP.items():
#     SYMBOL_MAP[k] = re.sub(r"([0-9])", lambda m: SYMBOL_MAP[m.group(1)], v)


def _obfuscate_variable_name(similar_to: Iterable[str] | None = None) -> str:
    if similar_to:
        for name in similar_to:
            for i in range(len(name)):
                namelist = list(name)
                if namelist[i] in (
                    element
                    for inner_tuple in similar_texts
                    for element in inner_tuple
                ):
                    try:
                        namelist[i] = dict(similar_texts)[namelist[i]]
                    except KeyError:
                        namelist[i] = dict(
                            {v: k for k, v in dict(similar_texts).items()}
                        )[namelist[i]]
                # Update lower/upper
                if i == 0:
                    continue
                namelist[i] = (
                    name[i].lower() if name[i].isupper() else name[i].upper()
                )
                name = "".join(namelist)
                if name not in similar_to:
                    return name
    while similar_to is not None and (
        (text := "".join(random.choices(string.ascii_letters, k=8)))
        in similar_to
    ):
        pass
    return (
        "".join(random.choices(string.ascii_letters, k=8))
        if similar_to is None
        else text
    )


def _split_string(text, max_len: int | None = None) -> list[str]:
    max_len = max_len or random.randint(1, 10)
    return [text[i : i + max_len] for i in range(0, len(text), max_len)]


def _shuffle_functions(code: str) -> str:
    # print(code)
    # return code
    functions: list[str] = re.findall(
        r"(function\s+\w+\s*\([^)]*\)\s*{(?:[^{}]*|{(?:[^{}]*|{[^{}]*})*})*})|"
        # Arrow function
        r"(?:(?:const|let|var)\s+)?"
        r"[^\s=]+\s*=\s*\([^)]*\)\s*=>\s*(?:{.*?}|[^;]+);?",
        code,
    )
    # return str(functions)

    # return str(functions) + "\n" + code
    for function in functions:
        code = code.replace(function, "")

    random.shuffle(functions)
    code = "\n".join(functions) + code
    return code


RE_VARIABLE_NAME = re.compile(
    r"\b(?:var|let|const)\s+(\w+)|\bfunction\s+(\w+)"
)

RE_MULTIPLE_BREAK = re.compile(r"\n+")

RE_STRING_LITERAL = re.compile(r'(["\'])(.*?)(["\'])')

RE_DICT_KEY = re.compile(r'["\'](\w+)"\s*:')


class ObfuscateOptions(TypedDict):
    is_minify: NotRequired[bool]
    seed: NotRequired[int | float | str | bytes | bytearray]


class ObfuscateContext:
    def __init__(
        self,
        variable_map: dict[str, str] = None,
        string_map: dict[str, str] = None,
    ) -> None:
        self.variable_map = variable_map or {}
        self.string_map = string_map or {}


def obfuscate_js(
    code,
    context: ObfuscateContext | None = None,
    **options: Unpack[ObfuscateOptions],
) -> tuple[str, dict[str, str]]:
    variable_map = context.variable_map if context is not None else {}
    string_map = context.string_map if context is not None else {}
    # print(context.variable_map, context.string_map)
    already_declared_vars = list(variable_map.values()) + list(
        string_map.keys()
    )
    # variable_map = context.variable_map or {}

    # Optional args: https://github.com/python/mypy/issues/6131
    options["is_minify"] = options.get("is_minify", True)

    random.seed(options.get("seed"))
    # Update . to []
    # code = repl_js(r"(\w+)\.(\w+)", r'\1["\2"]', code)

    # Update {"key":"value"} to {["key"]:"value"}
    code = RE_DICT_KEY.sub(r'["\1"]:', code)

    # Update string to function
    for i in range(random.randint(1, 3)):
        string_literals = RE_STRING_LITERAL.findall(code)
        # string_map: dict[str, str] = {}
        for quote, value, quote_end in string_literals:
            parts = _split_string(value)
            func_calls = []
            for part in parts:
                if part not in string_map.values():
                    func_name = _obfuscate_variable_name(
                        list(variable_map.values()) + list(string_map.keys())
                    )
                    # print(
                    #     list(variable_map.values()) + list(string_map.keys()),
                    #     func_name,
                    # )
                    string_map[func_name] = part
                else:
                    func_name = list(string_map.keys())[
                        list(string_map.values()).index(part)
                    ]
                func_calls.append(f"{func_name}()")
            code = code.replace(
                f"{quote}{value}{quote_end}", "+".join(func_calls)
            )

        for func_name, return_value in string_map.items():
            if func_name in already_declared_vars:
                continue
            if random.randint(0, 3) == 0:
                code = (
                    f'function {func_name}(){{return "{return_value}"}}\n'
                    + code
                )
            else:
                code = (
                    f'{random.choice(("const ", "let ", "", "", ""))}'
                    f'{func_name}=()=>"{return_value}";\n' + code
                )

    # Update variable name to random name
    names: list[str] = RE_VARIABLE_NAME.findall(code)
    # variable_map: dict[str, str] = {}
    for name in names:
        try:
            variable_map[name[0] or name[1]]
        except KeyError:
            variable_map[name[0] or name[1]] = _obfuscate_variable_name(
                list(variable_map.values()) + list(string_map.keys())
            )
            # print(list(variable_map.values()) + list(string_map.keys()))

    # def replace(match):
    #     code = match.group(0)
    #     if match.group(1):
    #         return code
    #     for original, obfuscated in variable_map.items():
    #         # if len(original) != 8:
    #         #     print(original)
    #         code = re.sub(rf"\b{original}\b", obfuscated, code)
    #     return code

    # code = re.sub(r'(["\'].*?["\'])|([^"\']+)', replace, code)

    for original, obfuscated in variable_map.items():
        code = repl_js(rf"\b{original}\b", obfuscated, code)

    # Shuffle functions
    code = _shuffle_functions(code)

    # Minify
    if options["is_minify"]:
        code = minify(code, ".js")
    else:
        code = RE_MULTIPLE_BREAK.sub(r"\n", code)

    # print(context.variable_map, context.string_map, string_map)

    return code  # type:ignore


if __name__ == "__main__":
    code = """
    function sayHello() {
        var message = "Hello, World!";
        alert(message)
        console.log("Console hello world message");
    }
    sayHello();
    """

    obfuscated_code = obfuscate_js(code)
    print(obfuscated_code)
