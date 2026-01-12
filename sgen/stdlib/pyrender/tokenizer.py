from collections.abc import Generator
from enum import Enum
from io import BufferedReader, BufferedWriter
from typing import BinaryIO, Callable

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
        if byte == b"{" and prev_byte == b"{":
            if current:
                yield Token(current[:-1], TokenType.TEXT)
                current = b""
            yield Token(b"{{", TokenType.PUNCTUATION)
        elif byte == b"}" and prev_byte == b"}":
            if current:
                yield Token(current[:-1], TokenType.TEXT)
                current = b""
            yield Token(b"}}", TokenType.PUNCTUATION)
        else:
            current += byte

        prev_byte = byte

    if current:
        yield Token(current, TokenType.TEXT)


def processTags(
    from_: BufferedReader | BinaryIO,
    to: BufferedWriter | BinaryIO,
    eval: Callable,
):
    from_.seek(0)
    tokens = tokenize(from_)

    depth = 0
    tag = b""
    for token in tokens:
        print(token)
        tag += token.token
        if token.type == TokenType.PUNCTUATION:
            # print(token.token)
            if token.token == b"{{":
                depth += 1
                # print(depth)
                if depth == 1:
                    tag = b""

            elif token.token == b"}}":
                depth -= 1
                if depth == 0:
                    to.write(str(eval(tag[:-2])).encode())
                    tag = b""
        if depth == 0:
            # print("raw", tag)
            to.write(tag)
