/* The landing page's search of the whole portal.

   One box over every practice question, lecture note, interactive chart and
   clinical skills card, filtered by source, course and block.
   The index is tools/build_search.py's search.json: a few megabytes, so it is
   fetched the first time someone reaches for the box rather than on every
   visit to the front door. A query means what it means in the notes and the
   bank: every word of two letters or more must appear, in any order.

   A row is [source, course, block, week, family, title, text, target]. */

(function () {
  "use strict";

  var SEARCH_MIN = 2;           // as portal.js: a shorter word is a keystroke, not a term
  var PAGE = 30;                // results drawn at a time
  var SNIP = 90;                // characters either side of the first hit
  var SOURCES = [
    { k: "n", label: "Lecture notes" },
    { k: "q", label: "Practice questions" },
    { k: "c", label: "Interactive charts" },
    { k: "k", label: "Clinical skills" }
  ];
  // when two results match equally well, a note is the better first stop than a question
  var SOURCE_RANK = { n: 0, c: 1, k: 2, q: 3 };

  var root = document.getElementById("hub-search");
  if (!root) return;
  var box = document.getElementById("hs-q");
  var out = document.getElementById("hs-results");
  var count = document.getElementById("hs-count");
  var more = document.getElementById("hs-more");
  var filtersBox = document.getElementById("hs-filters");

  var ROWS = null, HAY = null, META = null, loading = null;
  var COURSE = {}, BLOCK = {};
  var picked = { s: [], c: [], b: [] };
  var hits = [], shown = 0, timer = null;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function esc(t) {
    return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function words() {
    return (box.value || "").toLowerCase().split(/\s+/).filter(function (w) {
      return w.length >= SEARCH_MIN;
    });
  }

  function load() {
    if (loading) return loading;
    count.textContent = "Loading the index…";
    loading = fetch(root.getAttribute("data-index"))
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (d) {
        META = d.meta;
        ROWS = d.rows;
        HAY = ROWS.map(function (r) { return (r[5] + " " + r[6]).toLowerCase(); });
        META.courses.forEach(function (c) {
          COURSE[c.slug] = c;
          c.blocks.forEach(function (b) { BLOCK[c.slug + "/" + b[0]] = b[1]; });
        });
        buildFilters();
        run();
      })
      .catch(function () {
        loading = null;
        count.textContent = "The search index could not be loaded. Check your connection and try again.";
      });
    return loading;
  }

  /* ---------- filters ---------- */

  function chip(group, key, label) {
    var b = el("button", "chip");
    b.type = "button";
    b.dataset.g = group;
    b.dataset.k = key;
    b.setAttribute("aria-pressed", "false");
    b.appendChild(document.createTextNode(label));
    b.appendChild(el("span", "n", ""));
    b.addEventListener("click", function () {
      var list = picked[group], at = list.indexOf(key);
      if (at === -1) list.push(key); else list.splice(at, 1);
      // a block belongs to its course; unpicking the course leaves no block to stand on
      if (group === "c") picked.b = picked.b.filter(function (bk) { return picked.c.indexOf(bk.split("/")[0]) !== -1; });
      run();
    });
    return b;
  }

  function group(key, label) {
    var g = el("div", "hs-group");
    g.dataset.g = key;
    g.appendChild(el("p", "panel-h", label));
    var chips = el("div", "chips");
    g.appendChild(chips);
    filtersBox.appendChild(g);
    return chips;
  }

  function buildFilters() {
    filtersBox.innerHTML = "";
    var s = group("s", "Source");
    SOURCES.forEach(function (x) { s.appendChild(chip("s", x.k, x.label)); });
    var c = group("c", "Course");
    META.courses.forEach(function (x) { c.appendChild(chip("c", x.slug, x.short)); });
    var b = group("b", "Block");
    META.courses.forEach(function (x) {
      x.blocks.forEach(function (bl) {
        var ch = chip("b", x.slug + "/" + bl[0], bl[1]);
        ch.dataset.course = x.slug;
        b.appendChild(ch);
      });
    });
    var reset = el("button", "hs-reset", "Clear filters");
    reset.type = "button";
    reset.addEventListener("click", function () {
      picked = { s: [], c: [], b: [] };
      run();
    });
    filtersBox.appendChild(reset);
  }

  function keyOf(g, r) {
    if (g === "s") return r[0];
    if (g === "c") return r[1];
    return r[1] + "/" + r[2];
  }

  // a row passes every group but the one named (so that group's chips can count what picking them adds)
  function passes(r, except) {
    for (var g in picked) {
      if (g === except || !picked[g].length) continue;
      if (picked[g].indexOf(keyOf(g, r)) === -1) return false;
    }
    return true;
  }

  function paintFilters(matched) {
    var tally = { s: {}, c: {}, b: {} };
    matched.forEach(function (i) {
      var r = ROWS[i];
      for (var g in tally) {
        if (!passes(r, g)) continue;
        var k = keyOf(g, r);
        tally[g][k] = (tally[g][k] || 0) + 1;
      }
    });
    [].forEach.call(filtersBox.querySelectorAll(".chip"), function (b) {
      var g = b.dataset.g, k = b.dataset.k, on = picked[g].indexOf(k) !== -1, n = tally[g][k] || 0;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.querySelector(".n").textContent = n;
      b.disabled = !on && n === 0;
      // a block chip shows only under a picked course, or under every course once a search has narrowed it
      if (g === "b") b.hidden = !on && (picked.c.length ? picked.c.indexOf(b.dataset.course) === -1 : n === 0);
    });
    var bg = filtersBox.querySelector('[data-g="b"]');
    if (bg) bg.hidden = !bg.querySelector(".chip:not([hidden])");
    var any = picked.s.length + picked.c.length + picked.b.length;
    filtersBox.querySelector(".hs-reset").hidden = !any;
  }

  /* ---------- results ---------- */

  /* A word in a note's or chart's title is a strong hit. Not in a
     question's: its title is the lecture it was filed under, so a search
     for the lecture's subject would otherwise float every question in it
     above the note that teaches it. */
  function score(i, ws) {
    if (ROWS[i][0] === "q") return 0;
    var title = ROWS[i][5].toLowerCase(), s = 0;
    ws.forEach(function (w) { if (title.indexOf(w) !== -1) s += 3; });
    return s;
  }

  function run() {
    if (!ROWS) return;
    var ws = words();
    if (!ws.length) {
      hits = [];
      out.innerHTML = "";
      more.hidden = true;
      count.textContent = "Type a word or two: a drug, a sign, a disease, a lecture.";
      paintFilters([]);
      filtersBox.hidden = true;
      return;
    }
    filtersBox.hidden = false;
    var matched = [];
    for (var i = 0; i < HAY.length; i++) {
      var hay = HAY[i], ok = true;
      for (var j = 0; j < ws.length; j++) { if (hay.indexOf(ws[j]) === -1) { ok = false; break; } }
      if (ok) matched.push(i);
    }
    paintFilters(matched);
    hits = matched.filter(function (i) { return passes(ROWS[i], null); });
    var sc = {};
    hits.forEach(function (i) { sc[i] = score(i, ws); });
    hits.sort(function (a, b) {
      return (sc[b] - sc[a]) || (SOURCE_RANK[ROWS[a][0]] - SOURCE_RANK[ROWS[b][0]]) || (a - b);
    });
    out.innerHTML = "";
    shown = 0;
    count.textContent = hits.length
      ? hits.length.toLocaleString() + (hits.length === 1 ? " result" : " results")
      : "Nothing matches. Try fewer words, or clear a filter.";
    draw();
  }

  function draw() {
    var ws = words(), frag = document.createDocumentFragment();
    hits.slice(shown, shown + PAGE).forEach(function (i) { frag.appendChild(result(ROWS[i], ws)); });
    shown = Math.min(hits.length, shown + PAGE);
    out.appendChild(frag);
    more.hidden = shown >= hits.length;
    more.textContent = "Show " + Math.min(PAGE, hits.length - shown) + " more";
  }

  function href(r) {
    if (r[0] === "q") return r[1] + "/qbank.html#block=" + r[2] + "&q=" + encodeURIComponent(r[7]);
    // the words ride along so the note opens on the first place they appear, highlighted
    if (r[0] === "n") return r[1] + "/" + r[2] + ".html#n-" + encodeURIComponent(r[7]) +
      "&q=" + encodeURIComponent(words().join(" "));
    return r[7];
  }

  function where(r) {
    var parts = [];
    var c = COURSE[r[1]];
    if (c && r[1] !== "cs") parts.push(c.short);
    var b = BLOCK[r[1] + "/" + r[2]];
    if (b) parts.push(b);
    if (r[3]) parts.push("Week " + r[3]);
    if (r[0] === "q" && META.families[r[4]]) parts.push(META.families[r[4]]);
    return parts.join(" · ");
  }

  function marked(text, ws) {
    /* one pass over the plain text, longest word first, so a mark is never
       painted inside another mark's tag and "thyroid" never nests in "thyroiditis" */
    var paint = ws.filter(function (w) { return w.length >= 3; })
      .sort(function (a, b) { return b.length - a.length; })
      .map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); });
    if (!paint.length) return esc(text);
    var re = new RegExp(paint.join("|"), "gi"), html = "", last = 0, m;
    while ((m = re.exec(text))) {
      html += esc(text.slice(last, m.index)) + "<mark>" + esc(m[0]) + "</mark>";
      last = m.index + m[0].length;
    }
    return html + esc(text.slice(last));
  }

  function snippet(text, ws) {
    var low = text.toLowerCase(), at = -1;
    ws.forEach(function (w) {
      var k = low.indexOf(w);
      if (k !== -1 && (at === -1 || k < at)) at = k;
    });
    if (at === -1) at = 0;
    var from = Math.max(0, at - SNIP), to = Math.min(text.length, at + SNIP * 2);
    return (from ? "…" : "") + text.slice(from, to) + (to < text.length ? "…" : "");
  }

  function result(r, ws) {
    var li = el("li", "hs-hit");
    var a = el("a");
    a.href = href(r);
    var top = el("span", "hs-meta");
    top.appendChild(el("span", "hs-src hs-src-" + r[0],
      SOURCES.filter(function (s) { return s.k === r[0]; })[0].label.replace(/s$/, "")));
    top.appendChild(document.createTextNode(" " + where(r)));
    a.appendChild(top);
    var t = el("span", "hs-title");
    t.innerHTML = marked(r[5], ws);
    a.appendChild(t);
    var s = el("span", "hs-snip");
    s.innerHTML = marked(snippet(r[6], ws), ws);
    a.appendChild(s);
    li.appendChild(a);
    return li;
  }

  /* ---------- wiring ---------- */

  box.addEventListener("focus", load);
  box.addEventListener("input", function () {
    load();
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(run, 150);
  });
  box.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { box.value = ""; run(); }
    if (e.key === "Enter") { e.preventDefault(); if (timer) window.clearTimeout(timer); run(); }
  });
  more.addEventListener("click", draw);
  document.addEventListener("keydown", function (e) {
    // "/" jumps to the box, as it does in the notes and the bank
    var t = e.target, tag = t && t.tagName;
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return;
    e.preventDefault();
    box.focus();
  });
})();
