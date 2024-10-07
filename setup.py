from setuptools import setup, find_packages


setup(
    console=["cli.py"],
    packages=find_packages(),
    # data_files=[
    #     (
    #         "sgen_deps",
    #         ["sgen/dependencies/closure-compiler.jar"],
    #     ),
    #     (
    #         "sgen_templates",
    #         {
    #             file
    #             for file in Path("sgen/templates/").glob("**/*")
    #             if file.is_file()
    #         },
    #     ),
    #     (
    #         "sgen_examples",
    #         {
    #             file
    #             for file in Path("sgen/example/").glob("**/*")
    #             if file.is_file()
    #         },
    #     ),
    # ],
    # package_data={
    #     "dependencies": ["sgen/dependencies/closure-compiler.jar"],
    #     "templates": [
    #         "sgen/templates/project",
    #         "sgen/templates/project/*.py",
    #     ],
    # },
    package_data={
        "sgen": [
            "dependencies/closure-compiler.jar",
            "templates/project/*",
            "templates/project/*.py",
            "example/**/*",
        ]
    },
    install_requires=["Jinja2"],
    entry_points={"console_scripts": ["sgen = sgen.cli:main"]},
)
