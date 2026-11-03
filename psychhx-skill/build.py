"""
Purpose: Build the psychiatric interview clinical skills page (psychhx-skill/index.html) from the
         tables in the medwiki note "Summary Notes - Psychiatric Interview Clinical Skills".
Author: Noor Simsam
Date: 2026-10-29
Input: the vault note (POM2_VAULT or the default vault path)
Output: psychhx-skill/index.html

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
NOTE = VAULT / "01 - Lectures/99 - Clinical Skills/Summary Notes - Psychiatric Interview Clinical Skills.md"


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
REGIONS = {2: ('hpi', 'Identification and the presenting illness', 'PoM 2 · Psychiatry', '#3d6fb6'),
 3: ('screen', 'The psychiatric screen', 'PoM 2 · Psychiatry', '#7a3fb0'),
 4: ('safety', 'Safety: suicide and homicide', 'PoM 2 · Psychiatry', '#b0332f'),
 5: ('pastpsych', 'Past psychiatric history', 'PoM 2 · Psychiatry', '#23798a'),
 6: ('medical', 'Medical, medications, family', 'PoM 2 · Psychiatry', '#7d6413'),
 7: ('social', 'Personal and social history', 'PoM 2 · Psychiatry', '#2f6b4f'),
 8: ('mse', 'Mental status exam', 'PoM 2 · Psychiatry', '#a8366f'),
 9: ('moca', 'Cognitive screen (MoCA)', 'PoM 2 · Psychiatry', '#4d5590'),
 10: ('wind', 'Winding down and plan', 'PoM 2 · Psychiatry', '#2f5d7c')}

# the note's opening section, shown as the first band
GENERAL = [(1, "The general approach")]

# row name as the note shows it -> (problem heading, picture). A question has no picture to show.
TESTS = {
    'The problem, openly': ('Telling the story', None),
    'A reference point': ('Telling the story', None),
    'Precipitants': ('What set it off, what it cost', None),
    'Impact': ('What set it off, what it cost', None),
    'Coping and others': ('What set it off, what it cost', None),
    'Depression': ('Mood and anxiety', None),
    'Mania or hypomania': ('Mood and anxiety', None),
    'Anxiety': ('Mood and anxiety', None),
    'Trauma': ('Mood and anxiety', None),
    'Obsessive-compulsive disorder (OCD)': ('Mood and anxiety', None),
    'Psychosis': ('Reality, eating and substances', None),
    'Eating disorder': ('Reality, eating and substances', None),
    'Substance use': ('Reality, eating and substances', None),
    'Safety': ('Risk', None),
    'Ideation': ('Thoughts of dying', None),
    'How it feels to them': ('Thoughts of dying', None),
    'Plan': ('Thoughts of dying', None),
    'Access to means': ('Thoughts of dying', None),
    'Intent': ('Thoughts of dying', None),
    'Past attempts': ('Past and present risk', None),
    'Warning signs': ('Past and present risk', None),
    'Protective factors': ('Past and present risk', None),
    'Homicidal thoughts': ('Risk to others', None),
    'Mood disorders': ('Medical problems that come with it', None),
    'Schizophrenia, bipolar disorder': ('Medical problems that come with it', None),
    'Substance use: medical complications': ('Medical problems that come with it', None),
    'OCD': ('Medical problems that come with it', None),
    'Family history': ('Family', None),
    'Development': ('Growing up', None),
    'Childhood adversity': ('Growing up', None),
    'School': ('Growing up', None),
    'Personality': ('Growing up', None),
    'Relationships and supports': ('Adult life', None),
    'Sexual history': ('Adult life', None),
    'Legal history': ('Adult life', None),
    'Occupation': ('Adult life', None),
    'Appearance': ('How they look and act', None),
    'Behaviour': ('How they look and act', None),
    'Cooperation': ('How they look and act', None),
    'Speech': ('How they talk and think', None),
    'Thought form': ('How they talk and think', None),
    'Thought content': ('How they talk and think', None),
    'Affect': ('How they feel', None),
    'Mood': ('How they feel', None),
    'Perception': ('What they perceive', None),
    'Level of consciousness': ('What they perceive', None),
    'Insight and judgement': ('Judging the patient', None),
    'Cognition': ('Judging the patient', None),
    'Knowledge and intelligence': ('Judging the patient', None),
    'Endings: safety': ('Judging the patient', None),
    'Reliability': ('Judging the patient', None),
    'Visuospatial and executive': ('Planning and abstraction', None),
    'Abstraction': ('Planning and abstraction', None),
    'Memory: learning': ('Memory and attention', None),
    'Attention': ('Memory and attention', None),
    'Delayed recall': ('Memory and attention', None),
    'Naming': ('Language and place', None),
    'Language': ('Language and place', None),
    'Orientation': ('Language and place', None),
}

EXAM = exam_page.Exam(
    key="psychhx", folder=HERE, note=plain_note(NOTE), regions=REGIONS, general=GENERAL, tests=TESTS, opening={},
    h1='The psychiatric interview',
    lead='The mental status exam is gathered the whole way through, not as a separate step. Each part of the interview is below: what to say to open it, then what to ask or assess, grouped by what you are working out, and what to listen for. Built from the PoM 2 psychiatry lectures and the CS2 Psychiatry objectives. Safety is asked about in every psychiatric interview.',
    find='Find a question or domain (e.g. mania, SIGECAPS, affect)',
    root='Identification → Presenting illness → Psychiatric screen → Past psychiatric history → Medical history and medications → Family → Personal and social → Wind down, formulation, plan',
    root_note='Two components, held in balance: content (information, symptoms) and process (rapport, empathy). The mental status exam is gathered the whole way through.',
    video_credit='There are no videos or pictures on this page: a history is a conversation, so the skill is in what you say and what you listen for. Practise the questions out loud.',
    general_title="General approach", general_week='Every psychiatric interview',
    spine_heading='How to open it', spine_title='What to say', pearls_heading='Pearls',
    count_noun='areas to ask about', steps_label='Ask or assess', pos_label='Listen for',
)


if __name__ == "__main__":
    exam_page.build(EXAM)
