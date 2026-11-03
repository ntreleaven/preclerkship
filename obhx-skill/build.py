"""
Purpose: Build the obstetric and gynecologic history clinical skills page (obhx-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Obstetric and Gynecologic History Clinical Skills".
Author: Noor Simsam
Date: 2026-10-29
Input: the vault note (POM2_VAULT or the default vault path)
Output: obhx-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Obstetric and Gynecologic History Clinical Skills.md"


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
REGIONS = {2: ('gynsx', 'Gynecologic symptoms', 'PoM 2 · OB/Gyn history', '#8c3566'),
 3: ('menstrual', 'Menstrual history', 'PoM 2 · OB/Gyn history', '#a8366f'),
 4: ('obhist', 'Obstetric history', 'PoM 2 · OB/Gyn history', '#7a3fb0'),
 5: ('background', 'Past, medications, family, social', 'PoM 2 · OB/Gyn history', '#b4501f'),
 6: ('opr', 'The pregnant patient', 'PoM 2 · Ontario Perinatal Record', '#23798a'),
 7: ('wrap', 'Wrapping up', 'PoM 2 · OB/Gyn history', '#2f6b4f')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'Vaginal bleeding': ('Bleeding and pain', None),
    'Abdominal or pelvic pain': ('Bleeding and pain', None),
    'Dyspareunia (painful sex)': ('Bleeding and pain', None),
    'Vaginal discharge': ('Discharge and skin', None),
    'Vulvar itching, skin changes': ('Discharge and skin', None),
    'Infertility': ('Conceiving', None),
    'Menarche': ('Key dates', None),
    'Last menstrual period (LMP)': ('Key dates', None),
    'Previous menstrual period': ('Key dates', None),
    'Postmenopausal patients': ('Key dates', None),
    'Past problems': ('The pattern', None),
    'Cycle length and regularity': ('The pattern', None),
    'Days of bleeding': ('The pattern', None),
    'How heavy': ('Bleeding and pain now', None),
    'Current bleeding problems': ('Bleeding and pain now', None),
    'Pain and premenstrual symptoms': ('Bleeding and pain now', None),
    'Gestation': ('How each pregnancy went', None),
    'Mode of delivery': ('How each pregnancy went', None),
    'Sex and birth weight': ('How each pregnancy went', None),
    'Complications': ('How each pregnancy went', None),
    'Assisted reproduction (ART)': ('How it began and who cared', None),
    'Care providers': ('How it began and who cared', None),
    'Earlier losses': ('Pregnancies that ended early', None),
    'Ectopic pregnancy': ('Pregnancies that ended early', None),
    'Contraception': ('Treatment and prevention', None),
    'Hormone replacement therapy (HRT)': ('Treatment and prevention', None),
    'Other medications': ('Treatment and prevention', None),
    'Allergies': ('Treatment and prevention', None),
    'Immunizations': ('Treatment and prevention', None),
    'Family history': ('Risk from family and lifestyle', None),
    'Weight and diet': ('Risk from family and lifestyle', None),
    'Occupation, home, finances': ('Risk from family and lifestyle', None),
    'Substance use': ('Risk from family and lifestyle', None),
    'Current pregnancy': ('This pregnancy', None),
    'Nutrition': ('This pregnancy', None),
    'Medical and surgical history': ('Health that changes care', None),
    'Genetic history': ('Health that changes care', None),
    'Infectious disease': ('Health that changes care', None),
    'Mental health': ('Mind, habits and home', None),
    'Substance use in pregnancy': ('Mind, habits and home', None),
    'Lifestyle and social': ('Mind, habits and home', None),
}

EXAM = exam_page.Exam(
    key="obhx", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='Obstetric and gynecologic history',
    lead='These are private questions, so explain why you are asking and ask without judgment. Each part of the history is below in the order you take it: what to say to open it, then the questions to ask, grouped by what you are working out, and what to listen for. Built from the faculty OB/Gyne History Gathering Reference and the Ontario Perinatal Record.',
    find='Find a question (e.g. LMP, GTPAL, bleeding)',
    root='Presenting complaint → Gynecologic symptoms → Menstrual history → Obstetric history → Past history, medications, family, social → Review of systems → Summary and FIFE',
    root_note='The Ontario Perinatal Record is the checklist for a pregnant patient. Ask about pregnancy losses gently: the patient chooses how much to share.',
    video_credit='There are no videos or pictures on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud.',
    general_title="General approach", general_week='Every OB/Gyn history',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='areas to ask about', steps_label='Ask', pos_label='Listen for',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
