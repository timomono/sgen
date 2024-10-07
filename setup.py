from setuptools import setup, find_packages

setup(
    console=["cli.py"],
    packages=find_packages(include=("*", "*.js")),
    data_files=[
        (
            "sgen_deps",
            ["sgen/dependencies/closure-compiler.jar"],
        ),
    ],
    # package_data={"sgen": ["*.jar"]},
    install_requires=["Jinja2"],
    entry_points={"console_scripts": ["sgen = sgen.cli:main"]},
)
