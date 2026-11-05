# -*- coding: utf-8 -*-
"""Build the index behind the landing page's search of the whole portal.

Purpose: one file that holds every practice question, lecture note, interactive chart and
         clinical skills card as plain text, with the course, block, week and source each
         came from, so the front door can search all of it and filter by any of those.
Author:  Noor Sims (with Claude Code)
Date:    2026-11-04
Input:   tools/portal.py's roster, each course's data/questions and data/notes JSON
         (a chart figure's "interactive" link names its chart page), and the clinical skills exam pages (*-exam/index.html)
Output:  search.json at the repo root, read by search.js on index.html

Run from the repo root, before build_hub.py: the hub stamps this file's hash into the
address search.js fetches, so a rebuilt index is a new address rather than a stale cache.

A row is a list, not an object, because the keys would be most of the file:
    [source, course, block, week, family, title, text, target]
source is "q" (question), "n" (lecture note), "c" (interactive chart) or "k" (clinical
skills). text is what the search reads; the page cuts its snippet from it. target is the
question's id or the note's key, which search.js builds the link from, and for a chart or a
clinical skills card the address itself.
"""

import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portal

OUT = "search.json"
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
EXAM_CARD = re.compile(r'<article class="test"[^>]*>(.*?)</article>', re.S)
EXAM_TITLE = re.compile(r"<h1>(.*?)</h1>", re.S)
# a note's text stops being useful to search long before a long note ends; the
# lecture's own name and its first few thousand characters find it
NOTE_CHARS = 6000
# the explanation is searched for its opening, which names the answer and why; the rest
# of it doubled the file
ANSWER_CHARS = 300


def plain(markup):
    """Visible text of an HTML fragment, on one line."""
    text = WIKILINK.sub(lambda m: m.group(2) or m.group(1), markup or "")
    text = TAG.sub(" ", text)
    return SPACE.sub(" ", html.unescape(text)).strip()


def block_text(b):
    """The words a note block shows."""
    if b.get("t") == "table":
        cells = list(b.get("cols") or [])
        for row in b.get("rows") or []:
            cells.extend(row)
        return plain(b.get("lead", "")) + " " + plain(" ".join(cells))
    if b.get("t") == "figure":
        return plain(b.get("cap", ""))
    if b.get("t") == "callout":
        return plain(b.get("title", "")) + " " + plain(b.get("html", ""))
    if b.get("t") == "pathway":
        return plain(b.get("title", "")) + " " + plain(b.get("src", "") if isinstance(b.get("src"), str) else "")
    return plain(b.get("html", ""))


def questions(course, slug):
    path = os.path.join(course["slug"], "data", "questions", "%s.json" % slug)
    if not os.path.exists(path):
        return []
    rows = []
    for q in json.load(io.open(path, encoding="utf-8")):
        if q.get("retired"):
            continue
        pre = q.get("preamble") or ""
        if isinstance(pre, dict):
            pre = pre.get("html", "")
        opts = " ".join(plain(o.get("html", "")) for o in q.get("options") or [])
        text = " ".join(x for x in (plain(pre), plain(q.get("stem", "")), opts,
                                    plain(q.get("answer", ""))[:ANSWER_CHARS]) if x)
        title = "Q%s · %s" % (q.get("num", ""), q.get("lecture") or q.get("sourceLabel") or "")
        rows.append(["q", course["slug"], slug, q.get("week") or 0, q.get("family", ""), title, text, q["qid"]])
    return rows


def notes(course, slug):
    path = os.path.join(course["slug"], "data", "notes", "%s.json" % slug)
    if not os.path.exists(path):
        return []
    rows = []
    used = set()
    for week in json.load(io.open(path, encoding="utf-8"))["weeks"]:
        for lec in week["lectures"]:
            # notes.js keys a note by its id, numbering a repeat; the link has to match
            base = lec.get("id") or "lec"
            key, n = base, 2
            while key in used:
                key, n = "%s--%d" % (base, n), n + 1
            used.add(key)
            if lec.get("hasNote") is not True:
                continue
            parts = [lec.get("title", ""), plain(lec.get("framing", "")), plain(lec.get("keypoints", ""))]
            parts += [block_text(b) for b in lec.get("blocks") or []]
            text = SPACE.sub(" ", " ".join(p for p in parts if p)).strip()[:NOTE_CHARS]
            title = ("%s %s" % (lec.get("num", ""), lec["name"])).strip()
            rows.append(["n", course["slug"], slug, week.get("n") or 0, "", title, text, key])
    return rows


def charts(course):
    """One row per interactive chart, filed under the block and week of the lecture it opens from."""
    rows, seen = [], set()
    for slug, _n, _name, _weeks in course["blocks"]:
        npath = os.path.join(course["slug"], "data", "notes", "%s.json" % slug)
        if not os.path.exists(npath):
            continue
        for week in json.load(io.open(npath, encoding="utf-8"))["weeks"]:
            for lec in week["lectures"]:
                for b in lec.get("blocks") or []:
                    href = b.get("interactive")
                    if b.get("t") != "figure" or not href or href in seen:
                        continue
                    seen.add(href)
                    name = re.sub(r"\.svg$", "", b.get("alt", "")).strip()
                    title = name[:1].upper() + name[1:]
                    text = "%s %s interactive chart" % (title, lec["name"])
                    rows.append(["c", course["slug"], slug, week.get("n") or 0, "", title, text,
                                 "%s/%s" % (course["slug"], href)])
    return rows


def clinical_skills():
    """One row per exam card on the clinical skills exam pages."""
    rows = []
    for page in sorted(os.listdir(".")):
        path = os.path.join(page, "index.html")
        if not page.endswith("-exam") or not os.path.exists(path):
            continue
        src = io.open(path, encoding="utf-8").read()
        m = EXAM_TITLE.search(src)
        exam = plain(m.group(1)).split(":")[0] if m else page
        for card in EXAM_CARD.findall(src):
            h = re.search(r"<h4>(.*?)</h4>", card, re.S)
            if not h:
                continue
            title = "%s · %s" % (exam, plain(h.group(1)))
            rows.append(["k", "cs", page, 0, "", title, plain(card)[:1500], "%s/" % page])
    return rows


def main():
    rows = []
    meta = {"courses": [], "families": {}}
    for course in portal.COURSES:
        if not course["blocks"]:
            continue
        meta["courses"].append({
            "slug": course["slug"], "name": course["name"], "short": course["short"],
            "blocks": [[slug, name] for slug, _n, name, _w in course["blocks"]],
        })
        for f in course["families"]:
            meta["families"].setdefault(f["key"], f["name"])
        for slug, _n, _name, _weeks in course["blocks"]:
            rows += notes(course, slug)
            rows += questions(course, slug)
        rows += charts(course)
    meta["courses"].append({"slug": "cs", "name": "Clinical Skills", "short": "Clinical Skills", "blocks": []})
    rows += clinical_skills()
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps({"meta": meta, "rows": rows}, ensure_ascii=False, separators=(",", ":")) + "\n")
    by = {}
    for r in rows:
        by[r[0]] = by.get(r[0], 0) + 1
    print("%s: %d rows (%s), %.1f MB" % (OUT, len(rows), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                         os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    main()
