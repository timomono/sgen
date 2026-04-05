from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="sgen-tool",
    version="1.0.0",
    description="Simple Python-based static site generator",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="timomono",
    python_requires=">=3.11,<=3.13",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "sgen=sgen.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    license="BSD-3-Clause",
    license_files=["LICENSE"],
    url="https://github.com/timomono/sgen",
    project_urls={
        "Bug Tracker": "https://github.com/timomono/sgen/issues",
        "Source Code": "https://github.com/timomono/sgen",
    },
)
