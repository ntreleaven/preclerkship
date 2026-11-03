"""
Purpose: Build the Putting it together clinical skills page (consol-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Putting It Together Clinical Skills".
Author: Noor Simsam
Date: 2026-11-01
Input: the vault note (POM2_VAULT or the default vault path)
Output: consol-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Putting It Together Clinical Skills.md"


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
REGIONS = {2: ('history', 'The patient-centred history', 'T2C · Consolidation', '#3d6fb6'), 3: ('focus', 'From history to a focused exam', 'T2C · Consolidation', '#23798a'), 4: ('differential', 'Building and prioritizing the differential', 'T2C · Consolidation', '#7a3fb0'), 5: ('poc', 'The Problem-Oriented Clinical Record', 'T2C · Consolidation', '#a8366f'), 6: ('team', 'Common ground, the team and reflection', 'T2C · Consolidation', '#b4501f')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture)
TESTS = {
    'Chief complaint': ('Opening the story', None),
    'History of presenting illness (HPI)': ('Opening the story', None),
    'The illness experience (FIFE)': ('Opening the story', None),
    'Past medical history': ('Background and close', None),
    'Medications and allergies': ('Background and close', None),
    'Social and functional history': ('Background and close', None),
    'Family history and review of systems': ('Background and close', None),
    'Closing the history': ('Background and close', None),
    'Chest pain': ('The complaint tells you the exam', None),
    'Shortness of breath': ('The complaint tells you the exam', None),
    'Abdominal pain': ('The complaint tells you the exam', None),
    'Back or limb pain': ('The complaint tells you the exam', None),
    'Headache, weakness or numbness': ('The complaint tells you the exam', None),
    'Summary statement': ('From findings to a ranked list', None),
    'Generating causes': ('From findings to a ranked list', None),
    'Ranking': ('From findings to a ranked list', None),
    'Next step': ('From findings to a ranked list', None),
    'Identifying data and chief complaint': ('The write-up', None),
    'History': ('The write-up', None),
    'Physical exam': ('The write-up', None),
    'Problem list': ('The write-up', None),
    'Assessment (per problem)': ('The write-up', None),
    'Plan (per problem)': ('The write-up', None),
}

EXAM = exam_page.Exam(
    key="consol", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='Putting it together',
    lead='A full encounter, in order: the history, the focused exam its complaint calls for, a ranked differential, and the written Problem-Oriented Clinical Record. Each part gives what to do and the slip to avoid. Built from the Transition to Clerkship consolidation sessions.',
    find='Find a part (e.g. differential, problem list, FIFE)',
    root='History → Focused exam → Summary statement → Differential → Next steps → Problem-oriented record',
    root_note='Work from the patient\'s story to the exam it calls for, then say what the findings mean and what you would do next.',
    video_credit='There are no videos or pictures on this page: this is reasoning and communication, so practise it out loud.',
    general_title="General approach", general_week='Every full encounter',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='parts', steps_label='What to do', pos_label='Common slip',
)

if __name__ == "__main__":
    exam_page.build(EXAM)
