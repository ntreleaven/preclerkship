"""
Purpose: Draw the schematic figures for the pelvic and obstetrical exam page (side and front
         views of the pelvis, patient positioning): no photographs of bodies.
Author: Noor Simsam
Date: 2026-10-28
Input: none
Output: img/<name>.jpg for each drawn figure (800 px wide, JPEG q85)
"""

import io
import logging
from pathlib import Path

import cairosvg
from PIL import Image

LOG = logging.getLogger("draw_figures")
IMG = Path(__file__).resolve().parent / "img"
W, H = 800, 600

SKIN, SKIN_D = "#f1c9a5", "#c8946a"
PINK, PINK_D = "#e8a3ae", "#b9626f"
BONE, GUT = "#e9e2cf", "#b58d6e"
BLADDER = "#f3e08a"
STEEL, STEEL_D = "#aeb6c2", "#5b6573"
INK = "#222"
ARROW = "#c0392b"


def wrap(body: str, defs: str = "") -> str:
    """Wrap SVG body in a canvas with an arrowhead marker."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ARROW}"/></marker>{defs}</defs>'
            f'<rect width="{W}" height="{H}" fill="#fff"/>{body}</svg>')


def label(x: int, y: int, text: str, anchor: str = "start", size: int = 20) -> str:
    """A text label."""
    size = int(size * 1.35)
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="DejaVu Sans, Arial" font-size="{size}" '
            f'fill="{INK}">{text}</text>')


def pointer(x1: int, y1: int, x2: int, y2: int) -> str:
    """A thin leader line from a label to a structure."""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="1.5"/><circle cx="{x2}" cy="{y2}" r="3" fill="#555"/>'


def arrow(x1: int, y1: int, x2: int, y2: int, both: bool = False) -> str:
    """A red movement arrow."""
    start = ' marker-start="url(#ah)"' if both else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="4" '
            f'marker-end="url(#ah)"{start}/>')


# the vagina runs from the opening (OX, OY) up and back to the cervix (CX, CY): angle in degrees
OX, OY, CX, CY = 190, 400, 400, 285
ANG = -29.0


def sagittal(uterus_hi: bool = False) -> str:
    """The pelvis from the side (patient faces left): bones, bladder, urethra, vagina, cervix, uterus, rectum."""
    return (
        # sacrum and coccyx at the back, pubic bone at the front
        f'<path d="M560,90 C610,200 600,330 540,430 L505,420 C545,330 550,200 520,110 Z" fill="{BONE}" stroke="#8a826a" stroke-width="2"/>'
        f'<rect x="150" y="270" width="40" height="95" rx="18" fill="{BONE}" stroke="#8a826a" stroke-width="2" transform="rotate(12 170 318)"/>'
        # bladder and urethra
        f'<ellipse cx="260" cy="300" rx="62" ry="42" fill="{BLADDER}" stroke="#a89a3c" stroke-width="2"/>'
        f'<path d="M222,330 C205,360 190,385 178,418" fill="none" stroke="#a89a3c" stroke-width="9" stroke-linecap="round"/>'
        # rectum behind the vagina
        f'<path d="M470,130 C485,230 470,330 480,420 L520,440" fill="none" stroke="{GUT}" stroke-width="30" stroke-linecap="round"/>'
        # vagina
        f'<line x1="{OX}" y1="{OY + 14}" x2="{CX}" y2="{CY + 6}" stroke="{PINK_D}" stroke-width="44" stroke-linecap="round"/>'
        f'<line x1="{OX}" y1="{OY + 14}" x2="{CX}" y2="{CY + 6}" stroke="{PINK}" stroke-width="38" stroke-linecap="round"/>'
        # uterus leaning forward (anteverted), cervix pointing back into the vagina
        f'<g transform="translate({CX},{CY - 10}) rotate(-38)">'
        f'<path d="M-24,0 L-34,-70 C-60,-130 -40,-190 0,-196 C40,-190 60,-130 34,-70 L24,0 Z" fill="{PINK}" stroke="{PINK_D}" stroke-width="3"/>'
        f'<path d="M-8,0 L-8,-150 L8,-150 L8,0 Z" fill="#f6d3d9" opacity=".7"/>'
        f'<path d="M-24,0 C-24,22 24,22 24,0 Z" fill="#d9808e" stroke="{PINK_D}" stroke-width="3"/></g>'
        # outline of the lower abdominal wall and thigh skin
        f'<path d="M110,60 C100,180 120,260 160,330 L120,400 C80,430 80,480 110,520" fill="none" stroke="{SKIN_D}" stroke-width="3" stroke-dasharray="6 5"/>'
    )


def finger(length: int = 215, width: int = 22) -> str:
    """Two examining fingers in local coordinates along the vaginal axis (x forward)."""
    return (f'<rect x="-40" y="-{width}" width="{length}" height="{width}" rx="{width // 2}" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>'
            f'<rect x="-40" y="3" width="{length - 8}" height="{width}" rx="{width // 2}" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>')


def speculum(open_gap: int = 36, with_handle: bool = True) -> str:
    """A bivalve speculum in the vagina, blades opened so the cervix sits between them."""
    g = open_gap
    out = (f'<g transform="translate({OX + 20},{OY + 6}) rotate({ANG})">'
           f'<polygon points="0,-22 175,-{30 + g // 2} 175,-{14 + g // 2} 0,-14" fill="{STEEL}" stroke="{STEEL_D}" stroke-width="2.5"/>'
           f'<polygon points="0,14 175,{14 + g // 2 + 4} 175,{30 + g // 2 + 4} 0,22" fill="{STEEL}" stroke="{STEEL_D}" stroke-width="2.5"/>')
    if with_handle:
        out += (f'<rect x="-90" y="-20" width="92" height="12" rx="4" fill="{STEEL}" stroke="{STEEL_D}" stroke-width="2.5"/>'
                f'<rect x="-90" y="10" width="92" height="12" rx="4" fill="{STEEL}" stroke="{STEEL_D}" stroke-width="2.5" transform="rotate(14 0 16)"/>')
    return out + "</g>"


def fig_view_cervix() -> str:
    """Cervix between the blades."""
    return wrap(sagittal() + speculum(70) + label(30, 40, "Cervix between the blades", size=22))


def fig_remove() -> str:
    """Speculum closing as it is drawn out, with the vaginal walls checked on the way."""
    return wrap(sagittal() + speculum(8) + arrow(300, 470, 150, 500)
                + label(30, 40, "Draw back, blades closing", size=22))


def fig_sample() -> str:
    """Cervical brush rotated at the opening of the cervix (transformation zone)."""
    brush = (f'<g transform="translate({OX + 40},{OY + 8}) rotate({ANG})"><rect x="-60" y="-4" width="230" height="8" rx="4" fill="#3a6fb0"/>'
             + "".join(f'<line x1="{x}" y1="0" x2="{x + 6}" y2="{s}" stroke="#2c4f80" stroke-width="2.5"/><line x1="{x}" y1="0" x2="{x + 6}" y2="{-s}" stroke="#2c4f80" stroke-width="2.5"/>'
                       for x, s in [(150, 12), (160, 15), (170, 15), (180, 12)]) + "</g>")
    return wrap(sagittal() + speculum(70, False) + brush
                + f'<path d="M{CX + 6},{CY + 40} a38,38 0 1,1 -4,-72" fill="none" stroke="{ARROW}" stroke-width="4" marker-end="url(#ah)" transform="translate(-14,-4)"/>'
                + label(30, 40, "Brush at the os, rotate", size=22)
                + label(400, 470, "Transformation zone", size=19) + label(400, 500, "(cancer starts here)", size=19)
                + pointer(500, 450, CX + 5, CY - 12))


def fig_swab() -> str:
    """A swab on the cervix and another on the vaginal wall."""
    cs = (f'<g transform="translate({OX + 40},{OY - 4}) rotate({ANG})"><rect x="-60" y="-3" width="215" height="6" rx="3" fill="#d6cdb8" stroke="#8a826a"/>'
          f'<ellipse cx="160" cy="0" rx="13" ry="7" fill="#fff" stroke="#8a826a" stroke-width="2"/></g>')
    return wrap(sagittal() + speculum(70, False) + cs
                + label(30, 40, "Swab at the cervix", size=22)
                + pointer(440, 470, CX + 5, CY + 4))


def fig_bimanual_cervix() -> str:
    """Fingertips on the cervix, moving it side to side."""
    return wrap(sagittal() + f'<g transform="translate({OX + 10},{OY + 4}) rotate({ANG})">{finger(205)}</g>'
                + arrow(CX - 20, CY + 60, CX - 20, CY - 40, both=True)
                + label(30, 40, "Move the cervix gently", size=22))


def fig_bimanual_uterus() -> str:
    """Fingers lift the cervix; the other hand presses above the pubic bone."""
    hand = (f'<g transform="translate(130,150) rotate(35)"><rect x="0" y="0" width="150" height="46" rx="20" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/></g>')
    return wrap(sagittal() + f'<g transform="translate({OX + 10},{OY + 4}) rotate({ANG})">{finger(205)}</g>' + hand
                + arrow(250, 120, 300, 230) + arrow(CX - 5, CY + 70, CX - 15, CY - 10)
                + label(30, 40, "Lift cervix, press above pubis", size=22))


def fig_bimanual_adnexa() -> str:
    """Front view: fingers in one side fork of the vagina, abdominal hand sweeping down and in toward them."""
    cx = 400
    body = (f'<path d="M{cx - 28},330 L{cx - 22},430 L{cx + 22},430 L{cx + 28},330 Z" fill="{PINK}" stroke="{PINK_D}" stroke-width="3"/>'
            f'<path d="M{cx - 70},120 C{cx - 80},230 {cx - 40},310 {cx - 26},340 L{cx + 26},340 C{cx + 40},310 {cx + 80},230 {cx + 70},120 C{cx + 40},60 {cx - 40},60 {cx - 70},120 Z" fill="{PINK}" stroke="{PINK_D}" stroke-width="3"/>'
            f'<ellipse cx="{cx}" cy="342" rx="30" ry="14" fill="#d9808e" stroke="{PINK_D}" stroke-width="3"/>')
    tubes = "".join(f'<path d="M{cx + s * 62},100 C{cx + s * 120},60 {cx + s * 190},70 {cx + s * 215},140" fill="none" stroke="{PINK_D}" stroke-width="9" stroke-linecap="round"/>'
                    f'<ellipse cx="{cx + s * 225}" cy="170" rx="30" ry="22" fill="#f4e3b2" stroke="#a89a3c" stroke-width="3"/>' for s in (-1, 1))
    fingers = (f'<g transform="translate({cx + 14},520) rotate(-90)"><rect x="0" y="-22" width="150" height="20" rx="10" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>'
               f'<rect x="0" y="2" width="150" height="20" rx="10" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/></g>')
    hand = f'<g transform="translate(600,60) rotate(55)"><rect x="0" y="0" width="150" height="46" rx="20" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/></g>'
    return wrap(body + tubes + fingers + hand + arrow(640, 150, 540, 290)
                + label(30, 40, "Adnexa, front view", size=22)
                + label(cx + 225, 225, "Ovary", "middle", 17) + label(cx - 40, 400, "Vagina", "end", 17)
                + label(cx, 200, "Uterus", "middle", 18))


def lying(pregnant: bool = False, legs_up: bool = True, doppler: bool = False, tape: bool = False) -> str:
    """A patient seen from the side, lying on a table, with a drape; head to the left."""
    table = '<rect x="40" y="410" width="720" height="26" rx="8" fill="#9aa5b4"/><rect x="90" y="436" width="14" height="100" fill="#7b8696"/><rect x="690" y="436" width="14" height="100" fill="#7b8696"/>'
    pillow = '<ellipse cx="120" cy="385" rx="60" ry="24" fill="#dfe6ee" stroke="#8a96a6" stroke-width="2"/>'
    head = f'<circle cx="112" cy="345" r="36" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/><circle cx="102" cy="340" r="3.5" fill="{INK}"/><path d="M98,360 Q110,367 124,360" fill="none" stroke="{INK}" stroke-width="2.5"/>'
    belly_h = 70 if pregnant else 28
    trunk = f'<path d="M150,405 L150,{385 - 25} C230,{385 - belly_h - 10} 330,{385 - belly_h - 10} 395,{395 - belly_h // 2} L430,410 Z" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/>'
    if legs_up:
        legs = f'<path d="M430,398 L540,292" fill="none" stroke="{SKIN}" stroke-width="38" stroke-linecap="round"/>'
        drape = (f'<path d="M290,350 L440,340 L545,250 L580,285 L560,335 L470,418 L290,418 Z" fill="#e6eef7" stroke="#8fa3bd" stroke-width="3"/>'
                 f'<path d="M548,300 L622,408" stroke="{SKIN}" stroke-width="30" stroke-linecap="round"/>'
                 f'<rect x="600" y="404" width="52" height="16" rx="6" fill="#7b8696"/>'
                 f'<path d="M626,420 L626,470 L700,470" fill="none" stroke="#7b8696" stroke-width="8" stroke-linecap="round"/>')
    else:
        legs = f'<path d="M420,402 L690,402" stroke="{SKIN}" stroke-width="38" stroke-linecap="round"/>'
        drape = (f'<path d="M370,{392 - belly_h // 2} C400,{395 - belly_h // 2} 420,380 450,378 L710,382 L710,425 L370,425 Z" fill="#e6eef7" stroke="#8fa3bd" stroke-width="3"/>')
    extra = ""
    if tape:
        extra = (f'<path d="M290,316 C330,318 372,334 395,358" fill="none" stroke="#e0b100" stroke-width="7" stroke-dasharray="3 5"/>'
                 f'<circle cx="290" cy="316" r="6" fill="{ARROW}"/><circle cx="396" cy="359" r="6" fill="{ARROW}"/>')
    if doppler:
        extra = (f'<g transform="translate(370,{296})"><rect x="-12" y="-6" width="24" height="46" rx="8" fill="#455a74" stroke="#2c3a4d" stroke-width="2.5" transform="rotate(20)"/></g>'
                 + "".join(f'<path d="M{392 + 12 * i},{340 + 8 * i} q10,14 -6,26" fill="none" stroke="{ARROW}" stroke-width="3"/>' for i in range(3)))
    return table + pillow + trunk + head + legs + drape + extra


def fig_position() -> str:
    """Dorsal lithotomy: back on the table, hips at the edge, heels in the stirrups, drape pressed down."""
    return wrap(lying() + label(30, 40, "Dorsal lithotomy position", size=22))


def fig_ob_position() -> str:
    """Obstetrical exam position: on the back, head raised, abdomen uncovered, drape over the legs."""
    return wrap(lying(pregnant=True, legs_up=False) + label(30, 40, "Obstetrical exam position", size=22))


def fig_sfh() -> str:
    """Tape from the top of the pubic bone to the top of the uterus."""
    return wrap(lying(pregnant=True, legs_up=False, tape=True)
                + label(30, 40, "Symphysis-fundal height", size=22)
                + label(250, 296, "Fundus", size=18) + label(412, 350, "Symphysis pubis", size=18))


def fig_doppler() -> str:
    """Doppler over the baby's back."""
    return wrap(lying(pregnant=True, legs_up=False, doppler=True)
                + label(30, 40, "Doppler over the baby's back", size=22))


def label_sagittal(title: str, items: list) -> str:
    """Side view with labelled landmarks: (structure x, y, label x, y, text); labels right of 400 end at their x."""
    out = sagittal() + label(30, 40, title, size=22)
    for x, y, tx, ty, text in items:
        out += pointer(tx + (len(text) * 9 if tx < 400 else 0) if tx < 400 else tx - len(text) * 9, ty - 6, x, y)
        out += label(tx, ty, text, "start" if tx < 400 else "end", 17)
    return wrap(out)


FIGURES = {
    "position-and-drape.jpg": fig_position, "viewing-the-cervix.jpg": fig_view_cervix, "speculum-removal.jpg": fig_remove,
    "cervical-screening-sample.jpg": fig_sample, "other-swabs.jpg": fig_swab,
    "bimanual-cervix.jpg": fig_bimanual_cervix, "bimanual-uterus.jpg": fig_bimanual_uterus,
    "bimanual-adnexa.jpg": fig_bimanual_adnexa, "obstetrical-position-and-drape.jpg": fig_ob_position,
    "symphysis-fundal-height.jpg": fig_sfh, "fetal-heart-rate.jpg": fig_doppler,
    "speculum-landmarks.jpg": lambda: label_sagittal("Landmarks, side view", [
        (160, 330, 20, 250, "Pubic bone"), (260, 300, 20, 200, "Bladder"), (178, 410, 20, 480, "Urethra opening"),
        (300, 340, 120, 550, "Vagina"), (CX, CY, 780, 500, "Cervix (os)"), (330, 170, 780, 130, "Uterus"),
        (480, 300, 780, 300, "Rectum"), (570, 220, 780, 210, "Sacrum")]),
    "bimanual-landmarks.jpg": lambda: label_sagittal("Between the two hands", [
        (160, 330, 20, 250, "Pubic bone"), (CX, CY, 780, 500, "Cervix: fingertips"),
        (330, 170, 780, 130, "Uterus: between hands"), (545, 110, 780, 60, "Sacral promontory"),
        (480, 380, 780, 440, "Rectum")]),
}


def main() -> None:
    """Render every figure to a JPEG in img/."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for name, make in FIGURES.items():
        png = cairosvg.svg2png(bytestring=make().encode("utf-8"), output_width=W)
        Image.open(io.BytesIO(png)).convert("RGB").save(IMG / name, quality=85)
        LOG.info("drew %s", name)


if __name__ == "__main__":
    main()
