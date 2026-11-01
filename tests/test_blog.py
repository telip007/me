import json
import re
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from blog.content import ContentError, load_content
from blog.export import export_site
from blog.main import create_app


def social_image(page):
    match = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    assert match, "Every public article needs a share image"
    return match[1]


def test_generated_share_card_metadata_and_image(source):
    post(source, meta='slug: models\ntitle: "Models & agents"')
    client = TestClient(create_app(source_dir=source, base_path="/me"))
    page = client.get("/me/articles/models/").text
    image = social_image(page)
    assert image.startswith("https://example.test/me/social/")
    assert 'name="twitter:card" content="summary_large_image"' in page
    assert f'name="twitter:image" content="{image}"' in page
    assert 'property="og:image:width" content="1200"' in page
    assert 'property="og:image:height" content="630"' in page
    assert 'property="og:image:alt"' in page
    assert json.loads(re.search(r'application/ld\+json">(.*?)</script>', page, re.DOTALL)[1])["image"] == image
    response = client.get(urlsplit(image).path)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert int.from_bytes(response.content[16:20], "big") == 1200
    assert int.from_bytes(response.content[20:24], "big") == 630
    assert len(response.content) < 300_000
    assert "immutable" in response.headers["cache-control"]
    assert client.head(urlsplit(image).path).status_code == 200
    assert client.get(urlsplit(image).path, headers={"If-None-Match": response.headers["etag"]}).status_code == 304


def test_share_cards_are_individual_and_change_with_content(source):
    post(source, meta="slug: first\ntitle: First article")
    post(source, "second", "slug: second\ntitle: Second article")
    client = TestClient(create_app(source_dir=source))
    first = social_image(client.get("/articles/first/").text)
    second = social_image(client.get("/articles/second/").text)
    assert first != second
    assert client.get(urlsplit(first).path).content != client.get(urlsplit(second).path).content
    post(source, meta="slug: first\ntitle: An edited title")
    updated = TestClient(create_app(source_dir=source))
    current = social_image(updated.get("/articles/first/").text)
    assert current != first
    stale = updated.get(urlsplit(first).path)
    assert stale.status_code == 200
    assert stale.content == updated.get(urlsplit(current).path).content
    assert stale.headers["cache-control"] == "no-cache"
    post(source, meta="slug: first\ndraft: true")
    private = TestClient(create_app(source_dir=source))
    assert private.get(urlsplit(first).path).status_code == 404


def test_share_cards_preserve_custom_images_and_exclude_private_posts(source, tmp_path):
    post(source, meta="slug: custom\nimage: https://cdn.example.test/cover.jpg")
    post(source, "secret", "slug: secret\ndraft: true")
    post(source, "german", "slug: german\nlang: de")
    client = TestClient(create_app(source_dir=source))
    assert social_image(client.get("/articles/custom/").text) == "https://cdn.example.test/cover.jpg"
    for route in ["/social/secret.png", "/social/german.png", "/social/unknown/123.png"]:
        assert client.get(route).status_code == 404
    output = export_site(source_dir=source, output_dir=tmp_path / "dist")
    assert not (output / "social").exists()


def test_static_export_includes_generated_share_images(source, tmp_path):
    post(source, meta="slug: models")
    config = json.loads((source / "config.json").read_text())
    config["basePath"] = "/me"
    (source / "config.json").write_text(json.dumps(config))
    output = export_site(source_dir=source, output_dir=tmp_path / "dist")
    image = social_image((output / "articles/models/index.html").read_text())
    path = urlsplit(image).path.removeprefix("/me/")
    assert (output / path).read_bytes().startswith(b"\x89PNG")
    assert len(list((output / "social").rglob("*.png"))) == 1


@pytest.fixture
def source(tmp_path):
    src = tmp_path / "src"
    (src / "posts").mkdir(parents=True)
    (src / "config.json").write_text(
        json.dumps(
            {
                "siteUrl": "https://example.test",
                "basePath": "",
                "siteTitle": "Example",
                "siteSubtitle": "Building with AI",
                "siteDescription": "Description",
                "author": "Example",
            }
        )
    )
    (src / "about.md").write_text("---\ntitle: About this blog\nslug: about\n---\n# About this blog")
    (src / "privacy.md").write_text("# Privacy\n\nExisting English privacy notice.")
    (src / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    return src


def post(source, name="english", meta="", body="A useful article."):
    path = source / "posts" / f"{name}.md"
    defaults = {"title": name, "date": "'2026-01-01'", "tags": "[LLM]"}
    header = "\n".join(
        f"{key}: {value}" for key, value in defaults.items() if not re.search(rf"(?m)^{key}:", meta)
    )
    path.write_text(f"---\n{header}\n{meta}\n---\n{body}")
    return path


def test_content_routes_and_safe_markdown(source):
    post(
        source,
        meta="slug: models",
        body="## A heading\n\n<script>alert(1)</script>\n\n[Bad](javascript:alert(1))",
    )
    post(source, "german", "lang: de\nslug: modelle", "GERMAN_PRIVATE_MARKER")
    store = load_content(source)
    assert len(store.posts) == 1
    english = store.posts[0]
    assert english.lang == "en"
    assert english.url == "/articles/models/"
    assert "<script>" not in english.html
    assert 'href="javascript:' not in english.html
    assert '<h2 id="a-heading">' in english.html
    assert english.toc[0]["id"] == "a-heading"


def test_drafts_future_dates_and_metadata_validation(source):
    post(source, meta="slug: visible\ntranslationKey: pair\ndate: '2030-01-01'")
    post(source, "en", "lang: en\nslug: secret\ntranslationKey: pair\ndraft: true", "PRIVATE_DRAFT_MARKER")
    store = load_content(source)
    assert len(store.posts) == 1
    assert store.posts[0].lang == "en"
    post(source, "en", "draft: 'yes'")
    with pytest.raises(ContentError, match="draft must be true or false"):
        load_content(source)


@pytest.mark.parametrize(
    "meta,message",
    [
        ("slug: ../../escape", "Invalid post slug"),
        ("lang: fr", "Unsupported lang"),
        ("tags: nope", "tags must be an array"),
        ("date: nonsense", "Valid date required"),
    ],
)
def test_invalid_metadata_fails_closed(source, meta, message):
    post(source, meta=meta)
    with pytest.raises(ContentError, match=message):
        load_content(source)


def test_duplicate_routes_translations_and_tag_collisions(source):
    post(source, meta="slug: same\ntranslationKey: pair")
    post(source, "other", "slug: other\ntranslationKey: pair")
    with pytest.raises(ContentError, match="Duplicate translationKey"):
        load_content(source)
    post(source, "other", "slug: same")
    with pytest.raises(ContentError, match="Duplicate output route"):
        load_content(source)
    post(source, "other", "slug: other\ntags: [llm]")
    with pytest.raises(ContentError, match="Tag slug collision"):
        load_content(source)


def test_nonexecutable_yaml_and_json(source):
    file = source / "posts" / "unsafe.md"
    file.write_text("---javascript\n({title: process.exit(1)})\n---\nUnsafe")
    with pytest.raises(ContentError, match="Only YAML or JSON"):
        load_content(source)
    file.write_text(
        "---\ntitle: !!python/object/apply:os.system ['touch /tmp/blog-should-never-exist']\n---\nUnsafe"
    )
    with pytest.raises(ContentError):
        load_content(source)
    file.write_text('---json\n{"title":"Safe JSON","date":"2026-01-01","slug":"safe"}\n---\nSafe')
    assert load_content(source).posts[0].title == "Safe JSON"


def test_routes_filter_fragments_and_base_path(source):
    post(source, meta="slug: models")
    client = TestClient(create_app(source_dir=source, base_path="/me"))
    home = client.get("/me/")
    assert home.status_code == 200
    assert '<html lang="en"' in home.text
    assert 'href="/me/about/"' in home.text
    assert "language-switch" not in home.text
    english = client.get("/me/articles/models/")
    assert 'rel="canonical" href="https://example.test/me/articles/models/"' in english.text
    assert "hreflang=" not in english.text
    fragment = client.get("/me/?q=missing", headers={"HX-Request": "true"})
    assert fragment.status_code == 200
    assert "<html" not in fragment.text
    assert "models/" not in fragment.text
    assert "HX-Request" in fragment.headers["vary"]
    full = client.get("/me/?q=missing")
    assert "<html" in full.text
    assert "models/" not in full.text
    assert client.get("/me/archive/").status_code == 404
    assert 'lang="en"' in client.get("/me/not-found/").text
    assert "Existing English privacy notice." in client.get("/me/privacy/").text
    for path in ["/me/articles/", "/me/tags/", "/me/tags/llm/"]:
        assert client.get(path).status_code == 200


def test_legacy_english_and_legal_routes_redirect_canonical(source):
    post(source, meta="slug: models")
    client = TestClient(create_app(source_dir=source, base_path="/me"))
    paths = {
        "/en/": "/",
        "/en/articles/": "/articles/",
        "/en/articles/models/": "/articles/models/",
        "/en/tags/": "/tags/",
        "/en/tags/llm/": "/tags/llm/",
        "/en/about/": "/about/",
        "/en/rss.xml": "/rss.xml",
        "/ueber-mich/": "/about/",
        "/datenschutz/": "/privacy/",
    }
    for old, new in paths.items():
        response = client.get("/me" + old, follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == "/me" + new
    assert client.get("/me/en/articles/secret/", follow_redirects=False).status_code == 404


def test_feed_sitemap_draft_isolation_and_headers(source):
    post(source, meta='slug: visible\ntranslationKey: pair\nexcerpt: "A & B ]]> </script>"')
    post(source, "en", "lang: en\nslug: hidden\ntranslationKey: pair\ndraft: true", "PRIVATE_DRAFT_MARKER")
    client = TestClient(create_app(source_dir=source))
    for route in ["/", "/articles/", "/tags/", "/rss.xml", "/sitemap.xml", "/articles/visible/"]:
        response = client.get(route)
        assert response.status_code == 200
        assert "PRIVATE_DRAFT_MARKER" not in response.text
        assert "/hidden/" not in response.text
        assert response.headers["x-content-type-options"] == "nosniff"
    assert "A &amp; B ]]&gt; &lt;/script&gt;" in client.get("/rss.xml").text
    assert "\\u003c/script>" in client.get("/articles/visible/").text
    assert client.get("/en/articles/hidden/").status_code == 404
    assert "<language>en</language>" in client.get("/en/rss.xml").text
    assert "/privacy/" in client.get("/sitemap.xml").text
    assert "/en/" not in client.get("/sitemap.xml").text


def test_export_uses_app_and_preserves_previous_output_on_invalid_content(source, tmp_path):
    post(source, meta="slug: article")
    dist = tmp_path / "dist"
    export_site(source, dist)
    before = (dist / "index.html").read_text()
    assert (dist / "articles/article/index.html").is_file()
    assert (dist / "404.html").is_file()
    assert "url=/about/" in (dist / "ueber-mich/index.html").read_text()
    assert 'data-static-export="true"' in before
    assert "hx-get=" not in before
    assert "/static/htmx.min.js" not in before
    assert (dist / "static/site.css").is_file()
    post(source, "bad", "slug: ../../bad")
    with pytest.raises(ContentError):
        export_site(source, dist)
    assert (dist / "index.html").read_text() == before


def test_markdown_keeps_tables_strikethrough_and_bare_links(source):
    post(source, body="| A | B |\n|---|---|\n| One | Two |\n\n~~before~~\n\nhttps://example.test/reference")
    html = str(load_content(source).posts[0].html)
    assert "<table>" in html
    assert "<s>before</s>" in html
    assert '<a href="https://example.test/reference">' in html


def test_missing_legacy_date_uses_file_mtime(source):
    file = source / "posts/legacy.md"
    file.write_text("---\ntitle: Legacy\n---\nExisting article.")
    assert load_content(source).posts[0].date


def test_history_restoration_and_filter_canonical(source):
    post(source, meta="slug: useful")
    client = TestClient(create_app(source_dir=source))
    restored = client.get("/?q=useful", headers={"HX-Request": "true", "HX-History-Restore-Request": "true"})
    assert "<html" in restored.text
    assert 'rel="canonical" href="https://example.test/"' in restored.text
    assert 'content="noindex,follow"' in restored.text
    assert client.get("/?tag=llm").text.count("/articles/useful/") == 1


def test_search_uses_visible_content_not_html_markup(source):
    post(
        source,
        meta="slug: visible",
        body='A & B\n\n[Source](https://example.test/reference)\n\n```python\nprint("hello")\n```',
    )
    client = TestClient(create_app(source_dir=source))
    for query in ["A & B", "print", "Source"]:
        assert (
            "/articles/visible/" in client.get("/", params={"q": query}, headers={"HX-Request": "true"}).text
        )
    for query in ["href", "language-python", "example.test/reference"]:
        assert (
            "/articles/visible/"
            not in client.get("/", params={"q": query}, headers={"HX-Request": "true"}).text
        )


def test_site_origin_rejects_attribute_injection(source):
    config_path = source / "config.json"
    config = json.loads(config_path.read_text())
    config["siteUrl"] = 'https://example.test" onload="alert(1)'
    config_path.write_text(json.dumps(config))
    with pytest.raises(ContentError, match="siteUrl"):
        load_content(source)


def test_head_matches_get_status_headers_without_body(source):
    post(source, meta="slug: article")
    client = TestClient(create_app(source_dir=source, base_path="/me"))
    for path in [
        "/me/",
        "/me/articles/article/",
        "/me/rss.xml",
        "/me/sitemap.xml",
        "/me/robots.txt",
        "/me/favicon.svg",
        "/me/healthz",
    ]:
        head = client.head(path)
        get = client.get(path)
        assert head.status_code == get.status_code == 200
        assert head.headers["content-type"] == get.headers["content-type"]
        assert head.headers["content-length"] == get.headers["content-length"]
        assert not head.content
    assert client.head("/me/missing/").status_code == 404


@pytest.mark.parametrize(
    "field,first,second",
    [("draft", "true", "false"), ("title", "Private", "Public"), ("slug", "private", "public")],
)
@pytest.mark.parametrize("syntax", ["yaml", "json"])
def test_duplicate_front_matter_keys_fail_closed(source, field, first, second, syntax):
    file = source / "posts/ambiguous.md"
    if syntax == "yaml":
        file.write_text(f"---\ndate: 2026-01-01\n{field}: {first}\n{field}: {second}\n---\nPRIVATE")
    else:
        a = first if field == "draft" else json.dumps(first)
        b = second if field == "draft" else json.dumps(second)
        file.write_text(f'---json\n{{"date":"2026-01-01","{field}":{a},"{field}":{b}}}\n---\nPRIVATE')
    with pytest.raises(ContentError, match="Duplicate metadata key"):
        load_content(source)


def test_export_rejects_input_directories_and_symlinks_without_changes(source, tmp_path):
    from blog.main import ROOT

    for directory in [ROOT / "blog/static", ROOT / "blog/templates", ROOT / "scripts"]:
        with pytest.raises(ValueError, match="overlap"):
            export_site(source, directory)
    target = tmp_path / "keep"
    target.mkdir()
    (target / "marker").write_text("keep")
    link = tmp_path / "output"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        export_site(source, link)
    assert (target / "marker").read_text() == "keep"
    assert link.is_symlink()
    file = tmp_path / "file"
    file.write_text("keep")
    with pytest.raises(ValueError, match="directory"):
        export_site(source, file)
    assert file.read_text() == "keep"


@pytest.mark.parametrize("timestamp", ["2026-01-01t23:30:00+02:00", "2026-01-01 23:30:00+02:00"])
def test_timestamp_keeps_time_and_timezone(source, timestamp):
    post(source, meta=f'date: "{timestamp}"')
    assert load_content(source).posts[0].date == "2026-01-01T23:30:00+02:00"


def test_large_responses_are_compressed_and_cache_varies_by_encoding(source):
    post(source, meta="slug: article", body="Useful content. " * 300)
    client = TestClient(create_app(source_dir=source))
    for route in ["/articles/article/", "/static/site.css", "/static/htmx.min.js"]:
        response = client.get(route, headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200
        assert response.headers.get("content-encoding") == "gzip"
        assert "Accept-Encoding" in response.headers["vary"]
        assert response.headers["x-content-type-options"] == "nosniff"
    assert "content-encoding" not in client.get("/healthz", headers={"Accept-Encoding": "gzip"}).headers


def test_german_content_never_leaks_into_any_public_surface(source, tmp_path):
    post(source, "german", "lang: de\nslug: geheim\ntags: [GEHEIM]", "GERMAN_PRIVATE_MARKER")
    post(source, "draft", "draft: true\nslug: draft", "DRAFT_PRIVATE_MARKER")
    client = TestClient(create_app(source_dir=source))
    for route in ["/", "/articles/", "/tags/", "/about/", "/privacy/", "/rss.xml", "/sitemap.xml"]:
        response = client.get(route)
        assert response.status_code == 200
        assert "GERMAN_PRIVATE_MARKER" not in response.text
        assert "DRAFT_PRIVATE_MARKER" not in response.text
        assert "GEHEIM" not in response.text
        assert 'lang="de"' not in response.text
    for route in ["/articles/geheim/", "/en/articles/geheim/", "/texte/geheim/", "/tags/geheim/"]:
        assert client.get(route).status_code == 404
    export_site(source, tmp_path / "dist")
    for path in (tmp_path / "dist").rglob("*.html"):
        assert "GERMAN_PRIVATE_MARKER" not in path.read_text()
        assert "DRAFT_PRIVATE_MARKER" not in path.read_text()
        assert 'lang="de"' not in path.read_text()


def test_inline_styles_are_csp_authorized_and_fonts_discovered_early(source):
    import base64
    import hashlib

    post(source, meta="slug: readable")
    client = TestClient(create_app(source_dir=source, base_path="/me"))
    for route in ["/", "/articles/", "/articles/readable/", "/about/", "/missing/"]:
        response = client.get("/me" + route)
        assert 'rel="stylesheet"' not in response.text
        styles = re.findall(r'<style[^>]*>(.*?)</style>', response.text, re.DOTALL)
        assert styles
        for style in styles:
            digest = base64.b64encode(hashlib.sha256(style.encode()).digest()).decode()
            assert f"'sha256-{digest}'" in response.headers["content-security-policy"]
        assert "unsafe-inline" not in response.headers["content-security-policy"]
        for font_url in re.findall(r"url\('([^']+)'\)", "".join(styles)):
            assert font_url.startswith("/me/static/fonts/")
            assert client.get(font_url).status_code == 200
        preloads = re.findall(r'<link rel="preload"[^>]*>', response.text)
        assert len(preloads) == (2 if route in ["/articles/readable/", "/about/"] else 1)
        assert all(client.get(re.search(r'href="([^"]+)"', link)[1]).status_code == 200 for link in preloads)


def test_security_headers_and_static_cache_fingerprints(source):
    import hashlib

    from blog.main import ROOT

    app = create_app(source_dir=source)
    http = TestClient(app)
    https = TestClient(app, base_url="https://example.test")
    for route in ["/", "/missing/", "/healthz", "/static/site.css"]:
        response = https.get(route)
        assert response.headers["strict-transport-security"] == "max-age=31536000"
        assert response.headers["cross-origin-opener-policy"] == "same-origin"
        # HSTS must survive TLS termination at the hosting proxy; HTTP clients ignore it.
        assert http.get(route).headers["strict-transport-security"] == "max-age=31536000"
    version = hashlib.sha256((ROOT / "blog/static/site.js").read_bytes()).hexdigest()[:12]
    path = f"/static/site.js?v={version}"
    response = http.get(path)
    assert "immutable" in response.headers["cache-control"]
    cached = http.get(path, headers={"If-None-Match": response.headers["etag"]})
    assert cached.status_code == 304
    assert "immutable" in cached.headers["cache-control"]
    for path in ["/static/site.js?v=old", "/static/site.js?anything=yes", "/static/absent.css?v=123"]:
        assert "immutable" not in http.get(path).headers["cache-control"]


def test_htmx_history_and_timeout_are_explicit(source):
    post(source)
    client = TestClient(create_app(source_dir=source))
    for route in ["/", "/articles/"]:
        page = client.get(route).text
        config = json.loads(re.search(r'name="htmx-config" content=\'(.*?)\'', page)[1])
        assert config["historyRestoreAsHxRequest"] is False
        assert 0 < config["timeout"] <= 15000
        assert config["allowEval"] is False
        assert config["allowScriptTags"] is False
        assert config["selfRequestsOnly"] is True


def test_discovery_is_public_only_and_exportable(source, tmp_path):
    post(source, meta='slug: visible\ntitle: "A [visible] article"')
    post(source, "secret", "slug: secret\ndraft: true", "PRIVATE_MARKER")
    post(source, "german", "slug: geheim\nlang: de", "GERMAN_MARKER")
    app = create_app(source_dir=source, base_path="/me")
    client = TestClient(app)
    llms = client.get("/me/llms.txt")
    assert llms.status_code == 200
    assert llms.headers["content-type"].startswith("text/plain")
    assert llms.text.startswith("# Example\n")
    assert "https://example.test/me/articles/visible/" in llms.text
    assert "https://example.test/me/about/" in llms.text
    for route in ["/.well-known/ai-catalog.json", "/.well-known/ard.json"]:
        response = client.get("/me" + route)
        assert response.status_code == 200
        catalog = response.json()
        assert catalog["specVersion"] == "1.0"
        assert catalog["entries"]
        for entry in catalog["entries"]:
            resource = client.get(urlsplit(entry["url"]).path)
            assert resource.status_code == 200
            assert resource.headers["content-type"].split(";")[0] == entry["type"]
        assert client.head("/me" + route).status_code == 200
        assert not client.head("/me" + route).content
        for private in ["secret", "geheim", "PRIVATE_MARKER", "GERMAN_MARKER"]:
            assert private not in response.text + llms.text
    page = client.get("/me/").text
    assert 'rel="describedby"' in page and 'href="/me/llms.txt"' in page
    assert 'rel="ai-catalog"' in page and 'rel="ard"' in page
    assert "Agentmap: https://example.test/me/.well-known/ard.json" in client.get("/me/robots.txt").text
    output = export_site(source, tmp_path / "out")
    assert (output / "llms.txt").is_file()
    assert json.loads((output / ".well-known/ai-catalog.json").read_text())["entries"]
    assert (output / ".well-known/ard.json").is_file()
    for file in [output / "llms.txt", output / ".well-known/ai-catalog.json"]:
        assert "secret" not in file.read_text()


def test_share_card_urls_change_when_pillow_renderer_changes(source, monkeypatch):
    import importlib

    import PIL

    from blog import social

    post(source, meta="slug: rendering")
    store = load_content(source)
    before = social.card_path(store.posts[0], store.config)
    try:
        with monkeypatch.context() as patch:
            patch.setattr(PIL, "__version__", "future-renderer-version")
            importlib.reload(social)
            assert social.card_path(store.posts[0], store.config) != before
    finally:
        importlib.reload(social)
