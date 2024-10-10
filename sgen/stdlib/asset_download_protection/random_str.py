from pathlib import Path
from random import choice, randint
from string import ascii_letters, digits, ascii_lowercase


def random_path(base_path: Path, ext: str = "") -> Path:
    return _random_path(base_path).with_suffix(ext)


def _random_path(base_path: Path) -> Path:
    res = base_path / Path(random_text())
    if randint(0, 1) == 0 or res.exists():
        return base_path / _random_path(base_path)
    else:
        return res


def random_text() -> str:
    method = randint(0, 3)
    if method == 0:
        return _random_string()
    elif method == 1:
        return random_number()
    elif method == 2:
        return _random_lowercase()
    else:
        return _random_sentence()


def _random_sentence() -> str:
    return "_".join(_random_word() for i in range(randint(1, 6)))


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
    return "".join(choice(ascii_lowercase + "_" * 5) for i in range(length))


def random_number(length: int | None = None) -> str:
    length = length or randint(5, 30)
    return "".join(choice(digits) for i in range(length))


if __name__ == "__main__":
    print(random_text())
