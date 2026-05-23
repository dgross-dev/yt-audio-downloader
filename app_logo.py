# Logo wird programmatisch zur Laufzeit gezeichnet —
# keine externe PNG/SVG-Datei nötig, alles im Code.
from __future__ import annotations

from PIL import Image, ImageDraw


def _radial_gradient_circle(size: int, inner: tuple, outer: tuple) -> Image.Image:
    """Kreis mit Radial-Gradient. Wir zeichnen konzentrische Kreise von außen
    nach innen — schneller als per-pixel und sieht bei dieser Größe gleich gut aus."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = size / 2
    max_r = size / 2

    steps = int(max_r)
    for i in range(steps, 0, -1):
        t = i / steps                # 1 außen, 0 innen
        t = t * t * (3 - 2 * t)      # smoothstep
        color = (
            int(inner[0] + (outer[0] - inner[0]) * t),
            int(inner[1] + (outer[1] - inner[1]) * t),
            int(inner[2] + (outer[2] - inner[2]) * t),
            255,
        )
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color)

    return img


def make_logo(size: int = 128) -> Image.Image:
    """Erzeugt das App-Logo: blauer Kreis mit Musiknote und Download-Akzent."""
    # 4x supersampling für glattere Kanten
    scale = 4
    s = size * scale

    bg = _radial_gradient_circle(s, inner=(80, 145, 255), outer=(45, 70, 180))
    draw = ImageDraw.Draw(bg)

    # Notenkopf (schräggestellte Ellipse, via separater Ebene + Rotation)
    note_color = (255, 255, 255, 255)
    head_w = int(s * 0.32)
    head_h = int(s * 0.24)
    head_cx = int(s * 0.40)
    head_cy = int(s * 0.66)

    head_layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(head_layer).ellipse(
        [head_cx - head_w // 2, head_cy - head_h // 2,
         head_cx + head_w // 2, head_cy + head_h // 2],
        fill=note_color,
    )
    head_layer = head_layer.rotate(-18, resample=Image.BICUBIC, center=(head_cx, head_cy))
    bg.alpha_composite(head_layer)

    # Notenhals
    stem_x = head_cx + int(head_w * 0.42)
    stem_top = int(s * 0.22)
    stem_bottom = head_cy - int(head_h * 0.10)
    stem_w = max(4, int(s * 0.035))
    draw.rounded_rectangle(
        [stem_x - stem_w // 2, stem_top, stem_x + stem_w // 2, stem_bottom],
        radius=stem_w // 2, fill=note_color,
    )

    # Fähnchen — vereinfachtes Polygon, reicht für die Logo-Größe
    flag = [
        (stem_x, stem_top),
        (stem_x + int(s * 0.18), stem_top + int(s * 0.06)),
        (stem_x + int(s * 0.22), stem_top + int(s * 0.16)),
        (stem_x + int(s * 0.16), stem_top + int(s * 0.22)),
        (stem_x + int(s * 0.10), stem_top + int(s * 0.14)),
        (stem_x + stem_w // 2, stem_top + int(s * 0.08)),
    ]
    draw.polygon(flag, fill=note_color)

    # Download-Akzent unten rechts
    accent = (255, 220, 100, 255)
    ax, ay = int(s * 0.78), int(s * 0.78)
    r = int(s * 0.13)

    draw.ellipse([ax - r, ay - r, ax + r, ay + r],
                 fill=(30, 40, 90, 255), outline=accent, width=max(3, int(s * 0.012)))

    shaft_w = max(3, int(s * 0.018))
    draw.rounded_rectangle(
        [ax - shaft_w, ay - int(r * 0.55), ax + shaft_w, ay + int(r * 0.15)],
        radius=shaft_w, fill=accent,
    )
    draw.polygon([
        (ax - int(r * 0.45), ay + int(r * 0.05)),
        (ax + int(r * 0.45), ay + int(r * 0.05)),
        (ax,                 ay + int(r * 0.55)),
    ], fill=accent)

    # Downsample für saubere Kanten
    return bg.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    make_logo(256).save("/tmp/logo_preview.png")
    print("Logo gespeichert: /tmp/logo_preview.png")
