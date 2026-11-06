# -*- coding: utf-8 -*-
"""
Purpose: Draw the fracture radiology map: the module's own X-rays read in the order a fracture
         is described (views -> location -> type -> descriptors -> joint surface -> other
         findings -> bone quality -> healing).
Author:  Noor Simsam (with Claude Code)
Date:    2026-11-06
Input:   the two module decks, as attached to her OneNote pages (Asynch W10): "Fracture
         Interpretation PP with2023 edits.pdf" (--pdf) and "Fracture Interpretation pt.2.pdf"
         (--pdf2); every picture is cropped from them
Output:  an SVG with the crops embedded as JPEG data URIs (--out), optional PNG preview (--png)

The layout is tools/picture_map.py; this file is the content, every line of it from the
lecture note. It sits beside the lecture's overview chart (msk-w10-04_2), which keeps the
interactive page and the body map's links. Skipped on purpose: slide 38's wound photograph
(the film beside it is used) and the deck's drawings, except the varus/valgus pair and the
stages of healing, which have no film.

    python3 tools/pathways/src/msk-w10-04_3.py --pdf "<Fracture Interpretation PP with2023 edits.pdf>" \
        --pdf2 "<Fracture Interpretation pt.2.pdf>" \
        --out "<vault>/Attachments/fracture radiology map.svg" --png /tmp/p.png
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import picture_map  # noqa: E402

# picture_map's CROPS shape: (pdf page, image index on the page), crop box as fractions
CROPS = {
    "ap_foot": ((4, 0), (0, 0, 1, 1)),
    "oblique_foot": ((5, 1), (0, 0, 1, 1)),
    "lat_foot": ((6, 1), (0, 0, 1, 1)),
    "mortise": [((8, 0), (0, 0, 1, 1)), ((8, 1), (0, 0, 1, 1))],   # mortise | AP
    "y_view": ((9, 1), (0, 0, 1, 1)),
    "long_bone": ((11, 1), (0, 0, 1, 1)),
    "apophysis": ((12, 1), (0, 0, 1, 1)),
    "transverse": ((15, 0), (0, 0, 1, 1)),
    "oblique": ((16, 0), (0, 0, 1, 1)),
    "linear": ((18, 2), (0, 0, 1, 1)),
    "spiral": [((20, 0), (0, 0, 1, 1)), ((20, 1), (0, 0, 1, 1))],
    "comminuted": ((21, 2), (0, 0, 1, 1)),
    "butterfly": ((22, 1), (0, 0, 1, 1)),
    "segmental": ((23, 0), (0, 0, 1, 1)),
    "angulation": ((25, 0), (0, 0, 1, 1), "keep"),   # the deck's varus | valgus drawing
    "translation": ((27, 1), (0, 0, 1, 1)),
    "off_ended": ((28, 0), (0, 0, 1, 1)),
    "distraction": ((31, 0), (0, 0, 1, 1)),
    "impaction": ((32, 0), (0, 0, 1, 1)),
    "override": ((33, 0), (0, 0, 1, 1)),
    "step_off": ((35, 0), (0, 0, 1, 1)),
    "fat_fluid": ((36, 1), (0, 0, 1, 1)),
    "dislocation": ((37, 0), (0, 0, 1, 1)),
    "open": ((38, 1), (0, 0, 1, 1)),
    "periprosthetic": ((39, 0), (0, 0, 1, 1)),
    "avulsion": ((40, 1), (0, 0, 1, 1)),
    "amputation": ((41, 1), (0, 0, 1, 1)),
    "diastasis": ((42, 0), (0, 0, 1, 1)),
    "pathological": ((43, 0), (0, 0, 1, 1)),
}
CROPS2 = {   # part 2: fracture healing
    "stages": ((2, 0), (0, 0, 1, 1), "keep"),
    "primary": [((4, 0), (0, 0, 1, 1)), ((4, 1), (0, 0, 1, 1))],
    "secondary": [((5, 0), (0, 0, 1, 1)), ((5, 1), (0, 0, 1, 1))],
}

ROOT = {
    "title": "Describe every fracture film in the same order",
    "img": None,
    "lines": [
        "**Detect** it first: **trace the cortex**, look for **secondary signs**",
        "1 · **Views** · 2 · **Location** · 3 · **Type** · 4 · **Descriptors** · "
        "5 · **Joint surface** · 6 · **Other findings** · 7 · **Bone quality** · 8 · **Healing**",
        "• **More than one descriptor for each fracture**",
        "• **OLD ACIDS**: Open or closed · Location · Degree (complete or incomplete) · "
        "Articular surface · Comminution and type · Intrinsic bone quality · Displacement · "
        "Soft tissue injury",
    ],
}

BANDS = [
    {"name": "1 · VIEWS", "colour": "teal", "rows": [
        {"label": "STANDARD VIEWS: AP · lateral · oblique, the body described in anatomic position",
         "cards": [
             {"title": "AP (front-to-back)", "img": "ap_foot", "lines": ["• Right foot"]},
             {"title": "Oblique", "img": "oblique_foot", "lines": [
                 "• An **oblique** fracture shows on one view"]},
             {"title": "Lateral", "img": "lat_foot", "lines": [
                 "• A **spiral** fracture needs multiple views"]},
         ]},
        {"label": "SPECIAL VIEWS for particular sites", "cards": [
            {"title": "Ankle: mortise view", "img": "mortise", "lines": [
                "• **Mortise** (left) beside the AP (right)"]},
            {"title": "Shoulder: Y-view", "img": "y_view", "lines": [
                "• **Y-view** for the shoulder"]},
            {"title": "Wrist: scaphoid views", "img": None, "lines": [
                "• Wrist in **ulnar deviation**",
                "• **Clenched-fist** view"]},
        ]},
    ]},
    {"name": "2 · LOCATION", "colour": "purple", "rows": [
        {"label": "RIGHT OR LEFT · WHICH BONE · WHICH PART", "cards": [
            {"title": "Parts of a long bone", "img": "long_bone", "lines": [
                "• **Epiphysis** (end) · **physis** (growth plate, immature skeleton only)",
                "• **Metaphysis** · **diaphysis** (shaft)",
                "• Growth plate fracture = **Salter-Harris** injury"]},
            {"title": "Apophysis", "img": "apophysis", "lines": [
                "• **Non-articular bump** where muscles or tendons attach, **under traction**"]},
        ]},
    ]},
    {"name": "3 · TYPE", "colour": "orange", "rows": [
        {"label": "COMPLETE (all the way through), by the fracture line", "cards": [
            {"title": "Transverse", "img": "transverse", "lines": [
                "• Straight across, perpendicular to the shaft",
                "• **Pathological fractures are usually transverse**"]},
            {"title": "Oblique", "img": "oblique", "lines": [
                "• Diagonal, seen on one view",
                "• Check a second view to tell from spiral"]},
            {"title": "Longitudinal / linear", "img": "linear", "lines": [
                "• Along the long axis"]},
        ]},
        {"label": "SPIRAL AND COMMINUTED", "cards": [
            {"title": "Spiral", "img": "spiral", "lines": [
                "• Winds around the shaft: **twisting injury**",
                "• **Needs multiple views** · can resemble oblique, with a butterfly fragment"]},
            {"title": "Comminuted", "img": "comminuted", "lines": [
                "• **More than two fragments**"]},
        ]},
        {"label": "COMMINUTED: TWO SHAPES TO NAME", "cards": [
            {"title": "Butterfly fragment", "img": "butterfly", "lines": [
                "• A triangular **butterfly** fragment"]},
            {"title": "Segmental", "img": "segmental", "lines": [
                "• Comminuted, **segmental**"]},
            {"title": "Incomplete (immature skeleton)", "img": None, "lines": [
                "• **Bowing** · **buckle** · **greenstick** · **Salter-Harris**",
                "• Others: **avulsion**, **open** (band 6)"]},
        ]},
    ]},
    {"name": "4 · DESCRIPTORS", "colour": "blue", "rows": [
        {"label": "THE DISTAL FRAGMENT RELATIVE TO THE PROXIMAL",
         "note": "Except the clavicle: there the proximal fragment is described relative to the distal (neck muscles pull it up).",
         "cards": [
             {"title": "Translation (displacement)", "img": "translation", "lines": [
                 "• Ends move away from each other, in **shaft widths**"]},
             {"title": "Off-ended", "img": "off_ended", "kind": "bad", "lines": [
                 "• Translation **more than a full shaft width**"]},
             {"title": "Angulation", "img": "angulation", "lines": [
                 "• Named by the **direction of the apex**",
                 "• **Varus = apex lateral** · **valgus = apex medial**"]},
         ]},
        {"label": "LENGTH (and rotation: turned internally or externally, so look at the joints above and below)",
         "cards": [
             {"title": "Distraction", "img": "distraction", "lines": [
                 "• Fragments **pulled apart**"]},
             {"title": "Impaction", "img": "impaction", "lines": [
                 "• Driven into each other, **\"telescoped\"**",
                 "• **Foreshortens**"]},
             {"title": "Override", "img": "override", "lines": [
                 "• Fragments **overlap**",
                 "• **Foreshortens**"]},
         ]},
    ]},
    {"name": "5 · JOINT SURFACE", "colour": "magenta", "rows": [
        {"label": "EXTRA-ARTICULAR (joint spared, remodels) vs INTRA-ARTICULAR",
         "note": "Intra-articular: risk of secondary osteoarthritis, the reduction must be anatomic, longer to heal.",
         "cards": [
             {"title": "Step-off or depression", "img": "step_off", "kind": "bad", "lines": [
                 "• Abrupt break in the joint's cortical line: **trace the cortex**"]},
             {"title": "No line seen: secondary signs", "img": "fat_fluid", "kind": "bad", "lines": [
                 "• **Hemarthrosis (effusion)** and a **fat-fluid level** (lipohemarthrosis)",
                 "• = an **intra-articular fracture** even when no line is seen"]},
             {"title": "Subluxation or dislocation", "img": "dislocation", "kind": "bad", "lines": [
                 "• Joint surface involvement too"]},
         ]},
    ]},
    {"name": "6 · OTHER FINDINGS", "colour": "slate", "rows": [
        {"label": "OPEN · HARDWARE · AVULSION", "cards": [
            {"title": "Open (compound)", "img": "open", "kind": "bad", "lines": [
                "• Through the skin: the lecture's case, upper and mid third of the tibia and fibula"]},
            {"title": "Periprosthetic", "img": "periprosthetic", "wide": True, "lines": [
                "• Fracture around an implant · note any **foreign body or hardware**"]},
            {"title": "Avulsion", "img": "avulsion", "lines": [
                "• A tendon or ligament pulls off a fragment",
                "• e.g. intra-articular, dorsally displaced triangle at the extensor tendon's base of the distal phalanx"]},
        ]},
        {"label": "DIASTASIS · AMPUTATION", "cards": [
            {"title": "Diastasis", "img": "diastasis", "lines": [
                "• **Widened or incongruent joint**, with or without fracture",
                "• **Pubic symphysis**, acromioclavicular joint"]},
            {"title": "Amputation", "img": "amputation", "kind": "bad", "lines": [
                "• Its own finding, named in the description"]},
        ]},
    ]},
    {"name": "7 · BONE QUALITY", "colour": "brown", "rows": [
        {"label": "WEAKENED BONE", "cards": [
            {"title": "Pathological (fragility) fracture", "img": "pathological", "kind": "bad", "lines": [
                "• **Usually transverse**",
                "• Spontaneous, or with **trivial trauma**"]},
        ]},
    ]},
    {"name": "8 · HEALING", "colour": "olive", "rows": [
        {"label": "HEALING IS A CLINICAL DIAGNOSIS: no tenderness, no motion at the fracture site, weight-bearing possible",
         "cards": [
             {"title": "Secondary (spontaneous): the usual", "img": "stages", "wide": True, "lines": [
                 "• **Inflammatory → reparative (callus) → remodelling**",
                 "• Complete remodelling takes **years**"]},
             {"title": "Secondary healing: lateral malleolus", "img": "secondary", "lines": [
                 "• Complete secondary healing years after the fracture"]},
         ]},
        {"label": "PRIMARY (CONTACT) HEALING, AND THE TIMELINE", "cards": [
            {"title": "Primary healing: K-wires", "img": "primary", "lines": [
                "• Bone surfaces **directly apposed** (internal fixation)",
                "• **No callus**"]},
            {"title": "On x-ray, and how long", "img": None, "lines": [
                "• Line **widens at 10-14 days** (resorption, not displacement)",
                "• **Callus at 2 weeks** · union = mature bridging callus, medullary space restored",
                "• **Upper limb 3-10 weeks** (distal humerus longest) · **lower limb 6-12 weeks** (femoral neck and shaft longest)",
                "• **Delayed union** = twice as long as expected · **non-union** = no healing in **6-9 months** · **malunion** = non-anatomic healing"]},
        ]},
    ]},
]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--pdf2", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--png", type=Path)
    args = ap.parse_args()
    pictures = picture_map.load_crops(args.pdf, CROPS, {})
    pictures.update(picture_map.load_crops(args.pdf2, CROPS2, {}))
    svg, height = picture_map.render(ROOT, BANDS, pictures)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:   # LF on Windows too
        f.write(svg)
    logging.info("wrote %s (%d KB, %d px tall)", args.out, len(svg) // 1024, height)
    if args.png:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(args.png), output_width=picture_map.WIDTH)


if __name__ == "__main__":
    main()
