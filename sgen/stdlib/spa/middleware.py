from pathlib import Path
from sgen.base_middleware import BaseMiddleware
import re

SPA_SCRIPT = """<script>document.addEventListener("DOMContentLoaded",()=>{document.documentElement.classList.remove("spa_loading");c()});window.addEventListener("popstate",async()=>{await history.replaceState({},"",location.href);f(location.href)});async function c(){const b=document.getElementsByTagName("a");for(const a of b)a.addEventListener("click",async function(d){d.preventDefault();await history.pushState({},"",a.href);f(a.href)})}async function f(b){try{document.dispatchEvent(new Event("spa_loading"));document.documentElement.classList.add("spa_loading");const a=await fetch(b);a.ok||(404==a.status&&console.log("404 Error. "),console.error(`Status not ok: ${a.status} URL: ${b}`));const d=await a.text(),e=(new DOMParser).parseFromString(d,"text/html"),h=e.querySelectorAll("script");e.documentElement.classList.add("spa_loading");h.forEach(k=>{const g=document.createElement("script");g.textContent=k.textContent;document.head.appendChild(g)});document.documentElement.innerHTML=e.documentElement.innerHTML;c()}catch(a){console.error(a.message)}finally{document.dispatchEvent(new Event("spa_loaded")),document.documentElement.classList.remove("spa_loading")}}window.transition=f;</script>"""  # noqa: E501


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
