from pathlib import Path
import shutil

from sgen.base_middleware import BaseMiddleware
from sgen.components.base_num import encode_base_n, encode_bytes_to_base_n
from sgen.components.override_decorator import override

import os, base64

try:
    from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    raise ImportError(
        "cryptography library is required. Try: `pip install cryptography`"
    )


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    iv = os.urandom(12)

    # Derive 256-bit key with PBKDF2-SHA256, 100k iterations
    ciphertext = AESGCM(key).encrypt(iv, plaintext, None)

    # Pack: salt(16) + iv(12) + ciphertext — then base64 for easy transport
    blob = iv + ciphertext
    return blob


print(encrypt(b"Hello from Python!", b"m" * 32))


class EncrypterMiddleware(BaseMiddleware):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def do(self, build_path: Path) -> None:
        # Register
        template_dir = Path(__file__).parent / "register"
        target_dir = build_path / "_encrypter" / "register"

        if target_dir.exists():
            raise FileExistsError(
                "Directory '_encrypter/register' already exists"
            )

        target_dir.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(template_dir, target_dir)

        return super().do(build_path)
    
    def after(self, build_path: Path) -> None:
        # Encrypt
        encrypted_dir = build_path / "_encrypted"
        files = build_path.glob("*/**")

        for file in files:
            ENCRYPTER_DIR = build_path / "_encrypter"
            if file.is_relative_to(ENCRYPTER_DIR):
                continue # skip dirs in _encrypter
            if file.is_dir():
                continue
            
            original_relative_path = file.relative_to(build_path)
            encrypted_relative_path = encrypt(str(original_relative_path).encode(), b"m" * 32)
            encrypted_path = encrypted_dir / encode_bytes_to_base_n(
                encrypted_relative_path, 38, 
                "0123456789abcdefghijklmnopqrstuvwxyz-_"
                )
            encrypted_path.parent.mkdir(parents=True, exist_ok=True)
            body = file.read_bytes()
            with open(encrypted_path, "wb") as f:
                f.write(encrypt(body, b"m" * 32))

        SKIP_PATHS = ["_encrypter", "_encrypted"]
        build_glob = list(build_path.glob("*"))
        for path in build_glob:
            if path.name in SKIP_PATHS:
                continue # skip _encrypter dir
            if not path.is_dir():
                path.unlink()
                continue
            shutil.rmtree(
                path
            )
        return super().after(build_path)
