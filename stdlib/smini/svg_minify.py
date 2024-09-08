import re
from xml.etree import ElementTree


def main():
    tree = ElementTree.parse("in.svg")
    namespaces = {
        node[0]: node[1]
        for _, node in ElementTree.iterparse("in.svg", events=["start-ns"])
    }
    for key, value in namespaces.items():
        ElementTree.register_namespace("", value)

    root = tree.getroot()
    for element in root.iter():
        # Remove unnecessary style
        replaceStyle(element, r"(?<!-)opacity: *1;")
        replaceStyle(element, r"(?<!-)fill-opacity: *1;?")
        replaceStyle(element, r"(?<!-)stroke-opacity: *1;?")

        # Remove id
        element.attrib.pop("id", "")

    # tree.write("out.svg", xml_declaration=True)
    xmlStr = ElementTree.tostring(
        root, encoding="utf-8", method="xml", xml_declaration=True
    ).decode("utf-8")
    xmlStr = re.sub(r">\s+<", "><", xmlStr)
    xmlStr = re.sub(r"<defs .*?/>", "", xmlStr)
    with open("out.svg", "w") as f:
        f.write(xmlStr)


def replaceStyle(element: ElementTree.Element, pattern: str):
    style = element.get("style", "")
    replacedStyle = re.sub(pattern, "", style)
    if replacedStyle != "":
        pass
        element.set("style", replacedStyle)


if __name__ == "__main__":
    main()
