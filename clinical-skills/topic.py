"""
Purpose: Build one page per clinical skills topic (every topic without its own exam page:
         a physical exam with a <system>-exam/ folder, built by exam_page.py the way MSK is,
         is left to that) from its vault note "Summary Notes - <Name> Clinical Skills.md",
         in the portal's structure: the clinical skills block bar, a masthead, then each
         section's steps and its table of manoeuvres as cards, with Look and Test modes.
Author: Noor Simsam
Date: 2026-10-28
Input: the notes in <vault>/01 - Lectures/99 - Clinical Skills/ (POM2_VAULT or the default
       vault path), each with a cs_key in its frontmatter; SECTIONS and SKILLS in build.py
Output: clinical-skills/<key>.html for every note found; prints which topics have no note

The note is the single source: edit the note, then rerun this script and build.py.
"""

import html
import importlib.util
import logging
import os
import re
from pathlib import Path

LOG = logging.getLogger("clinical_skills_topic")
HERE = Path(__file__).resolve().parent
VAULT = Path(os.environ.get("POM2_VAULT", "/mnt/c/Users/nsims/medwiki"))
NOTES = VAULT / "01 - Lectures/99 - Clinical Skills"

_spec = importlib.util.spec_from_file_location("clinical_skills", HERE / "build.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

TEST_HINT = "Test: tap a card to show its steps, then tap again for the answer."
LOOK_HINT = "Look: everything shown."

STYLE = """<style>
.cs-tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:4px 0 6px;position:sticky;top:0;z-index:5;
  padding:10px 0;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--border)}
.cs-mode{display:inline-flex;border:1px solid var(--border);border-radius:999px;overflow:hidden;background:var(--card-bg)}
.cs-mode button{border:0;background:none;color:var(--text);font:500 .85rem var(--sans);padding:7px 14px;cursor:pointer}
.cs-mode button[aria-pressed="true"]{background:var(--q-accent,var(--accent));color:#fff}
.cs-tools input{flex:1;min-width:180px;font:.88rem var(--sans);padding:8px 12px;border-radius:999px;border:1px solid var(--border);background:var(--card-bg);color:var(--text)}
.cs-hint{width:100%;margin:0;font-size:.8rem;color:var(--muted)}
.cs-sec{margin-top:30px;scroll-margin-top:80px}
.cs-sec>h2{font-family:var(--serif);font-size:1.4rem;font-weight:600;display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline}
.cs-sec>h2 .n{color:var(--q-accent-ink,var(--accent))}
.cs-sec>h2 small{font-family:var(--sans);font-size:.72rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.cs-steps{margin-top:12px;padding:16px 20px;background:var(--card-bg);border:1px solid var(--border);border-radius:8px;font-size:.92rem;line-height:1.6}
.cs-steps ul{margin:0;padding-left:1.1em}.cs-steps ul ul{margin-top:2px;color:var(--muted)}
.cs-steps li{margin:3px 0}
.cs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-top:12px}
.cs-card{background:var(--card-bg);border:1px solid var(--border);border-top:3px solid var(--q-accent,var(--accent));border-radius:8px;padding:14px 16px;font-size:.88rem;line-height:1.55}
.cs-card h3{font-family:var(--serif);font-size:1.05rem;font-weight:600;margin:0 0 4px}
.cs-card .for{color:var(--muted);margin:0 0 8px}
.cs-card .lbl{display:block;font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:8px 0 2px}
.cs-card ol{margin:0;padding-left:1.2em}
.cs-card .ans{margin-top:8px;padding:8px 10px;border-radius:6px;background:var(--q-accent-soft,var(--accent-soft))}
.cs-pearls{margin-top:12px;padding:12px 18px;border-left:3px solid var(--q-accent,var(--accent));background:var(--card-bg);border-radius:0 8px 8px 0;font-size:.9rem}
.cs-pearls ul{margin:0;padding-left:1.1em}
mark{background:color-mix(in srgb,#ffd84d 55%,transparent);color:inherit;padding:0 2px;border-radius:2px}
body.quiz .cs-card{cursor:pointer}
body.quiz .cs-card .hide1,body.quiz .cs-card .hide2{display:none}
body.quiz .cs-card.s1 .hide1,body.quiz .cs-card.s2 .hide1,body.quiz .cs-card.s2 .hide2{display:block}
body.quiz .cs-card:not(.s2)::after{content:"tap to reveal";display:block;margin-top:8px;font-size:.75rem;color:var(--muted);font-style:italic}
.cs-hidden{display:none!important}
.cs-empty{color:var(--muted);margin-top:24px}
.tag{display:inline-block;margin-left:4px;padding:0 7px;border-radius:999px;font-size:.7rem;font-weight:600;white-space:nowrap;vertical-align:1px}
.tag.adv{background:var(--q-accent-soft,var(--accent-soft));color:var(--q-accent-ink,var(--accent))}
.tag.extra{border:1px solid var(--border);color:var(--muted)}
</style>"""

SCRIPT = """<script>
(function(){
  var body=document.body,hint=document.getElementById("cs-hint");
  document.querySelectorAll(".cs-mode button").forEach(function(b){
    b.addEventListener("click",function(){
      document.querySelectorAll(".cs-mode button").forEach(function(x){x.setAttribute("aria-pressed",String(x===b));});
      body.classList.toggle("quiz",b.dataset.m==="quiz");
      document.querySelectorAll(".cs-card").forEach(function(c){c.classList.remove("s1","s2");});
      hint.textContent=b.dataset.m==="quiz"?"%s":"%s";
    });
  });
  document.addEventListener("click",function(e){
    var c=e.target.closest&&e.target.closest(".cs-card");
    if(!c||!body.classList.contains("quiz"))return;
    if(c.classList.contains("s1"))c.classList.replace("s1","s2");else if(!c.classList.contains("s2"))c.classList.add("s1");
  });
  var q=document.getElementById("cs-q");
  q.addEventListener("input",function(){
    var words=q.value.toLowerCase().split(/\\s+/).filter(Boolean),shown=0;
    document.querySelectorAll(".cs-card").forEach(function(c){
      var t=c.textContent.toLowerCase(),ok=words.every(function(w){return t.indexOf(w)>-1;});
      c.classList.toggle("cs-hidden",!ok);if(ok)shown++;
    });
    document.querySelectorAll(".cs-sec").forEach(function(s){
      var cards=s.querySelectorAll(".cs-card"),any=!words.length||s.textContent.toLowerCase().indexOf(words[0])>-1;
      if(cards.length&&words.length)any=Array.prototype.some.call(cards,function(c){return !c.classList.contains("cs-hidden");});
      s.classList.toggle("cs-hidden",words.length>0&&!any);
    });
  });
})();
</script>""" % (TEST_HINT, LOOK_HINT)


def inline(md: str) -> str:
    """Render the note's inline markdown (bold, italic, highlights, wikilinks, <br>) to HTML."""
    text = html.escape(md.strip(), quote=False).replace("&lt;br&gt;", "<br>")
    text = re.sub(r"\[\[([^\]|]+)\\?\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"!\[\[[^\]]*\]\]", "", text)
    text = re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)
    text = re.sub(r"\(advanced:\s*([^()]+)\)", r'<span class="tag adv">later: \1</span>', text)
    text = re.sub(r"\(extra:\s*([^()]+)\)", r'<span class="tag extra">extra</span>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    return text


def bullets(lines: list[str]) -> str:
    """Render markdown bullets, nested by two-space indent, as nested lists."""
    out, depth = [], -1
    for line in lines:
        m = re.match(r"^(\s*)[-*] (.*)$", line)
        if not m:
            if out and line.strip():
                out[-1] = out[-1][:-5] + " " + inline(line) + "</li>"
            continue
        d = len(m.group(1).replace("\t", "  ")) // 2
        while depth < d:
            out.append("<ul>")
            depth += 1
        while depth > d:
            out.append("</ul>")
            depth -= 1
        out.append(f"<li>{inline(m.group(2))}</li>")
    out.extend("</ul>" for _ in range(depth + 1))
    # a nested list belongs inside the item before it
    joined = "".join(out)
    return re.sub(r"</li><ul>(.*?)</ul>", lambda m: "<ul>" + m.group(1) + "</ul></li>", joined)


def split_row(line: str) -> list[str]:
    """Split one markdown table row into cells, keeping escaped pipes inside wikilinks."""
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [c.replace("\\|", "|").strip() for c in cells]


def steps_html(cell: str) -> str:
    """Render a 'Steps' cell: numbered lines become an ordered list, anything else stays prose."""
    parts = [p.strip() for p in cell.split("<br>") if p.strip()]
    if len(parts) > 1 and all(re.match(r"^\d+\.", p) for p in parts):
        return "<ol>" + "".join(f"<li>{inline(re.sub(r'^\d+\.\s*', '', p))}</li>" for p in parts) + "</ol>"
    return f"<p>{inline(cell)}</p>"


def card(head: list[str], row: list[str]) -> str:
    """One manoeuvre as a card: its name and what it looks for always, the middle columns
    (steps, example question) on the first tap in Test mode, the last column on the second."""
    row = row + [""] * (len(head) - len(row))
    name, looks = row[0], row[1] if len(row) > 1 else ""
    middle = "".join(f'<span class="lbl">{inline(h)}</span>{steps_html(c)}' for h, c in zip(head[2:-1], row[2:-1]) if c)
    last = (f'<div class="ans"><span class="lbl">{inline(head[-1])}</span>{inline(row[-1])}</div>'
            if len(head) > 2 and row[-1] else "")
    return (f'<article class="cs-card"><h3>{inline(name)}</h3>'
            + (f'<p class="for">{inline(looks)}</p>' if looks else "")
            + f'<div class="hide1">{middle}</div><div class="hide2">{last}</div></article>')


def read_note(path: Path) -> dict:
    """Parse a clinical skills note into its key, title, framing and numbered sections."""
    text = path.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    key = re.search(r"^cs_key:\s*(\S+)", fm.group(1), re.M).group(1) if fm else None
    body = text[fm.end():] if fm else text
    title_m = re.search(r"Overview chart:\s*<u>(.*?)</u>", body)
    first = body.find("\n## ")
    intro = body[title_m.end() if title_m else 0:first if first > -1 else len(body)]
    sections = []
    for block in re.split(r"\n(?=## )", body[first + 1:] if first > -1 else ""):
        m = re.match(r"## (\d+)\.\s*(.*?)\s*$", block.split("\n", 1)[0])
        if not m:
            continue
        heading = m.group(2)
        where = re.search(r"\(([^()]*)\)\s*$", heading)
        lines = block.split("\n")[1:]
        pre, table, post = [], [], []
        for line in lines:
            if line.lstrip().startswith("|"):
                table.append(line)
            elif table:
                post.append(line)
            else:
                pre.append(line)
        rows = [split_row(r) for r in table if not re.match(r"^\s*\|?\s*:?-{3,}", r)]
        sections.append({"n": m.group(1), "title": heading[:where.start()].strip() if where else heading,
                         "where": where.group(1) if where else "", "pre": pre, "rows": rows, "post": post})
    return {"key": key, "title": re.sub("<[^>]+>", "", title_m.group(1)) if title_m else path.stem,
            "intro": " ".join(l.strip() for l in intro.splitlines() if l.strip()), "sections": sections}


def render(note: dict) -> str:
    """Render one topic page in the portal's structure."""
    sec_slug, _key, name, taught, _page, _what = next(s for s in cs.SKILLS if s[1] == note["key"])
    sec_name = next(s[1] for s in cs.SECTIONS if s[0] == sec_slug)
    when = " &rarr; ".join(cs.COURSES[c] for c in taught)
    parts = []
    for s in note["sections"]:
        pre = [l for l in s["pre"] if l.strip()]
        post = [l for l in s["post"] if l.strip()]
        grid = ""
        if len(s["rows"]) > 1:
            head = s["rows"][0]
            grid = '<div class="cs-grid">' + "".join(card(head, r) for r in s["rows"][1:]) + "</div>"
        parts.append(
            f'<section class="cs-sec" id="s{s["n"]}"><h2><span class="n">{s["n"]}</span> {inline(s["title"])}'
            + (f'<small>{inline(s["where"])}</small>' if s["where"] else "") + "</h2>"
            + (f'<div class="cs-steps">{bullets(pre)}</div>' if pre else "")
            + grid
            + (f'<div class="cs-pearls">{bullets(post)}</div>' if post else "")
            + "</section>")
    return cs.head(f"{name} - Clinical skills").replace("</style>", "</style>\n" + STYLE, 1) + cs.exam_nav(note["key"], base="") + f"""

<header class="q-masthead" id="content" tabindex="-1">
<div>
<p class="eyebrow">Schulich Clinical Skills &middot; {html.escape(sec_name)} &middot; {when}</p>
<h1>{inline(note["title"])}</h1>
<p class="lead">{inline(note["intro"])}</p>
</div>
</header>

<main>
<div class="cs-tools">
<div class="cs-mode" role="group" aria-label="Mode"><button data-m="look" aria-pressed="true">Look</button><button data-m="quiz" aria-pressed="false">Test</button></div>
<input type="search" id="cs-q" placeholder="Find a step or a test" autocomplete="off">
<p class="cs-hint" id="cs-hint">{LOOK_HINT}</p>
</div>
{"".join(parts)}
</main>
{SCRIPT}
""" + cs.FOOT


def main() -> None:
    """Build a page for every clinical skills note in the vault."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    built = set()
    notes = [read_note(p) | {"path": p} for p in sorted(NOTES.glob("Summary Notes - * Clinical Skills.md"))]
    cs.set_pages({n["key"] for n in notes if n["key"]})
    for note in notes:
        path = note["path"]
        if not note["key"] or not any(s[1] == note["key"] for s in cs.SKILLS):
            LOG.warning("skipped %s: no known cs_key", path.name)
            continue
        page = next(s[4] for s in cs.SKILLS if s[1] == note["key"])
        if page and page.startswith("../"):
            LOG.info("skipped %s: it has its own exam page, %s", note["key"], page)
            continue
        (HERE / f"{note['key']}.html").write_text(render(note), encoding="utf-8")
        built.add(note["key"])
        n = sum(max(len(s["rows"]) - 1, 0) for s in note["sections"])
        LOG.info("wrote %s.html: %d sections, %d cards", note["key"], len(note["sections"]), n)
    missing = [s[1] for s in cs.SKILLS if s[1] not in built and not s[4]]
    if missing:
        LOG.info("no note yet: %s", ", ".join(missing))


if __name__ == "__main__":
    main()
