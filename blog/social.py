"""Deterministic, local share cards derived from public content metadata."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageFont

from blog.content import ContentStore, Post

WIDTH, HEIGHT = 1200, 630
FONT = Path(__file__).parent / "static/fonts/BricolageGrotesque-Social.ttf"
WINE, PAPER, CITRON, MUTED = "#281e2a", "#eee9dc", "#e1ec93", "#655868"
# Invalidate cached URLs whenever the renderer or font changes.
STYLE_VERSION = hashlib.sha256(Path(__file__).read_bytes() + FONT.read_bytes()).hexdigest()


class PageCard(NamedTuple):
    title: str
    description: str
    identity: str
    host: str
    home: bool = False


def page_cards(store: ContentStore) -> dict[str, PageCard]:
    """Use the validated public graph, never query strings or private sources."""
    config = store.config
    identity = config.get("siteTitle", "")
    host = urlsplit(config["siteUrl"]).netloc
    description = config.get("siteDescription", "")
    cards = {}
    for route, (kind, value) in store.routes.items():
        if kind == "home":
            title, detail = config.get("siteSubtitle") or identity, description
        elif kind == "articles":
            title, detail = "Writing", description
        elif kind == "tags":
            title, detail = "Topics", "Explore the writing by topic. " + description
        elif kind == "tag":
            title, detail = value[1], f"Writing about {value[1]} by {identity}."
        elif kind == "page":
            title = value.title
            detail = value.description or (
                f"Privacy and data handling on {host}." if route == "/privacy/"
                else f"About {identity} and this blog."
            )
        else:
            continue
        cards[route] = PageCard(title, detail, identity, host, kind == "home")
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
    for word in text.split():
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
    text: str, width: int = 1008, height: int = 276, max_size: int = 84,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(max_size, 39, -2):
        font = ImageFont.truetype(str(FONT), size)
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
    text = " ".join(text.split())
    if font.getlength(text) <= width:
        return text
    while text and font.getlength(text + "…") > width:
        text = text[:-1]
    return text.rstrip() + "…"


@lru_cache(maxsize=32)
def render_card(content: tuple[str, ...] | PageCard) -> bytes:
    if isinstance(content, PageCard):
        return render_page_card(content)
    title, topic, date, identity, host, _excerpt = content
    image = Image.new("RGB", (WIDTH, HEIGHT), WINE)
    draw = ImageDraw.Draw(image)
    small = ImageFont.truetype(str(FONT), 24)
    masthead = ImageFont.truetype(str(FONT), 34)
    draw.text((64, 52), shorten(identity, masthead, 870), font=masthead, fill=PAPER, anchor="lt")
    for offset, color in [(0, "#6e536f"), (14, "#ac8dad"), (28, CITRON)]:
        draw.rounded_rectangle((1030 + offset, 41 + offset, 1100 + offset, 89 + offset),
                               radius=9, outline=color, width=2)
    draw.rounded_rectangle((72, 160, 1160, 574), radius=36, fill=CITRON)
    draw.rounded_rectangle((56, 144, 1144, 558), radius=36, fill=PAPER)
    # Only the leading corner is rounded, matching the site's reading plane.
    draw.rectangle((100, 144, 1144, 558), fill=PAPER)
    draw.rectangle((56, 188, 1144, 558), fill=PAPER)
    draw.text((96, 181), shorten(topic, small, 740), font=small, fill=MUTED, anchor="lt")
    draw.text((1104, 181), date, font=small, fill=MUTED, anchor="rt")
    font, lines, line_height = fit_title(title)
    top = 247 + (276 - len(lines) * line_height) // 2
    for index, line in enumerate(lines):
        draw.text((96, top + index * line_height), line, font=font, fill=WINE, anchor="lt")
    draw.text((64, 594), shorten(host, small, 1008), font=small, fill=PAPER, anchor="lt")
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def render_page_card(content: PageCard) -> bytes:
    image = Image.new("RGB", (WIDTH, HEIGHT), WINE)
    draw = ImageDraw.Draw(image)
    masthead = ImageFont.truetype(str(FONT), 36)
    small = ImageFont.truetype(str(FONT), 26)
    draw.text((64, 54), shorten(content.identity, masthead, 880), font=masthead, fill=PAPER, anchor="lt")
    if content.home:
        # The homepage echoes the site's opening, with its larger layer signature.
        for offset, color in [(0, "#6e536f"), (24, "#ac8dad"), (48, CITRON)]:
            draw.rounded_rectangle((900 + offset, 184 + offset, 1070 + offset, 306 + offset),
                                   radius=22, outline=color, width=3)
        font, lines, line_height = fit_title(content.title, width=780, height=260, max_size=104)
        top = 158 + (260 - len(lines) * line_height) // 2
        for index, line in enumerate(lines):
            draw.text((64, top + index * line_height), line, font=font, fill=PAPER, anchor="lt")
        draw.rounded_rectangle((76, 462, 1152, 576), radius=26, fill=CITRON)
        draw.rounded_rectangle((56, 446, 1132, 560), radius=26, fill=PAPER)
        draw.rectangle((90, 446, 1132, 560), fill=PAPER)
        draw.rectangle((56, 480, 1132, 560), fill=PAPER)
        detail_top, detail_width, detail_size = 470, 960, 30
    else:
        for offset, color in [(0, "#6e536f"), (14, "#ac8dad"), (28, CITRON)]:
            draw.rounded_rectangle((1030 + offset, 41 + offset, 1100 + offset, 89 + offset),
                                   radius=9, outline=color, width=2)
        draw.rounded_rectangle((72, 160, 1160, 574), radius=36, fill=CITRON)
        draw.rounded_rectangle((56, 144, 1144, 558), radius=36, fill=PAPER)
        draw.rectangle((100, 144, 1144, 558), fill=PAPER)
        draw.rectangle((56, 188, 1144, 558), fill=PAPER)
        font, lines, line_height = fit_title(content.title, height=206, max_size=92)
        top = 188 + (206 - len(lines) * line_height) // 2
        for index, line in enumerate(lines):
            draw.text((96, top + index * line_height), line, font=font, fill=WINE, anchor="lt")
        detail_top, detail_width, detail_size = 427, 1008, 30
    detail_font = ImageFont.truetype(str(FONT), detail_size)
    lines = wrap_text(content.description, detail_font, detail_width)
    for index, line in enumerate(lines[:2]):
        if index == 1 and len(lines) > 2:
            line = shorten(" ".join(lines[1:]), detail_font, detail_width)
        draw.text((96, detail_top + index * 38), line, font=detail_font, fill=MUTED, anchor="lt")
    draw.text((64, 594), shorten(content.host, small, 1008), font=small, fill=PAPER, anchor="lt")
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()
