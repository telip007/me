"""Temporary local UI fixture. Never writes to the publication source.

Run: uv run python -m tests.serve_ui_fixture (if tests is a package), or
     uv run python tests/serve_ui_fixture.py
The process owns its temporary directory and removes it on shutdown.
"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from blog.main import create_app

BODY = """This is a local test fixture. It is not a published article or a claim about an experiment.

## A concrete question

A reading interface must keep the question, example and evidence connected. This fixture exercises the layout with [a descriptive source link](https://developer.mozilla.org/en-US/docs/Web/HTML).

## The smallest useful example

```python
from fastapi import FastAPI
app = FastAPI()
# A deliberately long code line tests local horizontal scrolling without widening the whole page.
example = 'abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz'
```

| Approach | Useful property | Boundary | A deliberately wide extra column |
| --- | --- | --- | --- |
| Native HTML | Readable without scripts | Full document navigation | ALongUnbrokenValueThatTestsHorizontalTableScrollingOnNarrowScreens |
| HTMX | Server-rendered updates | Requires a runtime | A second value |

## What the evidence establishes

No measurements are asserted here. A fixture checks presentation; it is not evidence of production performance.

> A useful caveat belongs next to the statement it qualifies.

### A narrower detail

Repeated headings also need distinct anchors.

## A concrete question

**Strong text**, *emphasis*, ~~removed wording~~, and inline `code` remain legible. A long link tests wrapping: https://example.test/very/long/path/without/a/convenient/place/to/break/abcdefghijklmnopqrstuvwxyz0123456789
"""


def serve(port=8001):
    with tempfile.TemporaryDirectory(prefix="personal-blog-ui-") as directory:
        source = Path(directory) / "src"
        shutil.copytree(ROOT / "src", source)
        shutil.rmtree(source / "posts")
        (source / "posts").mkdir()
        for lang, slug, title in [
            ("de", "leseprobe", "Wie eine technische Erklärung überprüfbar wird"),
            ("en", "reading-check", "How to make a technical explanation verifiable"),
        ]:
            metadata = {
                "title": title,
                "slug": slug,
                "lang": lang,
                "translationKey": "reading-check",
                "date": "2026-10-29",
                "tags": ["LLM", "Engineering"],
                "excerpt": "Lokale Layoutprüfung mit Code, Tabellen und Quellen. Kein veröffentlichter Artikel."
                if lang == "de"
                else "A local layout check with code, tables and sources. Not a published article.",
            }
            (source / "posts" / f"{lang}.md").write_text(
                "---json\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n" + BODY
            )
        metadata = {
            "title": "Softwareentwicklungswerkzeugkettenverantwortungsabgrenzungsprüfung",
            "slug": "long-title",
            "date": "2026-10-28",
            "tags": ["Engineering"],
            "excerpt": "Lokaler Test eines sehr langen Titels.",
        }
        (source / "posts" / "long.md").write_text(
            "---json\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n" + BODY
        )
        uvicorn.run(create_app(source_dir=source), host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8001)
    serve(parser.parse_args().port)
