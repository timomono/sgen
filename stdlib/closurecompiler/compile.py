from enum import Enum
import subprocess
from pathlib import Path
from typing import Any

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


def compileByText(
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


def valueWithArgName(arg_name: str, values: list[Any]):
    params: list[str] = []
    for filename in values:
        params.append(arg_name)
        params.append(str(filename))


def compileByFilenames(
    input_js_filename: list[Path],
    output_js_filename: list[Path],
    compile_level: CompileLevel = CompileLevel.SIMPLE_OPTIMIZATIONS,
    options: list[str] = [],
):
    options = (
        [
            "java",
            "-jar",
            str(compilerJarFile.resolve().absolute()),
        ]
        + valueWithArgName("--js", input_js_filename)
        + [
            "--js_output_file",
            "--compilation_level",
            compile_level.name,
        ]
        + options
    )
    compiledText = subprocess.run(
        options,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if compiledText.stderr != "The compiler is waiting for input via stdin.\n":
        raise CompileError(
            "Error when running closure-compiler: \n"
            + compiledText.stderr.replace(
                "The compiler is waiting for input via stdin.\n", ""
            )
        )
