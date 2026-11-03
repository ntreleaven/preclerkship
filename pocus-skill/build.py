"""
Purpose: Build the How a station runs clinical skills page (pocus-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Ultrasound Clinical Skills".
Author: Noor Simsam
Date: 2026-11-01
Input: the vault note (POM2_VAULT or the default vault path)
Output: pocus-skill/index.html

The note is the single source of the questions and what to listen for: edit the note,
then rerun this script. Which problem heading each row sits under is set here. A history
is a conversation, so its cards have no pictures. How the page looks lives in
clinical-skills/exam_page.py, shared by every exam page.
"""

import importlib.util
import json
import os
import re
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exam_page", HERE.parent / "clinical-skills/exam_page.py")
exam_page = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exam_page)
VAULT = Path(os.environ.get("POM2_VAULT", "/mnt/c/Users/nsims/medwiki"))
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Ultrasound Clinical Skills.md"


def plain_note(path: Path) -> Path:
    """Copy the note with its single-asterisk italics removed (the engine reads bold only).

    Parameters
    ----------
    path : Path
        The vault note.

    Returns
    -------
    Path
        A temporary copy for the engine to read; the vault note is not touched.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)", r"\1", text)
    out = Path(tempfile.mkdtemp()) / path.name
    out.write_text(text, encoding="utf-8")
    return out


# section number in the note -> region on the page
REGIONS = {2: ('heart', 'Heart: the subxiphoid view', 'PoM 1 · POCUS session', '#b4501f'),
 3: ('upper', 'Upper abdomen', 'PoM 1 · POCUS session', '#23798a'),
 4: ('pelvis', 'Pelvis', 'PoM 1 · POCUS session', '#7a3fb0'),
 5: ('vessels', 'Vessels', 'T2C · POCUS', '#a8366f'),
 6: ('msk', 'Musculoskeletal structures', 'T2C · POCUS', '#2f6b4f')}

GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture)
TESTS = {
    'Subxiphoid (heart)': ('Is the heart moving, and is there fluid around it?', 'subxiphoid.jpg'),
    'Right upper quadrant': ('Liver, kidney and the space between them', 'ruq.jpg'),
    'Gallbladder': ('Liver, kidney and the space between them', 'gallbladder.jpg'),
    'Left upper quadrant': ('Liver, kidney and the space between them', 'luq.jpg'),
    'Pelvis, transverse': ('Bladder and what lies behind it', 'pelvis_transverse.jpg'),
    'Pelvis, sagittal': ('Bladder and what lies behind it', 'pelvis_sagittal.jpg'),
}

EXAM = exam_page.Exam(
    key="pocus", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='Point-of-care ultrasound',
    lead='Every view is found the same way: choose the probe, position the patient, place the probe with its marker the right way, sweep and tilt until the view appears, then name each structure by how bright it looks. Each view below gives the probe steps and what a good view shows. The vessel and musculoskeletal views are tagged <i>later</i>: the objectives name them, but the faculty page is empty, so only the objectives are given.',
    find='Find a view (e.g. gallbladder, Morison, subxiphoid)',
    root='Choose the probe → Position the patient → Place the probe, marker the right way → Sweep and tilt → Name each structure',
    root_note='The probe marker points to the patient\'s head (or to their right in a cross-section). Fluid is black, solid organs are grey, bone and the diaphragm are bright white.',
    video_credit='Ultrasound screenshots are reused under their open licences, credited below. Each view also has a probe-position video from <a href="https://www.youtube.com/@DrSamsImagingLibrary">Dr. Sam\'s Imaging Library</a>, played from YouTube only when you tap it. Practise the probe movements on a classmate in the session.',
    general_title="General approach", general_week='Every ultrasound',
    spine_heading='Before you scan', spine_title='The view', pearls_heading='Pearls',
    other_video=json.loads((HERE / "videos_other.json").read_text(encoding="utf-8")),
    video_page="https://www.youtube.com/watch?v={slug}",
    region_video={'heart': ['izxn8kXvUGk'], 'upper': ['mRLb-tRtCp8'], 'pelvis': ['geKUmvCHrf8'],
                  'vessels': ['p4qTMQZW4sk', 'vmmrjy1bhEc', 'vIbcAv9udso']},
    count_noun='views', steps_label='Steps', pos_label='A good view',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
