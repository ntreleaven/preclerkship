"""
Purpose: Build the paediatric history clinical skills page (pedshx-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Paediatric History Clinical Skills".
Author: Noor Simsam
Date: 2026-11-01
Input: the vault note (POM2_VAULT or the default vault path)
Output: pedshx-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Paediatric History Clinical Skills.md"


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


WEEK = "CS2 · Pediatrics Focused History"
# section number in the note -> region on the page
REGIONS = {2: ('who', 'Who is there and why', WEEK, '#3d6fb6'),
 3: ('birth', 'Before and around birth', WEEK, '#7a3fb0'),
 4: ('feeding', 'Feeding and growth', WEEK, '#23798a'),
 5: ('develop', 'Development, hearing and vision', WEEK, '#a8366f'),
 6: ('health', 'Health so far', WEEK, '#b4501f'),
 7: ('social', 'Home, school and safety', WEEK, '#2f6b4f'),
 8: ('teen', 'The adolescent history (HEADSSS)', WEEK, '#b0332f'),
 9: ('closing', 'Closing the visit', WEEK, '#2f5d7c'),
 10: ('ward', 'The ward visit: examining a child', 'CS2 · Pediatric Ward Visits', '#4d5590')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'Who is with the child': ('Opening the visit', None),
    'The story, from both': ('Opening the visit', None),
    'Antenatal (pregnancy)': ('Pregnancy, birth, the newborn weeks', None),
    'Birth': ('Pregnancy, birth, the newborn weeks', None),
    'Post-natal (newborn period)': ('Pregnancy, birth, the newborn weeks', None),
    'Feeding': ('Feeding and growing', None),
    'Growth': ('Feeding and growing', None),
    'Developmental milestones': ('Keeping pace', None),
    'Hearing and vision': ('Keeping pace', None),
    'Immunizations': ('Vaccines and illness', None),
    'Past illness and surgery': ('Vaccines and illness', None),
    'Medications and allergies': ('Medicines and family', None),
    'Family history': ('Medicines and family', None),
    'Household': ('Home and school', None),
    'School': ('Home and school', None),
    'Risk of harm to the child': ('Their safety', None),
    'Time alone and confidentiality': ('Setting it up', None),
    'Home': ('Home, school and friends', None),
    'Education and employment': ('Home, school and friends', None),
    'Activities': ('Home, school and friends', None),
    'Drugs': ('Habits and body', None),
    'Sex': ('Habits and body', None),
    'Suicide (mood)': ('Mood and safety', None),
    'Safety': ('Mood and safety', None),
}

EXAM = exam_page.Exam(
    key="pedshx", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='The paediatric history',
    lead='A paediatric history is the usual history with the child\'s whole story added: the pregnancy and birth, feeding and growth, development and vaccines, then home and school. A teenager is also asked on their own. Each part is below in the order you do it, with what to ask and what to listen for. <b>No faculty notes back this yet; built from the Clinical Skills objectives and upper-year notes.</b> Anything beyond the objectives is tagged <i>extra</i>, and where an objective has no source behind it, the page says so.',
    find='Find a question or topic (e.g. birth, vaccines, HEADSSS)',
    root='Who is there → Pregnancy, birth and newborn → Feeding and growth → Development → Health so far → Home, school, safety → The teenager alone (HEADSSS) → Closing',
    root_note='Family-centred: ask the child as well as the caregiver, in words that suit the child\'s age, without judging. A teenager is asked part of the history on their own, in confidence.',
    video_credit='There are no videos or pictures on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud.',
    general_title="General approach", general_week='Every paediatric history',
    spine_heading='Start here', spine_title='What to say', pearls_heading='Pearls',
    region_text={'closing': {'spine_title': 'How to finish'}, 'ward': {'spine_title': 'What the objectives say'}},
    count_noun='areas to ask about', steps_label='Ask', pos_label='Listen for',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
