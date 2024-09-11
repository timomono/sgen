from setuptools import setup

setup(
    console=["cli.py"],
    packages=["sgen"],
    entry_points={"console_scripts": ["sgen = sgen.cli:main"]},
)
