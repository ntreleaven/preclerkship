"""
Purpose: Build the cultural humility clinical skills page (humility-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Cultural Humility Clinical Skills".
Author: Noor Simsam
Date: 2026-10-29
Input: the vault note (POM2_VAULT or the default vault path)
Output: humility-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Cultural Humility Clinical Skills.md"


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
REGIONS = {2: ('gender', 'Gender-expansive care', 'PoM 1 · Cultural Humility', '#8c3566'),
 3: ('loe', 'Language other than English', 'PoM 1 · Cultural Humility', '#23798a'),
 4: ('culture', 'Culture across the interview', 'PoM 1 · Advanced Interviewing', '#4d5590'),
 5: ('reflect', 'Closing and reflecting', 'PoM 1 · Cultural Humility', '#2f6b4f')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'Name': ('Names and respect', None),
    'Pronouns': ('Names and respect', None),
    'Past experiences of care': ('Names and respect', None),
    'Gender-affirming care': ('Body and relationships', None),
    'Sexual history': ('Body and relationships', None),
    'Support and safety': ('Body and relationships', None),
    'Language': ('Reaching the patient', None),
    "The patient's own words": ('Reaching the patient', None),
    'Understanding at the end': ('Reaching the patient', None),
    'Immigration experience': ('Their situation', None),
    'Unique health challenges': ('Their situation', None),
    'Beliefs about the illness': ('Their situation', None),
}

EXAM = exam_page.Exam(
    key="humility", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='Cultural humility in the interview',
    lead='The interview is the same patient-centred spine as always, with two adaptations: gender-expansive care, and interviews in a language other than English. The patient is the expert on their own identity, culture and story, so you ask rather than assume. Built from the Cultural Humility Communication Block objectives; anything only Advanced Interviewing teaches is tagged <i>later</i>.',
    find='Find a question (e.g. pronouns, translator)',
    root='Introduction and consent → Chief complaint → History of presenting illness (FIFE) → Past history → Medications and allergies → Habits → Social → Family → Review of systems → Closing summary',
    root_note='Ask rather than assume, and recognize and address your own implicit biases.',
    video_credit='There are no videos or pictures on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud.',
    general_title="General approach", general_week='Every interview',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='areas to ask about', steps_label='Ask', pos_label='Listen for',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
