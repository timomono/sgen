from collections.abc import Generator
from enum import Enum
from io import BufferedReader, BufferedWriter
from typing import BinaryIO, Callable

from sgen.stdlib.pyrender.avoid_escape import AvoidEscape
import html

# """
# example:
# [
#     {
#         token: b"helloworld{{1+1=0}}",
#         children: [
#             {
#                 token: ""
#             }
#         ]
#     }
# ]
# """


class TokenType(Enum):
    PUNCTUATION = "punctuation"
    TEXT = "text"


class Token:
    def __init__(self, token: bytes, type: TokenType) -> None:
        self.token = token
        self.type = type

    def __str__(self) -> str:
        return f"Token(type={self.type}, token='{self.token.decode()}')"


def tokenize(from_: BufferedReader | BinaryIO) -> Generator[Token, None, None]:
    current = b""
    prev_byte = b""
    while True:
        byte: bytes = from_.read(1)
        if byte == b"":
            break
        if prev_byte == b"{" and (byte == b"{" or byte == b"%"):
            if current:
                yield Token(current[:-1], TokenType.TEXT)
                current = b""
            yield Token(prev_byte + byte, TokenType.PUNCTUATION)
        elif (prev_byte == b"%" or prev_byte == b"}") and byte == b"}":
            if current:
                yield Token(current[:-1], TokenType.TEXT)
                current = b""
            yield Token(prev_byte + byte, TokenType.PUNCTUATION)
        else:
            current += byte

        prev_byte = byte

    if current:
        yield Token(current, TokenType.TEXT)


punctuationPair = {
    b"{{": b"}}",
    b"{%": b"%}",
}


class PyrenderSyntaxError(SyntaxError):
    def __str__(self) -> str:
        return f"PyrenderSyntaxError('{self.msg}')"


def processTags(
    from_: BufferedReader | BinaryIO,
    to: BufferedWriter | BinaryIO,
    eval: Callable[[bytes], str],
    exec: Callable[[bytes], None],
):
    from_.seek(0)
    tokens = tokenize(from_)

    depth = 0
    tag = b""
    currentLine = 1
    startPunctuations: list[bytes] = []
    for token in tokens:
        currentLine += token.token.count(b"\n")
        tag += token.token
        if token.type == TokenType.PUNCTUATION:
            # if len(startPunctuations) > 0:
            #     print(punctuationPair[startPunctuations[-1]])
            # print(token.token)
            if token.token == b"{{" or token.token == b"{%":
                depth += 1
                startPunctuations.append(token.token)
                # print(depth)
                if depth == 1:
                    tag = b""
            elif (
                len(startPunctuations) > 0
                and token.token == punctuationPair[startPunctuations[-1]]
            ):
                startPunctuations.pop()
                depth -= 1
                if depth == 0:
                    if token.token == b"}}":
                        result = eval(tag[:-2])
                        if isinstance(result, AvoidEscape):
                            result = result.value
                        else:
                            result = html.escape(result)
                        to.write(str(result).encode())
                    elif token.token == b"%}":
                        exec(tag[:-2])
                    tag = b""
            elif token.token == b"}}" or token.token == b"%}":
                raise PyrenderSyntaxError(
                    f"Mismatch punctuations (at line {currentLine})"
                )
        if depth == 0:
            # print("raw", tag)
            to.write(tag)
