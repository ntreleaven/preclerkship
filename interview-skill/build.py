"""
Purpose: Build the patient-centred interview clinical skills page (interview-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Patient-Centred Interview Clinical Skills".
Author: Noor Simsam
Date: 2026-10-29
Input: the vault note (POM2_VAULT or the default vault path)
Output: interview-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Patient-Centred Interview Clinical Skills.md"


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
REGIONS = {2: ('complaint', 'Chief complaint', 'FoM · Introduction to Interviewing', '#3d6fb6'),
 3: ('hpi', 'History of presenting illness', 'FoM · Introduction to Interviewing', '#23798a'),
 4: ('fife', 'The illness experience (FIFE)', 'FoM · Introduction to Interviewing', '#7a3fb0'),
 5: ('pmh', 'Past medical history', 'FoM · Introduction to Interviewing', '#a8366f'),
 6: ('meds', 'Medications and allergies', 'FoM · Introduction to Interviewing', '#b4501f'),
 7: ('habits', 'Habits', 'FoM · Introduction to Interviewing', '#7d6413'),
 8: ('social', 'Social history', 'FoM · Introduction to Interviewing', '#2f6b4f'),
 9: ('family', 'Family history', 'FoM · Introduction to Interviewing', '#4d5590'),
 10: ('ros', 'Review of systems', 'FoM · Introduction to Interviewing', '#8c3566'),
 11: ('closing', 'Closing', 'FoM · Introduction to Interviewing', '#2f5d7c'),
 12: ('advanced', 'Advanced interviewing', 'PoM 1 · Advanced Interviewing', '#4b3f96')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'Site': ('Characterize the symptom', None),
    'Character': ('Characterize the symptom', None),
    'Radiation': ('Characterize the symptom', None),
    'Severity': ('Characterize the symptom', None),
    'Onset': ('Its course', None),
    'Timeline': ('Its course', None),
    'Associated symptoms': ('What changes it, what comes with it', None),
    'Exacerbating / relieving factors': ('What changes it, what comes with it', None),
    'Feelings': ('What they feel and think', None),
    'Ideas': ('What they feel and think', None),
    'Function': ('What it changes, what they want', None),
    'Expectations': ('What it changes, what they want', None),
    'Major illnesses': ('Illness and surgery so far', None),
    'Hospitalizations': ('Illness and surgery so far', None),
    'Surgeries': ('Illness and surgery so far', None),
    'Mental health history': ('Illness and surgery so far', None),
    'Vaccines': ('Staying well', None),
    'Prevention and safety': ('Staying well', None),
    'Screening': ('Staying well', None),
    'Last doctor visit': ('Staying well', None),
    'Prescriptions': ('What they take', None),
    'Non-prescription': ('What they take', None),
    'Dose and frequency': ('What they take', None),
    'Purpose': ('What they take', None),
    'Adherence and aids': ('Taking it safely', None),
    'Allergies': ('Taking it safely', None),
    'Caffeine': ('Everyday substances', None),
    'Smoking / vaping': ('Everyday substances', None),
    'Alcohol': ('Everyday substances', None),
    'Drugs': ('Everyday substances', None),
    'Exercise': ('Daily living', None),
    'Diet': ('Daily living', None),
    'Sleep': ('Daily living', None),
    'Safety': ('Home and safety', None),
    'Relationships and support': ('Home and safety', None),
    'Work and finances': ('Work and independence', None),
    'ADLs': ('Work and independence', None),
    'IADLs': ('Work and independence', None),
    'Exposures and travel': ('Work and independence', None),
    'General': ('Whole body and senses', None),
    'Head, eyes, ears, nose, throat (HEENT)': ('Whole body and senses', None),
    'Respiratory': ('Chest and circulation', None),
    'Cardiovascular': ('Chest and circulation', None),
    'Gastrointestinal': ('Abdomen and pelvis', None),
    'Urologic': ('Abdomen and pelvis', None),
    'Gynecologic and obstetric': ('Abdomen and pelvis', None),
    'Sexual': ('Abdomen and pelvis', None),
    'Musculoskeletal': ('Muscles, nerves, hormones', None),
    'Neurologic': ('Muscles, nerves, hormones', None),
    'Endocrine': ('Muscles, nerves, hormones', None),
    'Psychiatric': ('Mood and safety', None),
    # advanced interviewing: situations, grouped by the kind of conversation
    'Ethical framework': ('Ethics and the law', None),
    'Professional boundaries': ('Ethics and the law', None),
    'Confidentiality and its limits': ('Ethics and the law', None),
    'Age of consent': ('Ethics and the law', None),
    'STI counselling and reporting': ('Ethics and the law', None),
    'Prescribing narcotics': ('Ethics and the law', None),
    "Children's Aid Society": ('Ethics and the law', None),
    'Breaking bad news': ('Hard conversations', None),
    'Grief and death with dignity': ('Hard conversations', None),
    'Organ and tissue donation': ('Hard conversations', None),
    'The "difficult" patient': ('Difficult encounters', None),
    'Drug seeking': ('Difficult encounters', None),
    "A colleague's professionalism": ('Difficult encounters', None),
    "An illness you don't know": ('Difficult encounters', None),
    'Impact of disease on life': ('Life situation', None),
    'Adherence and money': ('Life situation', None),
    'Abuse (physical or sexual)': ('Safety', None),
    'Cultural competency (CHAT)': ('Culture and identity', None),
    'Language other than English': ('Culture and identity', None),
    'Shared decision-making and culture': ('Culture and identity', None),
    'Indigenous patients': ('Culture and identity', None),
    'LGBTQ+ patients': ('Culture and identity', None),
    'Gynecological history, sensitively': ('Culture and identity', None),
}

EXAM = exam_page.Exam(
    key="interview", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='The patient-centred interview',
    lead='Every history runs on the same spine. Each part of the interview is below in the order you do it: what to say to open it, then the questions to ask, grouped by what you are working out, and what to listen for in the answer. Built from the faculty Interviewing Template and the Clinical Skills objectives; anything only the PoM 1 Advanced Interviewing block teaches is tagged <i>later</i>.',
    find='Find a question or topic (e.g. FIFE, alcohol, ROS)',
    root='Introduction and consent → Chief complaint → History of presenting illness (FIFE) → Past history → Medications and allergies → Habits → Social → Family → Review of systems → Closing summary',
    root_note="The patient's agenda comes first, without losing sight of yours. Organized, yet organic: keep to the order, follow the patient's lead, and signpost where you are going next.",
    video_credit='The "Doctor Patient Introduction" clip is from the <a href="https://rsc.lib.uwo.ca/s/healthedu/item-set">Health Education Media Library</a> (Western Libraries; Clinical Neurological Sciences, Schulich School of Medicine and Dentistry), CC BY-NC 4.0, played from the library\'s own server and opened only when you tap it. There are no videos or pictures on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud.',
    clips={"The general approach": [{"mp4": "https://rsc.lib.uwo.ca/files/original/330d82ebb98681351f7e1f0a77127f490bfdf69a.mp4",
                                     "title": "Doctor Patient Introduction", "page": "https://rsc.lib.uwo.ca/s/healthedu/item/2429", "secs": 21}]},
    general_title="General approach", general_week='Every interview',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='areas to ask about', steps_label='Ask', pos_label='Listen for',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
