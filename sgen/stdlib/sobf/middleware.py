from logging import getLogger
from pathlib import Path
import re
from typing import Unpack
from sgen.base_middleware import BaseMiddleware
from sgen.components.obfuscation.obf import (
    ObfuscateContext,
    ObfuscateOptions,
    obfuscate_js,
)

logger = getLogger(__name__)


class SobfMiddleware(BaseMiddleware):
    def __init__(
        self,
        except_debug: bool = True,
        max_size: int = 50000,
        **options: Unpack[ObfuscateOptions],
    ) -> None:
        self.except_debug = except_debug
        self.max_size = max_size
        self.options = options

    def do(self, build_path: Path) -> None:
        from sgen.get_config import sgen_config

        if self.except_debug and sgen_config.DEBUG:
            return
        context: ObfuscateContext = ObfuscateContext()
        for file in build_path.glob("**/*"):
            if file.stat().st_size > self.max_size:
                logger.warning(
                    f"Skipping too big file obfuscation "
                    f"({file.resolve()}, {file.stat().st_size}byte(s))."
                    f"Changing max_size will obfuscate it.",
                )
                continue
            logger.debug(
                f"Obfuscating {file.resolve()} ({file.stat().st_size}byte(s))"
            )
            if file.suffix == ".js":
                with open(file, "r", encoding="utf-8") as frb:
                    body = frb.read()
                body = obfuscate_js(
                    body,
                    context,
                    **self.options,
                )

                with open(file, "w", encoding="utf-8") as fwb:
                    fwb.write(body)
            if file.suffix == ".html":
                with open(file, "r", encoding="utf-8") as frb:
                    body = frb.read()
                body = obfuscate_js_in_html(body, context, **self.options)
                with open(file, "w", encoding="utf-8") as fwb:
                    fwb.write(body)


def obfuscate_js_in_html(
    body: str,
    context: ObfuscateContext | None = None,
    **options: Unpack[ObfuscateOptions],
):
    context = context or ObfuscateContext()

    def repl_script_tag(m: re.Match[str]):
        js_body = obfuscate_js(
            m.group("body"),
            context,
            **options,
        )
        return m.group("prefix") + js_body + m.group("suffix")

    body = re.sub(
        r"(?P<prefix><script[\s\S]*?>)"
        r"(?P<body>[\s\S]*?)"
        r"(?P<suffix></script *>)",
        repl_script_tag,
        body,
    )

    def repl_attribute(m: re.Match[str]):
        js_body = obfuscate_js(
            m.group("body"),
            context,
            **options,
        )
        return (
            m.group("prefix")
            + js_body.replace('"', "&quot;").replace("'", "&apos;")
            + (m.group("suffix") or "")
        )

    body = re.sub(
        # r"(?P<prefix>on[a-zA-Z]*?\s*=\s*\"?)"
        r"(?P<prefix> on[a-zA-Z]+\s*=\s*([\"\'])?)"
        # r"(?P<body>[\s\S]*?)"
        r"(?P<body>[^\2]*?"
        # r"(?P<suffix>\"?)",
        r"(?P<suffix>\2)|[^ \"']+)",
        repl_attribute,
        body,
    )

    return body
