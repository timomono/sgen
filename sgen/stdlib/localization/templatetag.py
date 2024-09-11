from sgen.get_config import sgen_config
from jinja2.ext import Extension
from jinja2 import nodes
import os


class TransIncludeExtension(Extension):
    tags = {"t_include"}

    def __init__(self, environment):
        super().__init__(environment)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != "block_end":
            args.append(parser.parse_expression())

        return nodes.Output(
            [self.call_method("_render_t_include", args)]
        ).set_lineno(lineno)

    def _render_t_include(self, *args):
        if len(args) != 1:
            raise TypeError(f"Too many or too few arguments ({len(args)})")
        if not isinstance(args[0], str):
            raise TypeError(f"Unexpected type: {type(args[0])} not str")
        include_html_filename = args[0]
        if not include_html_filename.endswith(".html"):
            raise TypeError(f'Specified "{args[0]}" isn\'t html file.')
        try:
            return f'[[trans include (filename:"{include_html_filename}")]]'
            # with open(
            #     sgen_config.SRC_DIR / os.environ["buildLang"] / args[0]
            # ) as f:
            #     return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Included file "{args[0]}" not found '
                "(Tried to load from "
                f'{sgen_config.SRC_DIR / os.environ["buildLang"] / args[0]})'
            )


class TransExtension(Extension):
    tags = {"trans"}

    def __init__(self, environment):
        super().__init__(environment)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != "block_end":
            args.append(parser.parse_expression())

        return nodes.Output(
            [self.call_method("_render_t_include", args)]
        ).set_lineno(lineno)

    def _render_t_include(self, *args):
        if len(args) != 1:
            raise TypeError(f"Too many or too few arguments ({len(args)})")
        if not isinstance(args[0], str):
            raise TypeError(f"Unexpected type: {type(args[0])} not str")
        trans_key = args[0]
        try:
            return f'[[trans (key:"{trans_key}")]]'
            # with open(
            #     sgen_config.SRC_DIR / os.environ["buildLang"] / args[0]
            # ) as f:
            #     return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Included file "{args[0]}" not found '
                "(Tried to load from "
                f'{sgen_config.SRC_DIR / os.environ["buildLang"] / args[0]})'
            )
