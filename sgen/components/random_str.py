from pathlib import Path
from os.path import relpath
from random import choice, randint
from string import ascii_letters, digits, ascii_lowercase
from typing import Sequence


def random_path_to_url(
    path: Path,
    from_: Path,
    base_path: Path,
    always_absolute_filenames: tuple[str] = ("404.html",),
    is_absolute: None | bool = None,
):
    if (
        randint(0, 1) == 0
        or path.name in always_absolute_filenames
        or is_absolute is True
    ) and is_absolute is not False:
        return "/" + str(path.relative_to(base_path))
    else:
        return str(relpath(path if path.is_file() else path, from_))


def random_path(base_path: Path, ext: str = "", max_depth: int = 3) -> Path:
    return (
        random_folder_path(base_path, max_depth) / random_text()
    ).with_suffix(ext)


# def random_folder_path(base_path: Path, max_depth: int = 3) -> Path:
#     res = base_path / random_text()
#     print(max_depth, res)
#     if (randint(0, 1) == 0) and max_depth > 0 and not res.exists():
#         res.mkdir()
#         res = random_folder_path(res, max_depth=max_depth - 1)
#         return res
#     else:
#         return base_path


def random_folder_path(base_path: Path, max_depth: int = 3) -> Path:
    if base_path.is_file():
        raise TypeError("base_path should be directory (not file)")
    return_value = Path(base_path)
    for i in range(randint(0, max_depth)):
        while True:
            if not (res := return_value / random_text()).exists():
                break
        return_value = res
        return_value.mkdir()
    return return_value


def random_text() -> str:
    method = randint(0, 3)
    match method:
        case 0:
            return _random_string()
        case 1:
            return random_number()
        case 2:
            return _random_lowercase()
        case _:
            return _random_sentence()


def _random_sentence() -> str:
    return "-".join(_random_word() for i in range(randint(1, 6)))


def _random_word() -> str:
    return choice(
        (
            "animal",
            "panda",
            "javascript",
            "main",
            "script",
            "page",
            "logic",
            "cat",
            "dog",
            "meow",
            "banana",
            "apple",
            "many",
            "code",
        )
    )


def _random_string(length: int | None = None) -> str:
    length = length or randint(5, 30)
    return "".join(choice(ascii_letters + digits) for i in range(length))


def _random_lowercase(length: int | None = None) -> str:
    length = length or randint(5, 30)
    return "".join(choice(ascii_lowercase + "-" * 5) for i in range(length))


def random_number(length: int | None = None) -> str:
    length = length or randint(5, 30)
    return "".join(choice(digits) for i in range(length))


def random_base_number_to_str(integer: int) -> str:
    obf_str = ""
    match randint(0, 8):
        case 0:
            obf_str = str(integer)
        case 1:
            obf_str = bin(integer)
        case 2:
            obf_str = oct(integer)
        case _:
            obf_str = hex(integer)
    return obf_str


def random_expression_to_str(integer: int, random_base_number=True) -> str:

    def number(n: int) -> str:
        return random_base_number_to_str(n) if random_base_number else str(n)

    match randint(0, 8):
        case 0:
            while True:
                number_to_divide = randint(1, 10)
                if (integer / number_to_divide).is_integer():
                    break
            return (
                str(number(int(integer / number_to_divide)))
                + "*"
                + str(number(number_to_divide))
            )
        case 1:
            num_to_sub = randint(0, integer)
            return f"{number(integer + num_to_sub)}-{number(num_to_sub)}"
        case 2:
            number_to_add = randint(0, integer)
            return f"{number(integer - number_to_add)}+{number(number_to_add)}"
        case _:
            return number(integer)


def random_join_to_str(string: Sequence[str]) -> str:
    rand = randint(0, len(string))
    return (
        '"'
        + "".join(string[:rand])
        + '"'
        + "+"
        + '"'
        + "".join(string[rand:])
        + '"'
    )


if __name__ == "__main__":
    print(random_text())
