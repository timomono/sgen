from pathlib import Path
import re
from typing import Iterable, override
from sgen.base_middleware import BaseMiddleware
import xml.etree.ElementTree as ET


IGNORE_NAME_LIST = [".DS_Store", "__pycache__"]


class XMLSitemapMiddleware(BaseMiddleware):
    @override
    def do(self, build_path: Path):
        from sgen.get_config import sgen_config

        src_sitemap_path = sgen_config.SRC_DIR / "sitemap.xml"
        urlset = ET.Element("urlset")
        if src_sitemap_path.exists():
            urlset = ET.parse(src_sitemap_path).getroot()
        path_list: Iterable[Path] = build_path.glob("**/*.html")
        rel_path_list: list[Path] = list(
            map(lambda e: e.relative_to(build_path), path_list)
        )
        # for rel_path in rel_path_list:
        #     if rel_path.is_dir():
        #         continue
        #     url = "/" + str(rel_path)
        #     url_element = ET.Element("url")
        #     loc_element = ET.Element("loc")
        #     loc_element.text = url
        #     url_element.append(loc_element)
        #     urlset.append(url_element)
        for url_tag, new_rel_path in zip(urlset.findall("url"), rel_path_list):
            new_url = "/" + str(new_rel_path)
            loc_tag = url_tag.find("loc")
            if loc_tag is None:
                loc_tag = ET.SubElement(url_tag, "loc")
            loc_tag.text = new_url

        for new_rel_path in rel_path_list[
            len(urlset.findall("url")) :  # noqa:E203
        ]:
            new_url = "/" + str(new_rel_path)
            new_url_tag = ET.SubElement(urlset, "url")
            ET.SubElement(new_url_tag, "loc").text = new_url
        doc: bytes

        ET.indent(urlset, space="  ")
        doc = ET.tostring(urlset, "utf-8", xml_declaration=True)
        with open(sgen_config.SRC_DIR / "sitemap.xml", "wb") as f:
            f.write(doc)

        doc = ET.tostring(urlset, "utf-8", xml_declaration=True)
        doc = re.sub(r"[ 　\n]+".encode(), rb" ", doc)
        doc = re.sub(rb" *([><]) *", rb"\1", doc)
        with open(build_path / "sitemap.xml", "wb") as f:
            f.write(doc)
