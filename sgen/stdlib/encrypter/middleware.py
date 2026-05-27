from pathlib import Path
import shutil

from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override

import os, base64

try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    raise ImportError(
        "cryptography library is required. Try: `pip install cryptography`"
    )


def encrypt(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)

    # Derive 256-bit key with PBKDF2-SHA256, 100k iterations
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000
    )
    key = kdf.derive(password.encode())

    ciphertext = AESGCM(key).encrypt(iv, plaintext.encode(), None)

    # Pack: salt(16) + iv(12) + ciphertext — then base64 for easy transport
    blob = base64.b64encode(salt + iv + ciphertext).decode()
    return blob


print(encrypt("Hello from Python!", "my-secret-password"))


class EncrypterMiddleware(BaseMiddleware):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def do(self, build_path: Path) -> None:
        template_dir = Path(__file__).parent / "register"
        target_dir = build_path / "_encrypter" / "register"

        if target_dir.exists():
            raise FileExistsError(
                "Directory '_encrypter/register' already exists"
            )

        target_dir.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(template_dir, target_dir)
        return super().do(build_path)

    @override
    def after(self, build_path: Path) -> None:
        return super().after(build_path)
