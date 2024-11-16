from pathlib import Path
import re
from sgen.base_middleware import BaseMiddleware


class SelfXSSWarn(BaseMiddleware):
    def __init__(self, use_stra: bool = False) -> None:
        super().__init__()
        self.use_stra = use_stra

    def do(self, build_path: Path) -> None:
        def toTrans(string: bytes) -> bytes:
            if self.use_stra:
                return b'[[trans (key:"' + string + b'")]]'
            else:
                return string

        for file in build_path.glob("**/*.html"):
            with open(file, "rb") as frb:
                body = frb.read()
            body = re.sub(
                rb"(<head[\s\S]*?>)",
                rb"\1<script>"
                + rb"""console.log("""
                + rb""""%c"""
                + toTrans(rb"""Do not enter any code you do not understand""")
                + rb"""%c"""
                + toTrans(
                    rb"Self-XSS attacks can lead to your account being taken "
                    rb"over or your personal information being stolen."
                )
                + rb'",'
                + rb""""color: yellow;background-color:red;font-size:3rem","""
                + rb""""font-size:2rem;font-weight:bold");"""
                + rb"""</script>""",
                body,
            )
            with open(file, "wb") as fwb:
                fwb.write(body)
