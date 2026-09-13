#!/usr/bin/env python3
"""Regenerate cream / Instagram-style social preview images for Dinesh AI Fund."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "hedge_fund" / "web" / "static"
DOCS = ROOT / "docs"
EXAMPLES = ROOT / "examples"
SOCIAL = EXAMPLES / "social-launch"

INTER = "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"
OUTFIT = "/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf"
if not Path(INTER).exists():
    INTER = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    OUTFIT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CREAM = (247, 241, 232, 255)
CREAM2 = (239, 230, 216, 255)
INK = (26, 21, 16, 255)
ORANGE = (255, 107, 0, 255)
WHITE = (255, 253, 249, 255)
MUTED = (92, 82, 72, 255)
SOFT = (138, 126, 114, 255)
SCREEN = (22, 17, 13, 255)
BULL = (31, 138, 76, 255)
BEAR = (198, 40, 40, 255)
AGENTS = [
    ("01", "Scout", "SCOUTED", "neutral"),
    ("02", "Tech", "HOLD", "neutral"),
    ("03", "Fund", "BUY", "bull"),
    ("04", "News", "BULLISH", "bull"),
    ("05", "Quant", "EDGE 56", "neutral"),
    ("06", "Risk", "APPROVE", "bull"),
    ("07", "PM", "HOLD", "neutral"),
]


def fnt(path: str, size: int):
    return ImageFont.truetype(path, size)


def paint_cream(img: Image.Image, w: int, h: int):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(255 - (255 - 239) * t * 0.35)
        g = int(248 - (248 - 230) * t * 0.35)
        b = int(240 - (240 - 216) * t * 0.4)
        draw.line((0, y, w, y), fill=(r, g, b, 255))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((-w * 0.1, -h * 0.35, w * 0.55, h * 0.45), fill=(255, 107, 0, 38))
    od.ellipse((w * 0.55, h * 0.55, w * 1.2, h * 1.25), fill=(255, 154, 60, 28))
    img.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(radius=w // 14)))


def draw_mark(draw, x, y, size):
    draw.rounded_rectangle((x, y, x + size, y + size), radius=int(size * 0.22), fill=ORANGE)
    f = fnt(OUTFIT, int(size * 0.44))
    text = "DA"
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (x + (size - tw) / 2 - bbox[0], y + (size - th) / 2 - bbox[1] - size * 0.03),
        text,
        font=f,
        fill=WHITE,
    )


def tone_color(tone: str):
    if tone == "bull":
        return BULL, (31, 138, 76, 40)
    if tone == "bear":
        return BEAR, (198, 40, 40, 40)
    return ORANGE, (255, 107, 0, 40)


def spark_points(seed: int, n: int = 10):
    pts = []
    v = 28 + seed % 7
    for i in range(n):
        v += ((seed * (i + 2)) % 7) - 3
        pts.append(max(8, min(44, v)))
    return pts


def draw_spark(draw, x, y, w, h, seed, color):
    pts = spark_points(seed)
    step = w / (len(pts) - 1)
    coords = []
    for i, p in enumerate(pts):
        coords.append((x + i * step, y + h - p))
    # area
    area = [(x, y + h)] + coords + [(x + w, y + h)]
    fill = (*color[:3], 50)
    draw.polygon(area, fill=fill)
    draw.line(coords, fill=color, width=2, joint="curve")


def draw_monitor(draw, box, num, name, label, tone, seed):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=SCREEN, outline=(255, 107, 0, 90), width=2)
    # traffic dots
    for i, c in enumerate([(255, 107, 0), (255, 154, 60), (61, 207, 122)]):
        draw.ellipse((x0 + 10 + i * 12, y0 + 10, x0 + 17 + i * 12, y0 + 17), fill=c)
    nf = fnt(INTER, 13)
    draw.text((x0 + 50, y0 + 8), f"{num} {name}", font=nf, fill=(255, 192, 137, 255))
    draw_spark(draw, x0 + 12, y0 + 30, x1 - x0 - 24, 36, seed, (61, 207, 122) if tone == "bull" else ((255, 90, 90) if tone == "bear" else (255, 154, 60)))
    tc, tbg = tone_color(tone)
    # pill
    pf = fnt(INTER, 11)
    bb = draw.textbbox((0, 0), label, font=pf)
    tw = bb[2] - bb[0] + 16
    th = bb[3] - bb[1] + 8
    px = x0 + 12
    py = y1 - th - 12
    draw.rounded_rectangle((px, py, px + tw, py + th), radius=999, fill=tbg)
    draw.text((px + 8, py + 3), label, font=pf, fill=tc)


def draw_combined(draw, box, wide=True):
    x0, y0, x1, y1 = box
    # gradient-ish dark panel with orange right edge simulation
    draw.rounded_rectangle(box, radius=18, fill=(26, 21, 16, 255), outline=ORANGE, width=3)
    # orange accent bar
    draw.rounded_rectangle((x1 - 18, y0 + 8, x1 - 6, y1 - 8), radius=8, fill=ORANGE)
    kicker = fnt(INTER, 14)
    title = fnt(OUTFIT, 28 if wide else 24)
    body = fnt(INTER, 15)
    draw.text((x0 + 22, y0 + 14), "COMBINED RESULT", font=kicker, fill=(255, 192, 137, 255))
    draw.text((x0 + 22, y0 + 36), "TSLA · HOLD / WATCH", font=title, fill=WHITE)
    draw.text((x0 + 22, y0 + 72), "edge 56.4  ·  win 63%  ·  ~5.8% paper alloc", font=body, fill=(232, 210, 188, 255))
    # badge
    bf = fnt(INTER, 14)
    label = "HOLD / WATCH"
    bb = draw.textbbox((0, 0), label, font=bf)
    tw, th = bb[2] - bb[0] + 24, bb[3] - bb[1] + 14
    bx = x1 - tw - 36
    by = y0 + (y1 - y0 - th) / 2
    draw.rounded_rectangle((bx, by, bx + tw, by + th), radius=12, fill=(255, 107, 0, 55), outline=(255, 200, 150, 180), width=1)
    draw.text((bx + 12, by + 5), label, font=bf, fill=ORANGE)


def make_og(w=1200, h=630):
    img = Image.new("RGBA", (w, h), CREAM)
    paint_cream(img, w, h)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_mark(draw, 56, 40, 56)
    brand = fnt(OUTFIT, 36)
    sub = fnt(INTER, 18)
    small = fnt(INTER, 14)
    draw.text((128, 44), "Dinesh AI Fund", font=brand, fill=INK)
    draw.text((128, 86), "Founded by Dineshgopi Sunkara", font=sub, fill=MUTED)

    # hero strip
    draw.rounded_rectangle((56, 128, w - 56, 210), radius=18, fill=WHITE, outline=(26, 21, 16, 28), width=1)
    draw.text((76, 142), "SAMPLE · TSLA", font=fnt(INTER, 13), fill=ORANGE)
    draw.text((76, 162), "Tesla, Inc.  $248.50  +2.35%", font=fnt(OUTFIT, 28), fill=INK)
    draw.rounded_rectangle((w - 250, 150, w - 76, 188), radius=12, fill=ORANGE)
    draw.text((w - 232, 158), "HOLD / WATCH", font=fnt(INTER, 16), fill=WHITE)

    # 7 monitor floors
    gap = 12
    left = 56
    right = w - 56
    usable = right - left
    card_w = (usable - gap * 6) / 7
    top = 230
    bottom = 390
    for i, (num, name, label, tone) in enumerate(AGENTS):
        x0 = left + i * (card_w + gap)
        draw_monitor(draw, (x0, top, x0 + card_w, bottom), num, name, label, tone, seed=11 + i * 3)

    # combined result
    draw_combined(draw, (56, 414, w - 56, 530), wide=True)

    draw.text(
        (56, 556),
        "Input ticker → 7 agent monitor floors → Combined Result memo   ·   Paper / research only · Not financial advice",
        font=small,
        fill=SOFT,
    )
    draw.text((56, 586), "Also: NVDA BUY · Risk REJECT (capital protection)", font=small, fill=MUTED)

    return img.convert("RGB")


def make_square(size=1080):
    img = Image.new("RGBA", (size, size), CREAM)
    paint_cream(img, size, size)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_mark(draw, 64, 56, 72)
    draw.text((156, 62), "Dinesh AI Fund", font=fnt(OUTFIT, 42), fill=INK)
    draw.text((156, 112), "Founded by Dineshgopi Sunkara", font=fnt(INTER, 20), fill=MUTED)

    draw.text((64, 170), "PRODUCT DEMO", font=fnt(INTER, 16), fill=ORANGE)
    draw.text((64, 198), "TSLA → 7 agents → memo", font=fnt(OUTFIT, 44), fill=INK)
    draw.text((64, 255), "Cream floors. Orange accents. Dark monitor panels.", font=fnt(INTER, 20), fill=MUTED)

    # hero
    draw.rounded_rectangle((64, 310, size - 64, 400), radius=20, fill=WHITE, outline=(26, 21, 16, 28), width=1)
    draw.text((88, 328), "TSLA  $248.50  +2.35%", font=fnt(OUTFIT, 32), fill=INK)
    draw.rounded_rectangle((size - 280, 340, size - 88, 378), radius=12, fill=ORANGE)
    draw.text((size - 262, 348), "HOLD / WATCH", font=fnt(INTER, 16), fill=WHITE)

    # monitors 2 rows: 4 + 3
    gap = 14
    left = 64
    usable = size - 128
    card_w = (usable - gap * 3) / 4
    top = 430
    bottom = 590
    for i, (num, name, label, tone) in enumerate(AGENTS[:4]):
        x0 = left + i * (card_w + gap)
        draw_monitor(draw, (x0, top, x0 + card_w, bottom), num, name, label, tone, seed=5 + i * 4)

    card_w2 = (usable - gap * 2) / 3
    top2 = 610
    bottom2 = 770
    for i, (num, name, label, tone) in enumerate(AGENTS[4:]):
        x0 = left + i * (card_w2 + gap)
        draw_monitor(draw, (x0, top2, x0 + card_w2, bottom2), num, name, label, tone, seed=21 + i * 5)

    draw_combined(draw, (64, 800, size - 64, 940), wide=False)

    draw.text(
        (64, 970),
        "Paper / research only · Not financial advice · No AUM claims",
        font=fnt(INTER, 18),
        fill=SOFT,
    )
    return img.convert("RGB")


def save_all(img_og: Image.Image, img_sq: Image.Image):
    for folder in (DOCS, STATIC, EXAMPLES, SOCIAL):
        folder.mkdir(parents=True, exist_ok=True)
        img_og.save(folder / "og-image.png", "PNG", optimize=True)
        img_sq.save(folder / "og-square.png", "PNG", optimize=True)
    print("wrote og-image.png + og-square.png to docs/, static/, examples/, social-launch/")


def main():
    og = make_og()
    sq = make_square()
    save_all(og, sq)


if __name__ == "__main__":
    main()
