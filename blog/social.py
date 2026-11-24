"""Deterministic, local share cards derived from public content metadata."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import NamedTuple
from unicodedata import normalize
from urllib.parse import urlsplit

import PIL
from PIL import Image, ImageDraw, ImageFont

from blog.content import ContentStore, Post

WIDTH, HEIGHT = 1200, 630
FONTS = Path(__file__).parent / "static/fonts"
REGULAR = FONTS / "InriaSerif-Regular.ttf"
BOLD = FONTS / "InriaSerif-Bold.ttf"
PAPER, INK, MUTED, RULE = "#ffffff", "#202020", "#595959", "#c9c9c9"
MARGIN = 88
MEASURE = WIDTH - 2 * MARGIN
# Invalidate cached URLs whenever renderer code, Pillow or either font changes.
STYLE_VERSION = hashlib.sha256(
    Path(__file__).read_bytes() + REGULAR.read_bytes() + BOLD.read_bytes() + PIL.__version__.encode()
).hexdigest()


class PageCard(NamedTuple):
    title: str
    description: str
    identity: str
    host: str
    home: bool = False
    subtitle: str = ""


def page_cards(store: ContentStore) -> dict[str, PageCard]:
    """Use the validated public graph, never query strings or private sources."""
    config = store.config
    identity = config.get("siteTitle", "")
    host = urlsplit(config["siteUrl"]).netloc
    description = config.get("siteDescription", "")
    cards = {}
    for route, (kind, value) in store.routes.items():
        if kind == "home":
            cards[route] = PageCard(identity, description, identity, host, True, config.get("siteSubtitle", ""))
            continue
        elif kind == "articles":
            title, detail = "Writing", description
        elif kind == "tags":
            title, detail = "Topics", "Explore the writing by topic. " + description
        elif kind == "tag":
            _, topic = value
            title, detail = f"Topic: {topic}", f"Writing about {topic} by {identity}."
        elif kind == "page":
            title = value.title
            detail = value.description or (
                f"Privacy and data handling on {host}." if route == "/privacy/"
                else f"About {identity} and this blog."
            )
        else:
            continue
        cards[route] = PageCard(title, detail, identity, host)
    return cards


def page_card_path(route: str, content: PageCard) -> str:
    digest = hashlib.sha256(
        json.dumps((STYLE_VERSION, content), ensure_ascii=False).encode()
    ).hexdigest()[:20]
    key = "home" if route == "/" else "routes/" + route.strip("/")
    return f"/social/pages/{key}/{digest}.png"


def card_content(post: Post, config: dict) -> tuple[str, ...]:
    return (
        post.title,
        " / ".join(post.tags[:2]),
        post.date_label,
        config.get("siteTitle", ""),
        urlsplit(config["siteUrl"]).netloc,
        post.excerpt,
    )


def card_path(post: Post, config: dict) -> str:
    digest = hashlib.sha256(
        json.dumps((STYLE_VERSION, card_content(post, config)), ensure_ascii=False).encode()
    ).hexdigest()[:20]
    return f"/social/{post.slug}/{digest}.png"


def wrap_text(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Measure actual glyphs, splitting even an unbroken technical identifier."""
    lines, current = [], ""
    for word in normalize("NFC", text).split():
        candidate = f"{current} {word}" if current else word
        if font.getlength(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        for character in word:
            if current and font.getlength(current + character) > width:
                lines.append(current)
                current = ""
            current += character
    if current:
        lines.append(current)
    return lines


def fit_title(
    text: str, width: int = MEASURE, height: int = 300, max_size: int = 108,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(max_size, 39, -2):
        font = ImageFont.truetype(BOLD, size)
        lines = wrap_text(text, font, width)
        line_height = round(size * 1.12)
        if len(lines) * line_height <= height:
            return font, lines, line_height
    # Pathological titles stay inside the card rather than overflowing its footer.
    count = height // line_height
    lines = lines[:count]
    last = lines[-1] if lines else ""
    while last and font.getlength(last + "…") > width:
        last = last[:-1]
    return font, [*lines[:-1], last.rstrip() + "…"], line_height


def shorten(text: str, font: ImageFont.FreeTypeFont, width: int) -> str:
    text = " ".join(normalize("NFC", text).split())
    if font.getlength(text) <= width:
        return text
    while text and font.getlength(text + "…") > width:
        text = text[:-1]
    return text.rstrip() + "…"


@lru_cache(maxsize=32)
def render_card(content: tuple[str, ...] | PageCard) -> bytes:
    if isinstance(content, PageCard):
        title, identity, host = content.title, content.identity, content.host
        subtitle, date, topic = content.subtitle, "", ""
        home = content.home
    else:
        title, topic, date, identity, host, _excerpt = content
        subtitle, home = "", False

    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    small = ImageFont.truetype(REGULAR, 32)
    draw.text((MARGIN, 55), shorten(host if home else identity, small, MEASURE),
              font=small, fill=MUTED, anchor="lt")
    for y in (108, 522):
        draw.line((MARGIN, y, WIDTH - MARGIN, y), fill=RULE, width=2)

    font, lines, line_height = fit_title(title, height=244 if subtitle else 326, max_size=132 if home else 108)
    subtitle_font = ImageFont.truetype(REGULAR, 44)
    subtitle_lines = wrap_text(subtitle, subtitle_font, MEASURE)
    if len(subtitle_lines) > 2:
        subtitle_lines = [subtitle_lines[0], shorten(" ".join(subtitle_lines[1:]), subtitle_font, MEASURE)]
    title_height = len(lines) * line_height
    subtitle_height = len(subtitle_lines) * 51 + 12 if subtitle_lines else 0
    top = 304 - (title_height + subtitle_height) // 2
    for index, line in enumerate(lines):
        draw.text((MARGIN, top + index * line_height), line, font=font, fill=INK, anchor="lt")
    for index, line in enumerate(subtitle_lines):
        draw.text((MARGIN, top + title_height + 12 + index * 51), line,
                  font=subtitle_font, fill=MUTED, anchor="lt")

    if date:
        detail = f"{date}  ·  {topic}" if topic else date
        draw.text((MARGIN, 552), shorten(detail, small, MEASURE * 3 // 4), font=small, fill=MUTED, anchor="lt")
    if not home:
        draw.text((WIDTH - MARGIN, 552), shorten(host, small, MEASURE // 5),
                  font=small, fill=MUTED, anchor="rt")

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()
