#!/usr/bin/env python3
"""Regenerate social preview images for Dinesh AI Fund."""

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

CREAM = (255, 248, 240, 255)
INK = (26, 21, 16, 255)
ORANGE = (255, 107, 0, 255)
WHITE = (255, 255, 255, 255)
CHIP_BG = (58, 36, 20, 255)
MUTED = (232, 210, 188, 255)
SOFT = (190, 168, 148, 255)
PANEL = (42, 28, 18, 230)
AGENTS = ["01 Scout", "02 Tech", "03 Fund", "04 News", "05 Quant", "06 Risk", "07 PM"]


def fnt(path: str, size: int):
    return ImageFont.truetype(path, size)


def paint_dark(img, w, h):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(26 + (58 - 26) * t)
        g = int(21 + (36 - 21) * t)
        b = int(16 + (20 - 16) * t)
        draw.line((0, y, w, y), fill=(r, g, b, 255))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((w * 0.45, -h * 0.25, w * 1.15, h * 0.55), fill=(255, 107, 0, 70))
    od.ellipse((-w * 0.2, h * 0.55, w * 0.5, h * 1.2), fill=(255, 140, 40, 40))
    img.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(radius=w // 18)))


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


def measure(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1], b


def draw_chips(draw, agents, y, canvas_w, font, pad_x=22, pad_y=14, gap=12, row_gap=14):
    sizes = []
    for name in agents:
        tw, th, b = measure(draw, name, font)
        sizes.append((name, tw + pad_x * 2, th + pad_y * 2, b, tw, th))
    rows, row, used = [], [], 0
    max_w = canvas_w - 160
    for item in sizes:
        w = item[1]
        extra = 0 if not row else gap
        if row and used + extra + w > max_w:
            rows.append(row)
            row, used = [item], w
        else:
            used += extra + w
            row.append(item)
    if row:
        rows.append(row)
    cy = y
    for row in rows:
        total = sum(i[1] for i in row) + gap * (len(row) - 1)
        cx = (canvas_w - total) / 2
        rh = max(i[2] for i in row)
        for name, cw, ch, b, tw, th in row:
            draw.rounded_rectangle((cx, cy, cx + cw, cy + rh), radius=rh / 2, fill=CHIP_BG)
            draw.text((cx + (cw - tw) / 2 - b[0], cy + (rh - th) / 2 - b[1]), name, font=font, fill=CREAM)
            cx += cw + gap
        cy += rh + row_gap
    return cy


def draw_sample_panel(draw, x, y, w, h, scale=1):
    """Mini sample callout: Sample: TSLA → 7 agents → HOLD/WATCH memo"""
    draw.rounded_rectangle((x, y, x + w, y + h), radius=int(28 * scale), fill=PANEL)
    draw.rounded_rectangle(
        (x + int(8 * scale), y + int(8 * scale), x + w - int(8 * scale), y + h - int(8 * scale)),
        radius=int(22 * scale),
        outline=(255, 107, 0, 120),
        width=max(2, int(3 * scale)),
    )
    title_f = fnt(INTER, int(22 * scale))
    body_f = fnt(OUTFIT, int(34 * scale))
    sub_f = fnt(INTER, int(22 * scale))
    draw.text((x + int(28 * scale), y + int(22 * scale)), "SAMPLE EXAMPLE", font=title_f, fill=ORANGE)
    draw.text((x + int(28 * scale), y + int(58 * scale)), "TSLA  →  7 agents  →  HOLD / WATCH memo", font=body_f, fill=CREAM)
    draw.text(
        (x + int(28 * scale), y + int(108 * scale)),
        "Also: NVDA BUY · Risk REJECT (capital protection)",
        font=sub_f,
        fill=MUTED,
    )


def make_landscape(path: Path):
    s = 2
    w, h = 1200 * s, 630 * s
    img = Image.new("RGBA", (w, h), INK)
    paint_dark(img, w, h)
    d = ImageDraw.Draw(img, "RGBA")
    mark = 110
    draw_mark(d, 96, 70, mark)
    d.text((96 + mark + 28, 82), "SEVEN-AGENT RESEARCH FLOOR", font=fnt(INTER, 26), fill=ORANGE)
    d.text((96 + mark + 28, 120), "Dinesh AI Fund", font=fnt(OUTFIT, 86), fill=CREAM)
    d.text((96, 250), "Founded by Dineshgopi Sunkara", font=fnt(OUTFIT, 36), fill=CREAM)
    d.text(
        (96, 300),
        "Open educational research — paper only, never live trading.",
        font=fnt(INTER, 30),
        fill=MUTED,
    )
    draw_chips(d, AGENTS, 360, w, fnt(INTER, 24), pad_x=20, pad_y=12)
    # Canvas is 2x; scale=2 keeps panel typography crisp inside ~300px tall box
    draw_sample_panel(d, 96, 455, w - 192, 300, scale=2)
    d.text(
        (96, h - 70),
        "Not financial advice  ·  No AUM or return claims  ·  Demo scores are simulated",
        font=fnt(INTER, 24),
        fill=SOFT,
    )
    img.resize((1200, 630), Image.Resampling.LANCZOS).convert("RGB").save(path, "PNG", optimize=True)


def make_square(path: Path):
    s = 2
    w = h = 1080 * s
    img = Image.new("RGBA", (w, h), INK)
    paint_dark(img, w, h)
    d = ImageDraw.Draw(img, "RGBA")
    mark = 150
    draw_mark(d, (w - mark) // 2, 120, mark)
    text = "SEVEN-AGENT RESEARCH FLOOR"
    tw, th, b = measure(d, text, fnt(INTER, 28))
    d.text(((w - tw) / 2 - b[0], 310), text, font=fnt(INTER, 28), fill=ORANGE)
    text = "Dinesh AI Fund"
    tw, th, b = measure(d, text, fnt(OUTFIT, 88))
    d.text(((w - tw) / 2 - b[0], 360), text, font=fnt(OUTFIT, 88), fill=CREAM)
    text = "Founded by Dineshgopi Sunkara"
    tw, th, b = measure(d, text, fnt(OUTFIT, 36))
    d.text(((w - tw) / 2 - b[0], 470), text, font=fnt(OUTFIT, 36), fill=CREAM)
    text = "Paper research only  ·  Not live trading"
    tw, th, b = measure(d, text, fnt(INTER, 30))
    d.text(((w - tw) / 2 - b[0], 530), text, font=fnt(INTER, 30), fill=MUTED)
    draw_chips(d, AGENTS, 610, w, fnt(INTER, 26), pad_x=20, pad_y=12)
    panel_w = w - 220
    panel_h = 320
    draw_sample_panel(d, (w - panel_w) // 2, 820, panel_w, panel_h, scale=2)
    text = "Not financial advice  ·  Demo scores are simulated"
    tw, th, b = measure(d, text, fnt(INTER, 24))
    d.text(((w - tw) / 2 - b[0], h - 90), text, font=fnt(INTER, 24), fill=SOFT)
    img.resize((1080, 1080), Image.Resampling.LANCZOS).convert("RGB").save(path, "PNG", optimize=True)


def make_icon(path: Path, size: int):
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((0, 0, s, s), radius=int(s * 0.22), fill=ORANGE)
    f = fnt(OUTFIT, int(s * 0.44))
    text = "DA"
    b = d.textbbox((0, 0), text, font=f)
    tw, th = b[2] - b[0], b[3] - b[1]
    d.text(((s - tw) / 2 - b[0], (s - th) / 2 - b[1] - s * 0.03), text, font=f, fill=WHITE)
    img.resize((size, size), Image.Resampling.LANCZOS).save(path, "PNG", optimize=True)


def sync_copies(name: str, src: Path) -> None:
    data = src.read_bytes()
    for dest_dir in (DOCS, EXAMPLES, SOCIAL):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / name).write_bytes(data)


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    SOCIAL.mkdir(parents=True, exist_ok=True)
    make_landscape(STATIC / "og-image.png")
    make_square(STATIC / "og-square.png")
    make_icon(STATIC / "favicon.png", 32)
    make_icon(STATIC / "apple-touch-icon.png", 180)
    for name in ("og-image.png", "og-square.png", "favicon.png", "apple-touch-icon.png"):
        sync_copies(name, STATIC / name)
    print("wrote social images to", STATIC, DOCS, EXAMPLES, SOCIAL)


if __name__ == "__main__":
    main()
