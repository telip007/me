"""Container health probe that follows the configured application mount."""

import json
from pathlib import Path
from urllib.request import urlopen

from blog.content import normalize_base_path


def main():
    config = json.loads((Path(__file__).resolve().parents[1] / "src/config.json").read_text())
    base_path = normalize_base_path(config.get("basePath"))
    with urlopen(f"http://127.0.0.1:8000{base_path}/healthz", timeout=2) as response:
        if response.status != 200:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
