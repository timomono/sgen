def encode_base_n(num: int, base: int, chars: str | None = None):
    """
    Encode a number to base N string

    Args:
        num: Integer to encode
        base: Base to use (2-62 typically)
        chars: Custom character set (optional)
    """
    if num == 0:
        return chars[0] if chars else "0"

    if chars is None:
        chars = (
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )

    if base > len(chars):
        raise ValueError(f"Base {base} requires at least {base} characters")

    result = []
    negative = num < 0
    num = abs(num)

    while num > 0:
        result.append(chars[num % base])
        num //= base

    if negative:
        result.append("-")

    return "".join(reversed(result))


def decode_base_n(s: str, base: int, chars: str | None = None):
    """
    Decode base N string to integer

    Args:
        s: String to decode
        base: Base used for encoding
        chars: Custom character set (must match encoding)
    """
    if chars is None:
        chars = (
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )

    if base > len(chars):
        raise ValueError(f"Base {base} requires at least {base} characters")

    negative = s.startswith("-")
    if negative:
        s = s[1:]

    result = 0
    for char in s:
        value = chars.find(char)
        if value == -1 or value >= base:
            raise ValueError(f"Invalid character '{char}' for base {base}")
        result = result * base + value

    return -result if negative else result


def encode_bytes_to_base_n(
    data: bytes, base: int, chars: str | None = None
) -> str:
    """Wrapper: Encode bytes to base N string using encode_base_n"""
    # Convert bytes to integer
    num = int.from_bytes(data, "big")
    # Use existing encode function
    return encode_base_n(num, base, chars)


def decode_bytes_from_base_n(
    s: str, base: int, chars: str | None = None
) -> bytes:
    """Wrapper: Decode base N string to bytes using decode_base_n"""
    # Use existing decode function
    num = decode_base_n(s, base, chars)
    # Convert integer back to bytes
    if num == 0:
        return b"\x00"
    byte_length = (num.bit_length() + 7) // 8
    return num.to_bytes(byte_length, "big")
