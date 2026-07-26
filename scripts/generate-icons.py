#!/usr/bin/env python3
"""Generate Today's Moon home-screen icons."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MOON_TEXTURE = ROOT / "moon.jpg"
BG = (2, 3, 8)


def draw_stars(draw: ImageDraw.ImageDraw, size: int, seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(55):
        x = rng.randint(0, size - 1)
        y = rng.randint(0, size - 1)
        b = rng.randint(130, 255)
        r = rng.choice([0, 0, 1])
        draw.point((x, y), fill=(b, b, min(255, b + 18)))


def render_moon(diameter: int, phase: float = 0.62) -> Image.Image:
    texture = Image.open(MOON_TEXTURE).convert("L")
    moon = ImageOps.fit(texture, (diameter, diameter), Image.Resampling.LANCZOS)
    moon_rgb = Image.merge("RGB", (moon, moon, moon))

    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    shaded = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    shaded.paste(moon_rgb, (0, 0), mask)

    radius = diameter / 2
    center = diameter / 2
    shadow = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    pixels = shadow.load()
    terminator = 1.0 - phase * 2.0

    for py in range(diameter):
        for px in range(diameter):
            dx = px - center + 0.5
            dy = py - center + 0.5
            if dx * dx + dy * dy > radius * radius:
                continue
            nx = dx / radius
            if nx < terminator:
                t = min(1.0, max(0.0, (terminator - nx) / 0.55))
                pixels[px, py] = (2, 3, 8, int(225 * t))

    return Image.alpha_composite(shaded, shadow)


def build_icon(size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw_stars(draw, size, 11)

    moon_size = int(size * 0.58)
    moon = render_moon(moon_size, phase=0.62)
    moon = moon.filter(ImageFilter.GaussianBlur(radius=0.25))
    top_left = ((size - moon_size) // 2, (size - moon_size) // 2)
    canvas.alpha_composite(moon, top_left)

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx = size // 2
    cy = size // 2
    r = moon_size // 2
    glow_draw.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=(200, 210, 230, 24))
    canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(radius=size // 40)))
    return canvas.convert("RGB")


def save_icons() -> None:
    icon_512 = build_icon(512)
    icon_512.save(ROOT / "icon-512.png", "PNG")
    icon_512.resize((180, 180), Image.Resampling.LANCZOS).save(ROOT / "apple-touch-icon.png", "PNG")
    print(f"Wrote icons in {ROOT}")


if __name__ == "__main__":
    save_icons()