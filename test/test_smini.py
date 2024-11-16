import unittest

from sgen.components.minify import minify
import subprocess


class SminiTest(unittest.TestCase):
    def test_script(self):
        script = """
                function sayHello() {
                    const message = "Hello, World!";
                    // No semi-colon
                    console.log(message) 
                    console.log("Console hello world message");
                }
                sayHello();
                """
        obfuscated_script = minify(script, ".js")
        self.assertNotEqual(
            obfuscated_script,
            script,
        )

        result = subprocess.run(
            ("node", "-e", obfuscated_script), stdout=subprocess.PIPE
        )
        self.assertEqual(
            result.stdout.decode("utf-8"),
            "Hello, World!\nConsole hello world message\n",
        )


if __name__ == "__main__":
    unittest.main()
