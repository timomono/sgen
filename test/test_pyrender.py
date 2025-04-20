from io import StringIO
from pathlib import Path
import unittest

from sgen.stdlib.pyrender.renderer import PyRenderer


class SminiTest(unittest.TestCase):
    def test_script(self):
        inp = StringIO(
            """
{{"hey"}}
{% import random %}
{{ random.randint(1, 5) }}
"""
        )
        out = StringIO()
        PyRenderer().render(inp, out, Path.cwd())
        print("rendered:", out.getvalue())
