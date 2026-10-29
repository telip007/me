import json
import re

import pytest
from fastapi.testclient import TestClient

from blog.content import ContentError, load_content
from blog.export import export_site
from blog.main import create_app


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
                "siteSubtitle": "Deutsch",
                "siteDescription": "Beschreibung",
                "author": "Example",
                "locales": {"en": {"siteSubtitle": "English", "siteDescription": "Description"}},
            }
        )
    )
    (src / "about.md").write_text("---\ntitle: Über diesen Blog\nslug: ueber-mich\n---\n# Deutsch")
    (src / "about.en.md").write_text("---\ntitle: About this blog\nslug: about\n---\n# English")
    (src / "datenschutz.md").write_text("# Datenschutz\n\nBestehender Rechtstext.")
    (src / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    return src


def post(source, name="de", meta="", body="A useful article."):
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
        meta="slug: modelle\ntranslationKey: models",
        body="## A heading\n\n<script>alert(1)</script>\n\n[Bad](javascript:alert(1))",
    )
    post(source, "en", "lang: en\nslug: models\ntranslationKey: models")
    store = load_content(source)
    german, english = store.posts
    assert german.url == "/texte/modelle/"
    assert english.url == "/en/articles/models/"
    assert german.alternates == {"de": german.url, "en": english.url}
    assert "<script>" not in german.html
    assert 'href="javascript:' not in german.html
    assert '<h2 id="a-heading">' in german.html
    assert german.toc[0]["id"] == "a-heading"


def test_drafts_future_dates_and_metadata_validation(source):
    post(source, meta="slug: visible\ntranslationKey: pair\ndate: '2030-01-01'")
    post(source, "en", "lang: en\nslug: secret\ntranslationKey: pair\ndraft: true", "PRIVATE_DRAFT_MARKER")
    store = load_content(source)
    assert len(store.posts) == 1
    assert store.posts[0].alternates == {"de": "/texte/visible/"}
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
    post(source, meta="slug: modelle\ntranslationKey: models")
    post(source, "en", "lang: en\nslug: models\ntranslationKey: models")
    client = TestClient(create_app(source_dir=source, base_path="/me"))
    home = client.get("/me/")
    assert home.status_code == 200
    assert '<html lang="de"' in home.text
    assert 'href="/me/ueber-mich/"' in home.text
    english = client.get("/me/en/articles/models/")
    assert 'hreflang="de" href="https://example.test/me/texte/modelle/"' in english.text
    assert 'rel="canonical" href="https://example.test/me/en/articles/models/"' in english.text
    fragment = client.get("/me/?q=missing", headers={"HX-Request": "true"})
    assert fragment.status_code == 200
    assert "<html" not in fragment.text
    assert "de" not in fragment.text or "modelle/" not in fragment.text
    assert "HX-Request" in fragment.headers["vary"]
    full = client.get("/me/?q=missing")
    assert "<html" in full.text
    assert "modelle/" not in full.text
    assert client.get("/me/about/", follow_redirects=False).headers["location"] == "/me/ueber-mich/"
    assert client.get("/me/archive/").status_code == 404
    assert 'lang="en"' in client.get("/me/en/not-found/").text
    assert "Bestehender Rechtstext." in client.get("/me/datenschutz/").text
    assert "Privacy (German)" in client.get("/me/en/").text


def test_feed_sitemap_draft_isolation_and_headers(source):
    post(source, meta='slug: visible\ntranslationKey: pair\nexcerpt: "A & B ]]> </script>"')
    post(source, "en", "lang: en\nslug: hidden\ntranslationKey: pair\ndraft: true", "PRIVATE_DRAFT_MARKER")
    client = TestClient(create_app(source_dir=source))
    for route in ["/", "/en/", "/rss.xml", "/en/rss.xml", "/sitemap.xml", "/texte/visible/"]:
        response = client.get(route)
        assert response.status_code == 200
        assert "PRIVATE_DRAFT_MARKER" not in response.text
        assert "/hidden/" not in response.text
        assert response.headers["x-content-type-options"] == "nosniff"
    assert "A &amp; B ]]&gt; &lt;/script&gt;" in client.get("/rss.xml").text
    assert "\\u003c/script>" in client.get("/texte/visible/").text
    assert client.get("/en/articles/hidden/").status_code == 404
    assert "<language>en</language>" in client.get("/en/rss.xml").text
    assert "/datenschutz/" in client.get("/sitemap.xml").text


def test_export_uses_app_and_preserves_previous_output_on_invalid_content(source, tmp_path):
    post(source, meta="slug: article")
    dist = tmp_path / "dist"
    export_site(source, dist)
    before = (dist / "index.html").read_text()
    assert (dist / "texte/article/index.html").is_file()
    assert (dist / "404.html").is_file()
    assert "url=/ueber-mich/" in (dist / "about/index.html").read_text()
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
    assert client.get("/?tag=llm").text.count("/texte/useful/") == 1


def test_search_uses_visible_content_not_html_markup(source):
    post(
        source,
        meta="slug: visible",
        body='A & B\n\n[Source](https://example.test/reference)\n\n```python\nprint("hello")\n```',
    )
    client = TestClient(create_app(source_dir=source))
    for query in ["A & B", "print", "Source"]:
        assert "/texte/visible/" in client.get("/", params={"q": query}, headers={"HX-Request": "true"}).text
    for query in ["href", "language-python", "example.test/reference"]:
        assert (
            "/texte/visible/" not in client.get("/", params={"q": query}, headers={"HX-Request": "true"}).text
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
        "/me/texte/article/",
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
    for route in ["/texte/article/", "/static/site.css", "/static/htmx.min.js"]:
        response = client.get(route, headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200
        assert response.headers.get("content-encoding") == "gzip"
        assert "Accept-Encoding" in response.headers["vary"]
        assert response.headers["x-content-type-options"] == "nosniff"
    assert "content-encoding" not in client.get("/healthz", headers={"Accept-Encoding": "gzip"}).headers
