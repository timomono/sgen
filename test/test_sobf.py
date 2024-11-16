import base64
from time import sleep
import unittest

from sgen.components.obfuscation.obf import obfuscate_js
import subprocess
from logging import getLogger, basicConfig, DEBUG

from sgen.stdlib.sobf.middleware import obfuscate_js_in_html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

logger = getLogger(__name__)

script = """
function sayHello(param) {
    const message = "Hello, World!";
    console.log(message) // No semi-colon
    console.log('Console hello world message');
    if (message == param){
        console.log(`message
msg`)
    }
    const animal = {
        "cat": "Cat",
        "dog": "Dog",
    }
    console.log(animal.cat);
}
sayHello('Hello, World!');
"""


class SobfTest(unittest.TestCase):
    def test_script(self):
        for i in range(50):
            obfuscated_script = obfuscate_js(script, seed=i, is_minify=False)
            self.assertNotEqual(
                obfuscated_script,
                script,
            )

            result = subprocess.run(
                ("node", "-e", obfuscated_script), stdout=subprocess.PIPE
            )
            self.assertEqual(
                result.stdout.decode("utf-8"),
                "Hello, World!\nConsole hello world message\n"
                "message\nmsg\nCat\n",
                f"Seed: {i}, {obfuscated_script}",
            )

    def test_html(self):
        options = webdriver.ChromeOptions()
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        # options.add_argument("--headless")

        driver = webdriver.Chrome(
            options=options,
        )
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <script>
        {script}
    </script>
    <script>
        {script}
    </script>
    <button onclick="" id="hello_btn">
</body>
</html>"""
        driver.get(
            "data:text/html;base64," + base64.b64encode(html.encode()).decode()
        )
        driver.find_element(By.ID, "hello_btn").click()
        logs: list[dict[str, str]] = driver.get_log("browser")
        original_output = list(
            map(lambda log: log["message"].split('"')[1], logs)
        )
        for i in range(3, 50):
            obfuscated_script = obfuscate_js_in_html(
                html, seed=i, is_minify=False
            )
            self.assertNotEqual(
                obfuscated_script,
                script,
                f"Seed: {i}, {obfuscated_script}",
            )
            driver.get(
                "data:text/html;base64,"
                + base64.b64encode(obfuscated_script.encode()).decode()
            )
            try:
                driver.find_element(By.ID, "hello_btn").click()
            except NoSuchElementException:
                raise Exception(
                    f'No such element "hello_btn" ({obfuscated_script})'
                )
            logs: list[dict[str, str]] = driver.get_log("browser")

            errors = list(filter(lambda log: log["level"] == "SEVERE", logs))
            sleep(100)
            if errors != []:
                raise Exception(errors, f"Seed: {i}, {obfuscated_script}")

            output = list(map(lambda log: log["message"].split('"')[1], logs))

            self.assertEqual(
                original_output,
                output,
                f"Seed: {i}, {obfuscated_script}",
            )


if __name__ == "__main__":
    basicConfig(level=DEBUG)
    logger.setLevel(DEBUG)
    unittest.main()