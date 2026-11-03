"""
Purpose: Draw the palpation-pattern diagrams for the breast exam page (own work, CC0): the
         rectangle to cover and the vertical-strip pattern for the outer and the inner half.
Author: Noor Simsam
Date: 2026-10-28
Input: none
Output: img/palpate-landmarks.jpg, img/lateral-outer-half.jpg, img/medial-inner-half.jpg
"""

import io
from pathlib import Path

import cairosvg
from PIL import Image

IMG = Path(__file__).resolve().parent / "img"
NIPPLE_X, LEFT, RIGHT, TOP, BOTTOM = 400, 150, 630, 70, 530
OUTER, INNER, GREY = "#b4501f", "#23798a", "#555"


def strips(x_from: int, x_to: int, colour: str, down_first: bool) -> str:
    """Return the arrows of overlapping vertical strips between two x positions."""
    out, down = [], down_first
    for x in range(x_from, x_to + 1, 40):
        y1, y2 = (TOP + 30, BOTTOM - 20) if down else (BOTTOM - 20, TOP + 30)
        out.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{colour}" stroke-width="4" '
                   f'marker-end="url(#a{colour[1:]})"/>')
        down = not down
    return "".join(out)


def svg(show: str) -> str:
    """Build the SVG for 'both', 'outer' or 'inner'."""
    marks = "".join(f'<marker id="a{c[1:]}" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">'
                    f'<path d="M0,0 L8,4 L0,8 z" fill="{c}"/></marker>' for c in (OUTER, INNER))
    body = ""
    if show in ("both", "outer"):
        body += f'<rect x="{LEFT}" y="{TOP}" width="{NIPPLE_X - LEFT}" height="{BOTTOM - TOP}" fill="{OUTER}" fill-opacity=".10"/>'
        body += strips(LEFT + 20, NIPPLE_X - 20, OUTER, True)
    if show in ("both", "inner"):
        body += f'<rect x="{NIPPLE_X}" y="{TOP}" width="{RIGHT - NIPPLE_X}" height="{BOTTOM - TOP}" fill="{INNER}" fill-opacity=".10"/>'
        body += strips(NIPPLE_X + 20, RIGHT - 20, INNER, True)
    note = {"both": "Cover the whole rectangle", "outer": "Outer half: start in the armpit, work toward the nipple",
            "inner": "Inner half: start at the nipple, work to the breastbone"}[show]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 640" width="800" height="640">
<defs>{marks}</defs><rect width="800" height="640" fill="#fff"/>
<path d="M{RIGHT+10},20 L{RIGHT+10},620" stroke="{GREY}" stroke-width="3" stroke-dasharray="10 6"/>
<path d="M{TOP and 40},{TOP} L{RIGHT+10},{TOP}" stroke="{GREY}" stroke-width="3" stroke-dasharray="10 6"/>
<path d="M{LEFT},20 L{LEFT},620" stroke="{GREY}" stroke-width="3" stroke-dasharray="10 6"/>
<path d="M40,{BOTTOM} Q{NIPPLE_X},{BOTTOM+40} {RIGHT+10},{BOTTOM}" fill="none" stroke="{GREY}" stroke-width="3" stroke-dasharray="10 6"/>
{body}
<ellipse cx="{NIPPLE_X}" cy="{BOTTOM-165}" rx="205" ry="165" fill="none" stroke="#222" stroke-width="5"/>
<path d="M{NIPPLE_X-190},{BOTTOM-230} Q{LEFT+30},{TOP+80} {LEFT+8},{TOP+60}" fill="none" stroke="#222" stroke-width="5"/>
<circle cx="{NIPPLE_X}" cy="{BOTTOM-165}" r="34" fill="none" stroke="#222" stroke-width="4"/>
<circle cx="{NIPPLE_X}" cy="{BOTTOM-165}" r="9" fill="#222"/>
<g font-family="Arial, sans-serif" font-size="22" fill="#222">
<text x="{RIGHT-110}" y="52" text-anchor="end">collarbone (clavicle)</text>
<text x="{RIGHT+22}" y="300" transform="rotate(90 {RIGHT+22} 300)" text-anchor="middle">midsternal line</text>
<text x="{LEFT-12}" y="300" transform="rotate(-90 {LEFT-12} 300)" text-anchor="middle">posterior axillary line</text>
<text x="{NIPPLE_X}" y="{BOTTOM+52}" text-anchor="middle">bra line (inframammary fold)</text>
<text x="{LEFT+12}" y="{TOP+26}" font-size="19">armpit and tail</text>
<text x="400" y="626" text-anchor="middle" font-size="24" font-weight="bold">{note}</text>
</g></svg>"""


def main() -> None:
    """Render the three diagrams to JPEG."""
    for show, name in (("both", "palpate-landmarks"), ("outer", "lateral-outer-half"), ("inner", "medial-inner-half")):
        png = cairosvg.svg2png(bytestring=svg(show).encode(), output_width=800)
        Image.open(io.BytesIO(png)).convert("RGB").save(IMG / f"{name}.jpg", quality=85)


if __name__ == "__main__":
    main()
