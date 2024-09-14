from setuptools import setup

setup(
    console=["cli.py"],
    packages=["sgen"],
    install_requires=["Jinja2"],
    entry_points={"console_scripts": ["sgen = sgen.cli:main"]},
)
