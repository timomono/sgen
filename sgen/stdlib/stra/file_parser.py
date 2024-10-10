from collections import OrderedDict
from pathlib import Path
import re
from typing import Generator

from sgen.components.override_decorator import OverrideStrict, override


class StraParseError(Exception):
    pass


class Stra(OverrideStrict):
    """
    > Hello world
    こんにちは世界
    > Welcome to my site!
    私のサイトへようこそ！
    """

    @override
    def __init__(self, value: dict | OrderedDict) -> None:
        self._value = OrderedDict(value)

    @property
    def ordered_dict(self):
        return self._value.copy()

    @staticmethod
    def from_load_file(file: Path):
        with open(file, "r") as f:
            return Stra.from_parse_text(f.read())

    @staticmethod
    def from_parse_text(text: str):
        value: dict[str, str] = {}
        lines = text.splitlines()
        pointer = 0
        while True:
            key = ""
            while lines[pointer].lstrip() == "":
                pointer += 1
                # raise StraParseError('Key should be starts with "> "')
            while True:
                try:
                    line = lines[pointer]
                except IndexError:
                    break

                if not (line.startswith("> ")) and (
                    line.lstrip() != "" or line == "pass"
                ):
                    break
                if line.lstrip() == "":
                    # key += "\n"
                    pointer += 1
                    continue
                key += (
                    re.match(
                        "^> *(.*)$",
                        line,
                    ).group(  # type: ignore
                        1
                    )
                    + " "
                )
                pointer += 1
            if key == "":
                raise StraParseError(f"Excepted key at line {pointer}")
            # Remove \n
            if key[-1] == " ":
                key = key[:-1]
            try:
                lines[pointer]
            except IndexError:
                value[key] = ""
                break
            translated_text = ""
            while True:
                try:
                    line = lines[pointer]
                except IndexError:
                    break

                if line.startswith(">"):
                    break
                if line.strip() == "":
                    pointer += 1
                    continue
                if line.strip() == "pass":
                    pointer += 1
                    continue
                translated_text += line + "\n"
                pointer += 1
            # Remove \n
            if len(translated_text) != 0 and translated_text[-1] == "\n":
                translated_text = translated_text[:-1]

            value[key] = translated_text
            try:
                lines[pointer]
            except IndexError:
                break

        return Stra(value)

    def __getitem__(self, item: str) -> str:
        return self._value[" ".join(s.lstrip() for s in item.splitlines())]

    def __iter__(self) -> Generator[tuple[str, str], None, None]:
        yield from self._value.items()

    @override
    def __str__(self) -> str:
        string = ""
        for key, translated_text in self:
            for line in re.split("\n|\r\n", key):
                string += "> " + line + "\n"
            for line in re.split("\n|\r\n", translated_text):
                string += line + "\n"
        return string


if __name__ == "__main__":
    input_string = """> Hello world
こんにちは世界
> Good
> morning
おはようございます
> How are you?
pass
"""
    string = input_string.replace("\n", "[\\n]")
    print(f"in str\t:{string}")
    stra_obj = Stra.from_parse_text(
        input_string,
    )
    print("object\t:", stra_obj.ordered_dict)
    print(stra_obj["Good morning"])
    print("to str\t:", str(stra_obj).replace("\n", "[\\n]"))
