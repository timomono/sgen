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


def _obfuscate_variable_name(
    similar_to: Iterable[str] | None = None,
    seed: int | float | str | bytes | bytearray = None,
) -> str:
    # assert seed is not None
    # random.seed(seed)
    # res = "".join(random.choices(string.ascii_letters, k=8))
    # print(seed, res)
    # return res
    if similar_to:
        for name in similar_to:
            for i in range(len(name)):
                namelist = list(name)
                # if namelist[i] in (
                #     element
                #     for inner_tuple in similar_texts
                #     for element in inner_tuple
                # ):
                #     try:
                #         namelist[i] = dict(similar_texts)[namelist[i]]
                #     except KeyError:
                #         namelist[i] = dict(
                #             {v: k for k, v in dict(similar_texts).items()}
                #         )[namelist[i]]
                # Update lower/upper
                if i == 0:
                    continue
                namelist[i] = (
                    name[i].lower() if name[i].isupper() else name[i].upper()
                )
                name = "".join(namelist)
                if name not in similar_to:
                    return name
    random.seed(seed)
    while similar_to is not None and (
        (text := "".join(random.choices(string.ascii_letters, k=8)))
        in similar_to
    ):
        seed += 1
        random.seed(seed)
        pass
    random.seed(seed)
    return (
        "".join(random.choices(string.ascii_letters, k=8))
        if similar_to is None
        else text
    )


def _split_string(
    text,
    max_len: int | None = None,
    except_embedded_js: bool = False,
    seed: int = None,
) -> list[str]:
    random.seed(seed)
    max_len = max_len or random.randint(1, 10)
    if len(text) == 0:
        random.seed(seed)
        return [""] * random.randint(1, max_len)
    if except_embedded_js:
        parts = RE_EMBEDDED_JS.split(text)
        embedded_js = RE_EMBEDDED_JS.findall(text)
        result = []
        for i, part in enumerate(parts):
            result.extend(
                [part[i : i + max_len] for i in range(0, len(part), max_len)]
            )
            try:
                result.append(embedded_js[i])
            except IndexError:
                pass
        return result
    else:
        return [text[i : i + max_len] for i in range(0, len(text), max_len)]


def _shuffle_functions(code: str, seed: int = None) -> str:
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

    random.seed(seed)
    random.shuffle(functions)
    code = "\n".join(functions) + code
    return code


RE_VARIABLE_NAME = re.compile(
    r"\b(?:var|let|const)\s+(\w+)|\bfunction\s+(\w+)"
)

RE_MULTIPLE_BREAK = re.compile(r"\n+")

# RE_STRING_LITERAL = re.compile(r'(["\'])(.*?\1)|`[\s\S]*?`')
RE_STRING_LITERAL = re.compile(r'(["\'`])([\s\S]*?)(\1)')

RE_DICT_KEY = re.compile(r'["\'](\w+)"\s*:')
RE_EMBEDDED_JS = re.compile(r"\${[\s\S]*?}")


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
) -> str:
    # return code
    variable_map = context.variable_map if context is not None else {}
    string_map = context.string_map if context is not None else {}
    # print(context.variable_map, context.string_map)
    # variable_map = context.variable_map or {}

    # Optional args: https://github.com/python/mypy/issues/6131
    options["is_minify"] = options.get("is_minify", True)

    # Update . to []
    # code = repl_js(r"(\w+)\.(\w+)", r'\1["\2"]', code)

    # Update {"key":"value"} to {["key"]:"value"}
    code = RE_DICT_KEY.sub(r'["\1"]:', code)

    # Update string to function
    # for i in range(random.randint(1, 3)):
    for i in range(1):
        string_literals = RE_STRING_LITERAL.findall(code)
        string_map_used: dict[str, str] = {}  # {func_name: return_value}
        string_map_used_quotes: dict[str, str] = {}  # {func_name: quote}
        args: dict[str, dict[str, str]] = (
            {}
        )  # {func_name: {embedded_js: obfuscated_name}}
        for quote, value, quote_end in string_literals:
            assert quote in ('"', "'", "`")
            parts = _split_string(
                value,
                except_embedded_js=quote == "`",
                seed=options.get("seed"),
            )
            assert parts != []
            func_calls = []
            for part in parts:
                # if random.randint(0, 7) == 0:
                if part in string_map.values() and (
                    string_map_used_quotes.get(
                        func_name := list(string_map.keys())[
                            list(string_map.values()).index(part)
                        ],
                        None,
                    )
                    == quote
                ):
                    # Use existing function
                    string_map_used[func_name] = part
                else:
                    # Make new function
                    func_name = _obfuscate_variable_name(
                        list(variable_map.values()) + list(string_map.keys()),
                        seed=options.get("seed"),
                    )
                    args[func_name] = {}
                    # Ensure that the function name is unique
                    assert func_name not in list(variable_map.values()) + list(
                        string_map.keys()
                    ), "Function name already exists"
                    string_map[func_name] = part
                    string_map_used[func_name] = part
                    string_map_used_quotes[func_name] = quote
                func_calls.append(f"{func_name}()")
            assert func_calls != []
            print("REPL", f"{quote}{value}{quote_end}", "+".join(func_calls))
            print("========CODE========\n", code, "\n====================")
            # TODO: Not Working:
            # "hello";'"hello"'
            # Working:
            # '"hello"'
            code = code.replace(
                f"{quote}{value}{quote_end}", "+".join(func_calls)
            )

        for func_name, return_value in string_map_used.items():
            random.seed(options.get("seed"))
            # return_value = return_value.replace('"', '\\"')
            quote = string_map_used_quotes[func_name]
            # quote = "'"
            assert quote in ('"', "'", "`")

            # Add embedded js to args
            if quote == "`":
                for embedded_js in RE_EMBEDDED_JS.findall(return_value):
                    # {'RNvNaVop': {'${animal["dog"]}': 'RNvnaVoP'}, ...}
                    args[func_name][embedded_js] = _obfuscate_variable_name(
                        list(variable_map.values()) + list(string_map.keys()),
                        seed=options.get("seed"),
                    )
                    padding = " " * (
                        max(0, 60 - len(return_value.replace("\n", "\\n")))
                    )
                    # print(return_value)
                    print(
                        "RET"
                        + return_value.replace("\n", "\\n")
                        + f"{padding}~~~~~"
                        + "EMB"
                        + embedded_js.replace("\n", "\\n")
                        + f"\tREPLTO ${{{args[func_name][embedded_js]}()}}"
                    )
                    # return_value = return_value.replace(
                    #     embedded_js, f"${{{func_name}[embedded_js]}}"
                    # )
                    return_value = return_value.replace(
                        embedded_js, f"${{{args[func_name][embedded_js]}()}}"
                    )
                    # print(return_value)

            if random.randint(0, 3) == 0:
                code = (
                    f"function {func_name}"
                    f"({",".join(args[func_name].values())}){{"
                    f"return {quote}{return_value}{quote}"
                    f"}}\n" + code
                )
            else:
                code = (
                    # f'{random.choice(("const ", "let ", "", "", ""))}'
                    f"{func_name}=("
                    f"{",".join(args[func_name].values())}"
                    f")=>{quote}{return_value}{quote};\n" + code
                )

    # Update variable name to random name
    # names: list[str] = RE_VARIABLE_NAME.findall(code)
    # # variable_map: dict[str, str] = {}
    # for name in names:
    #     try:
    #         variable_map[name[0] or name[1]]
    #     except KeyError:
    #         variable_map[name[0] or name[1]] = _obfuscate_variable_name(
    #             list(variable_map.values()) + list(string_map.keys())
    #         )
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

    # for original, obfuscated in variable_map.items():
    #     code = repl_js(rf"\b{original}\b", obfuscated, code)

    # Shuffle functions
    # code = _shuffle_functions(code, seed=options.get("seed"))

    # Minify
    if options["is_minify"]:
        code = minify(code, ".js")
    else:
        code = RE_MULTIPLE_BREAK.sub(r"\n", code)

    # print(context.variable_map, context.string_map, string_map)

    # print("variable_map", variable_map)
    # print("already_declared_vars", already_declared_vars)
    # print("string_map", string_map)
    return code


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
