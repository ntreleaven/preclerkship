"""
Purpose: Build the How a station runs clinical skills page (station-skill/index.html) from the
         tables in the medwiki note "Summary Notes - How a Station Runs Clinical Skills".
Author: Noor Simsam
Date: 2026-11-01
Input: the vault note (POM2_VAULT or the default vault path)
Output: station-skill/index.html

The note is the single source of the questions and what to listen for: edit the note,
then rerun this script. Which problem heading each row sits under is set here. A history
is a conversation, so its cards have no pictures. How the page looks lives in
clinical-skills/exam_page.py, shared by every exam page.
"""

import importlib.util
import os
import re
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exam_page", HERE.parent / "clinical-skills/exam_page.py")
exam_page = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exam_page)
VAULT = Path(os.environ.get("POM2_VAULT", "/mnt/c/Users/nsims/medwiki"))
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - How a Station Runs Clinical Skills.md"


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
REGIONS = {2: ('door', 'Reading the door', 'TOSCE and OSCE', '#3d6fb6'), 3: ('marked', 'What is marked', 'TOSCE and OSCE', '#23798a'), 4: ('openings', 'Opening lines for each exam', 'PPES · FoM and PoM 1', '#7a3fb0'), 5: ('histsta', 'History stations', 'Interviewing · FoM to T2C', '#a8366f'), 6: ('closing', 'Closing and reporting', 'TOSCE and OSCE', '#b4501f'), 7: ('versus', 'TOSCE versus OSCE', 'FoM to T2C', '#2f6b4f')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture)
TESTS = {
    'Communication': ('Talking with the patient', None),
    'Physical exam technique': ('Doing the exam', None),
    'Organization': ('Doing the exam', None),
    'Professionalism': ('Looking after the patient', None),
    'Clinical reasoning (OSCE, some TOSCE stations)': ('Thinking it through', None),
    'Accepting feedback (TOSCE)': ('Thinking it through', None),
    'Vital signs and general inspection (PPES Week 1)': ('Chest and belly', None),
    'Respiratory (PPES Week 2)': ('Chest and belly', None),
    'Abdomen (PPES Week 3)': ('Chest and belly', None),
    'Cardiovascular (PPES Week 4)': ('Chest and belly', None),
    'Head and neck (PPES Week 7)': ('Head, nerves and joints', None),
    'Neurological (PPES Weeks 8 and 9)': ('Head, nerves and joints', None),
    'Musculoskeletal (PPES Week 10)': ('Head, nerves and joints', None),
    'The warning signal': ('Ending well', None),
    'Thanking and covering the patient': ('Ending well', None),
    'The summary': ('Ending well', None),
    'Purpose': ('What differs', None),
    'Content': ('What differs', None),
    'Feedback': ('What differs', None),
    'Marking': ('What differs', None),
}

EXAM = exam_page.Exam(
    key="station", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='How a station runs',
    lead='Every station runs the same way: read the door, knock and introduce yourself, do the task out loud, then close and report. Below is what each station marks, the opening line for each exam, and how to finish. Built from the course Clinical Skills material and the course syllabi; no station scenario or marking sheet is reproduced.',
    find='Find a topic (e.g. draping, hand hygiene, summary)',
    root='Read the door → Knock, introduce, consent → Do the task out loud → Close the encounter → Report to the examiner',
    root_note='The patient comes first (comfort, consent, privacy), and the examiner can only mark what they see and hear, so say what you are doing and what you find.',
    video_credit='There are no videos or pictures on this page: a station is a performance, so practise it out loud with a partner.',
    general_title="General approach", general_week='Every station',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='topics', steps_label='What to do', pos_label='Common slip',
)

if __name__ == "__main__":
    exam_page.build(EXAM)
