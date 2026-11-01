"""Deterministic, local share cards derived from public article metadata."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

import PIL
from PIL import Image, ImageDraw, ImageFont

from blog.content import Post

WIDTH, HEIGHT = 1200, 630
FONT = Path(__file__).parent / "static/fonts/BricolageGrotesque-Social.ttf"
WINE, PAPER, CITRON, MUTED = "#281e2a", "#eee9dc", "#e1ec93", "#655868"
# Invalidate cached URLs whenever renderer code, Pillow or the font changes.
STYLE_VERSION = hashlib.sha256(
    Path(__file__).read_bytes() + FONT.read_bytes() + PIL.__version__.encode()
).hexdigest()


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


def fit_title(text: str) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(84, 39, -2):
        font = ImageFont.truetype(str(FONT), size)
        lines = wrap_text(text, font, 1008)
        line_height = round(size * 1.12)
        if len(lines) * line_height <= 276:
            return font, lines, line_height
    # Pathological titles stay inside the card rather than overflowing its footer.
    count = 276 // line_height
    lines = lines[:count]
    last = lines[-1] if lines else ""
    while last and font.getlength(last + "…") > 1008:
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
def render_card(content: tuple[str, ...]) -> bytes:
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
