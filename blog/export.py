"""Optional static compatibility export from the same validated ASGI application."""

from __future__ import annotations

import os
import shutil
import tempfile
from html import escape
from pathlib import Path

from fastapi.testclient import TestClient

from blog.main import ROOT, create_app


def export_site(
    source_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    static_dir: str | Path | None = None,
) -> Path:
    source = Path(source_dir or ROOT / "src").resolve()
    requested_output = Path(output_dir or ROOT / "dist")
    if requested_output.is_symlink():
        raise ValueError("Export directory must not be a symlink")
    output = requested_output.resolve()
    if output.exists() and not output.is_dir():
        raise ValueError("Export target must be a directory")
    protected = [
        source,
        Path(static_dir or ROOT / "blog/static").resolve(),
        ROOT / "blog",
        ROOT / "scripts",
        ROOT / ".git",
    ]
    for directory in protected:
        directory = directory.resolve()
        if output == directory or output in directory.parents or directory in output.parents:
            raise ValueError("Export directory must not overlap project inputs")
    app = create_app(source_dir=source, static_dir=static_dir, static_export=True)
    store = app.state.content
    prefix = app.state.base_path
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        with TestClient(app) as client:
            for route, (kind, value) in store.routes.items():
                if kind == "redirect":
                    target = escape(prefix + value, quote=True)
                    canonical = escape(store.config["siteUrl"] + prefix + value, quote=True)
                    body = (
                        '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
                        f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{canonical}">'
                        f'<title>Weiterleitung</title></head><body><a href="{target}">Über diesen Blog</a></body></html>'
                    )
                else:
                    response = client.get(prefix + route)
                    response.raise_for_status()
                    body = response.text
                destination = staging / (
                    route.lstrip("/") + "index.html" if route.endswith("/") else route.lstrip("/")
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(body)
            response = client.get(prefix + "/__missing__/")
            if response.status_code != 404:
                raise RuntimeError("Expected a rendered 404 page")
            (staging / "404.html").write_text(response.text)
        if app.state.static_dir.is_dir():
            shutil.copytree(app.state.static_dir, staging / "static")
        shutil.copyfile(source / "favicon.svg", staging / "favicon.svg")
        # All validation and rendering finishes before the previous output is moved.
        backup = output.with_name(output.name + ".previous")
        if backup.exists():
            raise RuntimeError(f"Export recovery directory exists: {backup}")
        had_output = output.exists()
        if had_output:
            os.replace(output, backup)
        try:
            os.replace(staging, output)
        except BaseException:
            if had_output:
                os.replace(backup, output)
            raise
        if had_output:
            shutil.rmtree(backup)
        return output
    finally:
        if staging.exists():
            shutil.rmtree(staging)
