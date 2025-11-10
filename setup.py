from setuptools import setup, find_packages


setup(
    console=["cli.py"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Jinja2"],
    entry_points={"console_scripts": ["sgen = sgen.cli:main"]},
)
