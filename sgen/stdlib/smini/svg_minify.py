import re
import io
from xml.etree import ElementTree


def svg_minify(input: str) -> str:
    tree = ElementTree.ElementTree(ElementTree.fromstring(input))
    namespaces = {
        node
        for _, node in ElementTree.iterparse(
            io.StringIO(input), events=["start-ns"]
        )
    }
    for key, value in namespaces:
        ElementTree.register_namespace("", value)

    root = tree.getroot()
    remove_non_svg_elements(root)
    for element in root.iter():
        # Remove unnecessary style
        replaceStyle(element, r"(?<!-)opacity: *1;")
        replaceStyle(element, r"(?<!-)fill-opacity: *1;?")
        replaceStyle(element, r"(?<!-)stroke-opacity: *1;?")

        # Remove id
        if not (
            re.match(
                r"[\s\S]* *<!--( |\n|\r\n)*smini( |\n|\r\n)*:( |\n|\r\n)*"
                r"except[-_]id( |\n|\r\n)*-->[\s\S]*",
                input,
                re.IGNORECASE,
            )
            or (
                re.match(
                    r"[\s\S]* *<!--( |\n|\r\n)*smini( |\n|\r\n)*:( |\n|\r\n)*"
                    r"except[-_]root[-_]id( |\n|\r\n)*-->[\s\S]*",
                    input,
                    re.IGNORECASE,
                )
                and element == root
            )
        ):
            element.attrib.pop("id", "")

    # tree.write("out.svg", xml_declaration=True)
    xmlStr = ElementTree.tostring(
        root,
        encoding="utf-8",
        method="xml",
        # xml_declaration=True,
    ).decode("utf-8")
    xmlStr = re.sub(r">\s+<", "><", xmlStr)
    xmlStr = re.sub(r"<defs .*?/>", "", xmlStr)
    return xmlStr


def remove_non_svg_elements(element: ElementTree.Element):
    attrs_to_remove = [
        attr
        for attr in element.attrib
        if not (attr.startswith("{http://www.w3.org/2000/svg}"))
        and attr.startswith("{")
    ]
    for attr in attrs_to_remove:
        del element.attrib[attr]

    elements_to_remove = []

    for child in element:
        if not child.tag.startswith("{http://www.w3.org/2000/svg}"):
            elements_to_remove.append(child)
        else:
            remove_non_svg_elements(child)

    for child in elements_to_remove:
        element.remove(child)


def replaceStyle(element: ElementTree.Element, pattern: str):
    style = element.get("style", "")
    replacedStyle = re.sub(pattern, "", style)
    if replacedStyle != "":
        pass
        element.set("style", replacedStyle)
