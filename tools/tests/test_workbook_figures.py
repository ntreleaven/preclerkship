# -*- coding: utf-8 -*-
"""
Purpose: keep each workbook picture on the question that asks about it. A picture
         set to the right of the text can start level with the question before
         (reader report #21: the Q51 smear was on Q49), and the bank must not
         carry it there
Author: Noor Simsam
Date: 2026-11-02
Input: tools/fom/parse_workbook.py, fom/data/questions/b1.json and b3.json
Output: pytest results
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "fom"))
pytest.importorskip("pymupdf")
import parse_workbook  # noqa: E402


def question(num: int, page: int, stem: str, imgs: int = 0) -> parse_workbook.WQ:
    """A parsed workbook question with `imgs` placeholder pictures."""
    q = parse_workbook.WQ(num, [], page)
    q.stem = [stem]
    q.imgs = [{"page": page}] * imgs
    return q


def test_picture_moves_to_the_question_that_points_at_it() -> None:
    qs = [question(49, 37, "Which of the following is most correct:", imgs=1),
          question(50, 37, "Which of the following does not cause HIT:"),
          question(51, 37, "Which finding is seen in the peripheral blood smear to the right")]
    parse_workbook.rehome_figures(qs)
    assert [len(q.imgs) for q in qs] == [0, 0, 1]


def test_picture_stays_when_its_own_question_asks_about_it() -> None:
    qs = [question(83, 41, "Shown below is a peripheral smear", imgs=1),
          question(84, 41, "Which blood film shown on the right")]
    parse_workbook.rehome_figures(qs)
    assert [len(q.imgs) for q in qs] == [1, 0]


def test_picture_never_crosses_a_page() -> None:
    qs = [question(104, 43, "Which is the most ideal method of sampling", imgs=1),
          question(105, 44, "the blood film shown on the right")]
    parse_workbook.rehome_figures(qs)
    assert [len(q.imgs) for q in qs] == [1, 0]


@pytest.mark.parametrize("bank, has, lacks", [
    ("b1", "b1-wb-fom-q25", "b1-wb-fom-q24"),
    ("b3", "b3-wb-heme-q51", "b3-wb-heme-q49"),
    ("b3", "b3-wb-heme-q105", "b3-wb-heme-q104"),
])
def test_bank_carries_the_picture_on_the_right_question(bank: str, has: str, lacks: str) -> None:
    rows = json.loads((ROOT / "fom" / "data" / "questions" / (bank + ".json")).read_text(encoding="utf-8"))
    stems = {q["qid"]: q["stem"] for q in rows}
    assert "<img" in stems[has]
    assert "<img" not in stems[lacks]
