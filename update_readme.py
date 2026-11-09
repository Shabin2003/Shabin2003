"""Rewrite the project list in README.md from the portfolio's projects.json."""
import json
import logging
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = "https://shabin2003.github.io/projects.json"
START, END = "<!-- projects:start -->", "<!-- projects:end -->"

(ROOT / "logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s() %(message)s",
    handlers=[logging.FileHandler(ROOT / "logs" / "update.log", encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)


def fetch_projects():
    with urllib.request.urlopen(SOURCE, timeout=30) as response:
        projects = json.load(response)
    log.info("fetched %d projects from %s", len(projects), SOURCE)
    return projects


def project_line(project):
    description = project["description"].replace("|", "/").replace("\n", " ")
    demo = f" · [demo]({project['demo']})" if project["demo"] else ""
    return f"- **[{project['name']}]({project['url']})**{demo}" + (f": {description}" if description else "")


def render_list(projects):
    featured = [p for p in projects if p["featured"]]
    others = [p for p in projects if not p["featured"]]
    parts = []
    if featured:
        parts += ["### Selected work", "", *map(project_line, featured), ""]
    if others:
        parts += ["### More projects" if featured else "### Projects", "", *map(project_line, others), ""]
    return "\n".join(parts)


def main():
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = f"{START}\n{render_list(fetch_projects())}{END}"
    updated, count = re.subn(f"{re.escape(START)}.*?{re.escape(END)}", lambda _: block, text, flags=re.S)
    if count != 1:
        raise RuntimeError(f"expected one project block in README.md, found {count}")
    readme.write_text(updated, encoding="utf-8", newline="\n")
    log.info("README.md %s", "updated" if updated != text else "unchanged")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("README update failed")
        raise
