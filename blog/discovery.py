"""Public discovery files and content-equivalent Markdown representations."""

import re
from urllib.parse import urlsplit

from blog.content import ContentStore, markdown_label


def wants_markdown(accept: str) -> bool:
    qualities = {}
    for media_range in accept.lower().split(","):
        name, *parameters = (part.strip() for part in media_range.split(";"))
        quality = "1"
        for parameter in parameters:
            key, _, value = parameter.partition("=")
            if key.strip() == "q":
                quality = value.strip()
                break
        if re.fullmatch(r"(?:0(?:\.\d{0,3})?|1(?:\.0{0,3})?)", quality):
            qualities[name] = max(qualities.get(name, 0), float(quality))
    markdown = qualities.get("text/markdown", 0)
    html = qualities.get("text/html", qualities.get("text/*", qualities.get("*/*", 0)))
    return markdown > 0 and markdown >= html


def render_document(data: dict, absolute) -> str:
    kind = data["page_type"]
    if kind == "page":
        return data["page"].markdown.strip("\n") + "\n"

    title = data["title"]
    lines = [f"# {markdown_label(title)}", ""]
    if kind == "post":
        post = data["post"]
        date = f"Published {post.date}"
        if post.updated != post.date:
            date += f" · Updated {post.updated}"
        lines.extend([
            markdown_label(post.excerpt), "", date, "",
            post.markdown.strip("\n"),
        ])
    elif kind == "tag_index":
        lines.extend(f"- [{markdown_label(tag['name'])}]({data['config']['siteUrl']}{tag['url']})"
                     for tag in data["tags"])
    else:
        lines.extend([markdown_label(data["description"]), ""])
        if kind == "home":
            lines.extend(["## Musings & Writings", ""])
        for post in data["posts"]:
            lines.append(f"- [{markdown_label(post.title)}]({absolute(post.url)}): {markdown_label(post.excerpt)}")
        if not data["posts"]:
            lines.append(data["labels"]["noResults"] if data["noindex"] else data["labels"]["empty"])

    about = data["config"]["siteUrl"] + data["about_url"]
    lines.extend(["", " · ".join([
        f"[Writing]({absolute('/articles/')})",
        f"[Topics]({absolute('/tags/')})",
        f"[About]({about})",
    ])])
    return "\n".join(lines) + "\n"


def render_llms(store: ContentStore, absolute, *, markdown_available: bool) -> str:
    markdown_note = (
        " The homepage, writing index, topic pages, About page and articles support `Accept: text/markdown`."
        if markdown_available else ""
    )
    lines = [
        f"# {markdown_label(store.config['siteTitle'])}", "",
        f"> {markdown_label(store.config.get('siteDescription', ''))}", "",
        ("Articles link to their sources where applicable." + markdown_note), "",
        "## Site", "",
        f"- [Writing]({absolute('/articles/')}): All public articles.",
        f"- [Topics]({absolute('/tags/')}): Browse articles by topic.",
        f"- [About]({absolute(store.about['en'].url)}): About this blog.",
        f"- [RSS]({absolute('/rss.xml')}): Article feed.",
        f"- [Sitemap]({absolute('/sitemap.xml')}): Canonical public URLs.", "",
        "## Articles", "",
    ]
    lines.extend(f"- [{markdown_label(post.title)}]({absolute(post.url)}): {markdown_label(post.excerpt)}" for post in store.posts)
    return "\n".join(lines) + "\n"


def render_catalog(store: ContentStore, absolute) -> dict:
    publisher = urlsplit(store.config["siteUrl"]).hostname
    resources = [
        ("overview", "Blog overview for LLMs", "text/plain", "/llms.txt",
         ["What does this blog cover?", "Where can I find a list of articles?"]),
        ("writing", "Writing", "text/html", "/articles/",
         ["Which articles cover AI agents?", "Find articles about software engineering"]),
        ("feed", "Article feed", "application/rss+xml", "/rss.xml",
         ["Where is the RSS feed?", "How can I follow new articles?"]),
        ("sitemap", "Public sitemap", "application/xml", "/sitemap.xml",
         ["Where is the blog sitemap?", "List the canonical public URLs on this blog"]),
    ]
    return {
        "specVersion": "1.0",
        "host": {"displayName": store.config["siteTitle"]},
        "entries": [
            {"identifier": f"urn:air:{publisher}:blog:{key}", "displayName": name,
             "type": media_type, "url": absolute(route), "representativeQueries": queries}
            for key, name, media_type, route, queries in resources
        ],
    }
