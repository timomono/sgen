from enum import Enum
import subprocess
from pathlib import Path

compilerJarFile = (
    Path(__file__).parent.parent.parent
    / "dependencies"
    / "closure-compiler.jar"
)


class CompileError(Exception):
    pass


class CompileLevel(Enum):
    WHITESPACE_ONLY = 0
    SIMPLE_OPTIMIZATIONS = 1
    ADVANCED_OPTIMIZATIONS = 2


def compile(
    inputJs: str,
    compile_level: CompileLevel = CompileLevel.SIMPLE_OPTIMIZATIONS,
    options: list[str] = [],
) -> str:
    options += [
        "java",
        "-jar",
        str(compilerJarFile.resolve().absolute()),
        "--compilation_level",
        compile_level.name,
    ]
    compiledText = subprocess.run(
        options,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        input=inputJs,
    )
    if compiledText.stderr != "The compiler is waiting for input via stdin.\n":
        raise CompileError(
            "Error when running closure-compiler: \n"
            + compiledText.stderr.replace(
                "The compiler is waiting for input via stdin.\n", ""
            )
        )
    return compiledText.stdout
