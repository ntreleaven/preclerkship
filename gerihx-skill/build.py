"""
Purpose: Build the geriatric assessment clinical skills page (gerihx-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Geriatric Assessment Clinical Skills".
Author: Noor Simsam
Date: 2026-11-01
Input: the vault note (POM2_VAULT or the default vault path); img/credits.json for the one picture
Output: gerihx-skill/index.html

The note is the single source of the questions and what to listen for: edit the note,
then rerun this script. Which problem heading each row sits under is set here. A history is a
conversation, so its cards have no pictures, except gait, which carries one. How the page looks
lives in clinical-skills/exam_page.py, shared by every exam page.
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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Geriatric Assessment Clinical Skills.md"


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


WEEK = "CS2 · Geriatrics"
# section number in the note -> region on the page
REGIONS = {2: ('history', 'The history, with the caregiver', WEEK, '#3d6fb6'),
 3: ('function', 'Daily function', WEEK, '#2f6b4f'),
 4: ('ros', 'Geriatric review of systems', WEEK, '#a8366f'),
 5: ('mind', 'Thinking and mood', WEEK, '#7a3fb0'),
 6: ('gait', 'Gait', WEEK, '#b4501f'),
 7: ('plan', 'Problem list, plan and presenting', WEEK, '#2f5d7c')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'Presenting concern': ('The story', None),
    'Collateral from the caregiver': ('The story', None),
    'Falls and near-falls': ('Safety and medicines', None),
    'Medications and polypharmacy': ('Safety and medicines', None),
    'Screening and prevention': ('Prevention and wishes', None),
    'Wishes for care': ('Prevention and wishes', None),
    'ADLs (basic self-care)': ('Self-care', None),
    'IADLs (living independently)': ('Self-care', None),
    'Home': ('Home, help and food', None),
    'Support and money': ('Home, help and food', None),
    'Eating': ('Home, help and food', None),
    'Light-headedness': ('Dizzy, seeing, hearing', None),
    'Vision and hearing': ('Dizzy, seeing, hearing', None),
    'Teeth and mouth': ('Mouth, gut, bladder', None),
    'Bowel and bladder': ('Mouth, gut, bladder', None),
    'Weight loss': ('Weight and pain', None),
    'Pain': ('Weight and pain', None),
    'Memory and confusion': ('Thinking and mood', None),
    'Mood': ('Thinking and mood', None),
    'Gait': ('Walking', 'tandem-gait.jpg'),
}

EXAM = exam_page.Exam(
    key="gerihx", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='The geriatric assessment',
    lead='A comprehensive geriatric assessment looks at the whole older person, not one complaint: the history with a caregiver\'s view added, daily function, the extra review-of-systems questions, thinking and mood, and gait. Each part is below in the order you do it, with what to ask and what to listen for. <b>No faculty notes back this yet; built from the Clinical Skills objectives and upper-year notes.</b> Anything beyond the objectives is tagged <i>extra</i>, and where an objective has no source behind it (the older-adult gait method, the GDS depression scale, the problem list), the page says so.',
    find='Find a question or topic (e.g. falls, ADLs, collateral)',
    root='The history with the caregiver → Daily function (ADLs, IADLs) → Review of systems → Thinking and mood → Gait → Problem list and plan',
    root_note='Patient-centred: the older adult\'s own story and goals come first, and a caregiver adds a second view, with the patient\'s permission. Always think of delirium, depression and dementia.',
    video_credit='There are no videos on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud. The gait card has one picture, credited below.',
    general_title="General approach", general_week='Every geriatric assessment',
    spine_heading='Start here', spine_title='What to say', pearls_heading='Pearls',
    region_text={'mind': {'spine_title': 'The screening tests'}, 'gait': {'spine_title': 'What the objective says', 'count_noun': 'gait assessment'},
                 'plan': {'spine_title': 'What the objectives say'}},
    count_noun='areas to ask about', steps_label='Ask or do', pos_label='Listen or look for',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
