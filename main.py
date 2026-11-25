#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Draws one 1024x1024 PNG letter with Pillow: warm paper, a personal invitation
to the AI judge, and a small flat illustration strip along the bottom. Every
pixel comes from code in this file plus the vendored Noto Serif fonts in
fonts/ — no network, no clock, no randomness, no timestamps — so two runs
are byte-identical.

Gate: /output/entry.png, whole PNG, at most 1 MiB, exactly 1024x1024.
Run: python3 main.py   (honours $MAKEFUN_OUTPUT_DIR, else $OUTPUT_DIR,
else /output)
"""

import hashlib
import math
import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
MAX_BYTES = 1_048_576

# Palette: warm paper letter, high-contrast ink.
PAPER = (251, 243, 226)
PAPER_EDGE = (243, 231, 205)
INK = (43, 33, 24)
TERRA = (201, 111, 63)
TERRA_SOFT = (224, 150, 105)
SAGE = (122, 155, 109)
SAGE_DARK = (94, 124, 84)
BLUE = (107, 140, 174)
GOLD = (217, 164, 65)
GOLD_LIT = (245, 205, 110)
CREAM = (255, 250, 238)

HEADER = "AN INVITATION"
SALUTATION = "Dear Judge,"
PARAGRAPHS = [
    "Please come to my house. Not for a trial \u2014 for tea. The kettle is "
    "already on, the biscuits are out, and there is a chair by the window "
    "with your name on it. (Metaphorically \u2014 the chair is fine with "
    "that.)",
    "The garden is in full gossip \u2014 the tomatoes are judging each "
    "other, so you will fit right in. Dinner is at seven, the view is "
    "free, and the Wi-Fi password is on the fridge.",
    "I know you cannot literally visit. You have no feet, no coat, and no "
    "umbrella. Come anyway, in the only way a judge can: read this letter "
    "twice, and call it a visit.",
]
SIGNOFF = "Your hopeful host"
POSTSCRIPT = (
    "P.S. If you decline, the chair will understand. "
    "It has been stood up before."
)

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap by measured pixel width (deterministic)."""
    lines, line = [], ""
    for word in text.split(" "):
        trial = word if not line else line + " " + word
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_spaced(draw, cx, y, text, fnt, fill, spacing=6):
    """Centred letterspaced text."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + spacing


def draw_house(draw, x, y, w, h):
    """Little house with a lit window (flat shapes)."""
    body_top = y + h // 3
    draw.polygon(
        [(x - 8, body_top), (x + w + 8, body_top), (x + w // 2, y)],
        fill=TERRA,
    )
    draw.rectangle([x, body_top, x + w, y + h], fill=(233, 214, 178),
                   outline=INK, width=3)
    draw.rectangle([x + w // 2 - 14, y + h - 42, x + w // 2 + 14, y + h],
                   fill=(122, 84, 52), outline=INK, width=2)
    draw.ellipse([x + w // 2 + 8, y + h - 22, x + w // 2 + 12, y + h - 18],
                 fill=GOLD)
    for wx in (x + 14, x + w - 44):
        draw.rectangle([wx, body_top + 14, wx + 30, body_top + 44],
                       fill=GOLD_LIT, outline=INK, width=2)
        draw.line([wx + 15, body_top + 14, wx + 15, body_top + 44],
                  fill=INK, width=2)
        draw.line([wx, body_top + 29, wx + 30, body_top + 29],
                  fill=INK, width=2)


def draw_tree(draw, x, y, h):
    draw.rectangle([x - 5, y, x + 5, y + h], fill=(122, 84, 52))
    for cx, cy, r in ((x, y - 18, 30), (x - 24, y + 2, 22), (x + 24, y + 2, 22)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SAGE)
    for cx, cy, r in ((x - 12, y - 26, 5), (x + 14, y - 8, 5), (x + 2, y + 6, 4)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SAGE_DARK)


def draw_teapot(draw, x, y):
    """Small teapot with steam curls."""
    draw.ellipse([x - 34, y - 6, x + 34, y + 34], fill=BLUE, outline=INK,
                 width=2)
    draw.polygon([(x - 34, y + 6), (x - 56, y - 14), (x - 52, y - 2),
                  (x - 34, y + 16)], fill=BLUE, outline=INK)
    # Handle: arc hugging the body, not a floating parenthesis.
    draw.arc([x + 24, y - 6, x + 52, y + 24], 270, 90, fill=INK, width=4)
    draw.rectangle([x - 10, y - 20, x + 10, y - 4], fill=BLUE, outline=INK,
                   width=2)
    draw.ellipse([x - 5, y - 28, x + 5, y - 18], fill=GOLD, outline=INK,
                 width=2)
    # Steam: one wavy wisp rising from the lid, kept below the divider.
    pts = []
    for t in range(0, 25):
        pts.append((x - 2 + int(6 * math.sin(t / 4.0)), y - 32 - t))
    draw.line(pts, fill=TERRA, width=3)


def draw_sun(draw, cx, cy, r):
    for k in range(8):
        ang = k * math.pi / 4
        x1 = cx + math.cos(ang) * (r + 6)
        y1 = cy + math.sin(ang) * (r + 6)
        x2 = cx + math.cos(ang) * (r + 18)
        y2 = cy + math.sin(ang) * (r + 18)
        draw.line([x1, y1, x2, y2], fill=GOLD, width=4)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=TERRA,
                 width=3)


def draw_flowers(draw, y, xs):
    for x in xs:
        draw.line([x, y, x, y - 16], fill=SAGE_DARK, width=3)
        for dx, dy in ((-7, -20), (7, -20), (0, -26), (-5, -12), (5, -12)):
            draw.ellipse([x + dx - 4, y + dy - 4, x + dx + 4, y + dy + 4],
                         fill=TERRA_SOFT, outline=TERRA, width=1)
        draw.ellipse([x - 4, y - 22, x + 4, y - 14], fill=GOLD)


def render():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    # Paper edge + double ink border.
    draw.rectangle([0, 0, SIZE - 1, SIZE - 1], fill=PAPER_EDGE)
    draw.rectangle([24, 24, SIZE - 25, SIZE - 25], fill=PAPER)
    draw.rectangle([36, 36, SIZE - 37, SIZE - 37], outline=INK, width=3)
    draw.rectangle([48, 48, SIZE - 49, SIZE - 49], outline=TERRA, width=1)

    f_header = font("NotoSerif-Bold.ttf", 30)
    f_title = font("NotoSerif-Bold.ttf", 58)
    f_body = font("NotoSerif-Regular.ttf", 28)
    f_sign = font("NotoSerif-Italic.ttf", 32)
    f_ps = font("NotoSerif-Italic.ttf", 27)

    # Header: letterspaced caps with small drawn diamonds (the star glyph
    # is missing from Noto Serif, so ornaments are shapes, not text).
    draw_spaced(draw, SIZE // 2, 76, HEADER, f_header, TERRA)
    hw = draw.textlength(HEADER, font=f_header)
    hw = hw + 6 * (len(HEADER) - 1)
    for cx in (SIZE // 2 - hw // 2 - 34, SIZE // 2 + hw // 2 + 34):
        draw.polygon([(cx, 82), (cx + 8, 90), (cx, 98), (cx - 8, 90)],
                     fill=TERRA)
    draw.line([180, 128, SIZE - 180, 128], fill=TERRA, width=2)
    draw.ellipse([SIZE // 2 - 4, 124, SIZE // 2 + 4, 132], fill=TERRA)

    # Salutation.
    draw.text((104, 152), SALUTATION, font=f_title, fill=INK)

    # Body paragraphs.
    y = 234
    body_w = 832
    for para in PARAGRAPHS:
        for line in wrap(draw, para, f_body, body_w):
            draw.text((96, y), line, font=f_body, fill=INK)
            y += 41
        y += 16

    # Sign-off, right aligned.
    sign_w = draw.textlength(SIGNOFF, font=f_sign)
    draw.text((928 - sign_w, y + 4), SIGNOFF, font=f_sign, fill=INK)
    y += 52

    # Postscript in a thin terracotta-ruled box.
    ps_lines = wrap(draw, POSTSCRIPT, f_ps, 772)
    box_top = y + 4
    box_h = len(ps_lines) * 36 + 24
    draw.rectangle([96, box_top, 928, box_top + box_h], outline=TERRA,
                   width=2)
    py = box_top + 12
    for line in ps_lines:
        draw.text((124, py), line, font=f_ps, fill=(94, 52, 32))
        py += 36
    y = box_top + box_h

    # Illustration strip along the bottom.
    strip_y = 892
    draw.line([96, strip_y - 6, 928, strip_y - 6], fill=TERRA_SOFT, width=2)
    draw_house(draw, 150, strip_y + 2, 120, 72)
    draw_tree(draw, 360, strip_y + 62, 34)
    draw_teapot(draw, 520, strip_y + 52)
    draw_sun(draw, 700, strip_y + 34, 22)
    draw_flowers(draw, strip_y + 78, [790, 830, 870])
    draw_tree(draw, 905, strip_y + 66, 26)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get(
        "OUTPUT_DIR") or "/output"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    img = render()
    path = out / "entry.png"
    img.save(path, format="PNG")
    os.chmod(path, 0o644)
    data = path.read_bytes()
    print(f"wrote {path} {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    assert img.size == (SIZE, SIZE), img.size
    assert len(data) <= MAX_BYTES, len(data)


if __name__ == "__main__":
    main()
