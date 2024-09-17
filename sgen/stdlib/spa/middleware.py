from pathlib import Path
from sgen.base_middleware import BaseMiddleware
import re

SPA_SCRIPT = """<script>(function(a){a.addEventListener("DOMContentLoaded",()=>{d(a)})})(document);window.addEventListener("popstate",async()=>{await history.replaceState({},"",location.href);e(location.href)});async function d(a){console.log("loaded");a=a.getElementsByTagName("a");console.log(a);for(const b of a)b.addEventListener("click",async function(c){c.preventDefault();await history.pushState({},"",c.target.href);e(c.target.href)})}async function e(a){try{const b=await fetch(a);if(!b.ok)throw Error(`Status not ok: ${b.status} URL: ${a}`);const c=await b.text(),f=(new DOMParser).parseFromString(c,"text/html"),g=f.querySelectorAll("script");console.log(g);g.forEach(h=>{console.log(h);const k=document.createElement("script");k.textContent=h.textContent;document.head.appendChild(k)});document.replaceChild(document.adoptNode(f.documentElement),document.documentElement);d(document)}catch(b){console.error(b.message)}}window.transition=e;</script>"""  # noqa: E501


class SPAMiddleware(BaseMiddleware):
    def do(self, buildPath: Path) -> None:
        for file in buildPath.glob("**/*"):
            if file.is_dir():
                continue
            if file.suffix not in [".html", "htm"]:
                continue
            with open(file, "r") as f:
                body = f.read()
            body = re.sub(r"(< */ *head *>)", rf"{SPA_SCRIPT}\1", body)
            with open(file, "w") as f:
                f.write(body)
