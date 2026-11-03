"""
Purpose: Build the presenting a case clinical skills page (present-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Presenting a Case Clinical Skills".
Author: Noor Simsam
Date: 2026-10-29
Input: the vault note (POM2_VAULT or the default vault path)
Output: present-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Presenting a Case Clinical Skills.md"


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
REGIONS = {2: ('oral', 'The oral presentation', 'FoM · Introduction to Interviewing', '#3d6fb6'),
 3: ('exam', 'Reporting the physical exam', 'FoM · Primary Physical Exam Skills', '#23798a'),
 4: ('plan', 'Summary, differential and plan', 'T2C · Surgery, Consolidation', '#7a3fb0'),
 5: ('record', 'The written record', 'T2C · Consolidation', '#a8366f'),
 6: ('surgical', 'A surgical patient', 'T2C · Surgery', '#b4501f'),
 7: ('after', 'After the presentation', 'T2C · Consolidation', '#2f6b4f')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'Identification and chief complaint': ('Who and why', None),
    'History of presenting illness': ('Who and why', None),
    "The patient's illness experience (FIFE)": ('Who and why', None),
    'Past medical history': ('The background', None),
    'Medications and allergies': ('The background', None),
    'Habits and social history': ('The background', None),
    'Family history': ('The background', None),
    'Review of systems': ('What you found', None),
    'Physical exam': ('What you found', None),
    'History': ('The database', None),
    'Physical exam (write-up)': ('The database', None),
    'Problem list': ('Your reasoning', None),
    'Assessment and plan, per problem': ('Your reasoning', None),
    'Learning issues': ('Your reasoning', None),
}

EXAM = exam_page.Exam(
    key="present", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='Presenting a case',
    lead='A case is presented in the same order the history was taken. Each part is below with what to say and the slip to avoid, then the summary, differential and plan, and the written Problem-Oriented Clinical Record. Built from the Clinical Skills objectives and the faculty Interviewing Template; anything taught in the T2C Surgery and Consolidation sessions is tagged <i>later</i>.',
    find='Find a part (e.g. FIFE, differential, plan)',
    root='Identification and chief complaint → HPI (FIFE) → Past history, medications → Habits and social → Family → Review of systems → Physical exam → One-line summary → Problem list and differential → Plan',
    root_note='Clear and concise, in the order of the interviewing template: say what matters for this problem, the findings that are present and the ones that are absent.',
    video_credit='There are no videos or pictures on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud.',
    general_title="General approach", general_week='Every presentation',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='parts', steps_label='What to say', pos_label='Common slip',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
