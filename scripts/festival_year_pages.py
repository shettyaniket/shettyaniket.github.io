#!/usr/bin/env python3
"""Builds /muhurtha/festivals/<year>/ pages and <year>.json from the data in the festivals index,
links them from that index and adds them to the sitemap. Safe to run again."""
import datetime, glob, html, json, os, re

BASE = "https://aniketshetty.com/muhurtha/festivals"
INDEX = "muhurtha/festivals/index.html"
KIND = {"major": "Major", "regional": "Regional", "observance": "Observance"}
FEATURED = ["makar-sankranti", "maha-shivaratri", "holi", "ugadi", "ram-navami", "raksha-bandhan",
            "janmashtami", "ganesh-chaturthi", "dussehra", "diwali"]
esc = html.escape

page = open(INDEX, encoding="utf-8").read()
page = re.sub(r'\n *<!-- year-links -->.*?<!-- /year-links -->', "", page, flags=re.S)
data = json.loads(re.search(r'id="fdata">(.*?)</script>', page, re.S).group(1))
years = sorted({int(d[:4]) for f in data for d in f["d"]})

head = page[:page.index("<h1>")]
# The list's own styles sit after the index's heading.
list_css = next(m for m in re.findall(r"<style>.*?</style>", page[page.index("<h1>"):], re.S) if ".frow" in m)
YEAR_CSS = "<style>#yq{display:block;width:100%;box-sizing:border-box;margin-top:14px;font:inherit;font-size:16px;color:var(--text);background:var(--surface-2);border:1px solid var(--border);border-radius:10px;padding:10px 12px}#yq[hidden],#yempty[hidden]{display:none}#yk:not([hidden]){display:flex;flex-wrap:wrap;justify-content:flex-start;gap:6px;margin:14px 0}.ymonth[hidden],.frow[hidden]{display:none}</style>"
tail = page[page.index('<p><a class="cta" href="https://apps.apple.com'):]
tail = tail.replace('href="/muhurtha/festival-rules/">How every festival is dated</a>',
                    'href="/muhurtha/festival-rules/">How every festival is dated</a> '
                    '<a class="cta secondary" href="/muhurtha/festivals/">All festivals</a>', 1)

def rows_for(year):
    rows = [(d, f) for f in data for d in f["d"] if d.startswith(f"{year}-")]
    return sorted(rows, key=lambda r: (r[0], r[1]["n"]))

def year_links(current=None):
    return " · ".join(str(y) if y == current else f'<a href="/muhurtha/festivals/{y}/">{y}</a>' for y in years)

def build(year):
    rows = rows_for(year)
    url = f"{BASE}/{year}/"
    def day(d): return datetime.date.fromisoformat(d)
    def nice(d): return f"{day(d):%A}, {day(d).day} {day(d):%B %Y}"
    first = {f["i"]: d for d, f in reversed(rows)}
    named = sorted(((f, first[f["i"]]) for f in data if f["i"] in FEATURED and f["i"] in first), key=lambda p: p[1])
    short_name = lambda f: f["n"].split(" · ")[0]
    lead = [(f, d) for f, d in named if f["i"] in ("holi", "dussehra", "diwali")]
    title = f"Hindu Festivals {year}: Full Calendar with Dates | Muhurtha"
    desc = (f"Hindu festivals {year} by month: " + ", ".join(f"{short_name(f)} {day(d).day} {day(d):%B}" for f, d in lead)
            + f" and all {len(rows)} festivals, fasts and observances, with what each one means.")
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head, flags=re.S)
    h = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m[1] + esc(desc) + m[2], h)
    h = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m[1] + esc(title) + m[2], h)
    h = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m[1] + esc(desc) + m[2], h)
    h = h.replace(f"{BASE}/\"", url + "\"")
    h = h.replace("</head>", '  <meta name="twitter:card" content="summary_large_image">\n</head>', 1)
    counts = {k: sum(f["k"] == k for _, f in rows) for k in KIND}
    parts = [f"{short_name(f)} on {day(d).day} {day(d):%B}" for f, d in lead]
    sentence = ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else "".join(parts)
    body = [list_css, YEAR_CSS, f"<h1>Hindu festivals {year}</h1>",
            f'<p class="updated">In {year}, the big days are {esc(sentence)}. All {len(rows)} festivals, fasts and observances are below, worked out from the Moon and the Sun. '
            'Dates are for Mumbai; a festival can fall a day apart elsewhere, because tithis change at different local times.</p>',
            f"<p>Other years: {year_links(year)}</p>"]
    chips = [("", f"All ({len(rows)})"), ("major", f"Major ({counts['major']})"), ("regional", f"Regional ({counts['regional']})"), ("observance", f"Observance ({counts['observance']})")]
    body.append(f'<input type="search" id="yq" hidden placeholder="Search festivals in {year}" aria-label="Search festivals in {year}" autocomplete="off">')
    body.append('<div class="ff-row chips" id="yk" role="group" aria-label="Show" hidden>'
                + "".join(f'<button class="chip" data-k="{k}" aria-pressed="false">{esc(t)}</button>' for k, t in chips) + "</div>")
    month = None
    for d, f in rows:
        dt = day(d)
        if dt.month != month:
            if month: body.append("</ul></section>")
            month = dt.month
            body.append(f'<section class="ymonth" id="{dt:%B}".lower()><h2 class="fmonth">{dt:%B %Y}</h2>\n<ul class="frows">'.replace(f'"{dt:%B}".lower()', f'"{dt:%B}"'.lower()))
        body.append(f'<li class="frow" data-k="{f["k"]}"><div class="fday"><b>{dt.day}</b><small>{dt:%a}</small></div><div class="fbody">'
                    f'<a href="/muhurtha/festivals/{f["i"]}/">{esc(f["n"])}</a><p>{esc(f["g"])}</p></div>'
                    f'<span class="fkind {f["k"]}">{KIND[f["k"]]}</span></li>')
    body.append("</ul></section>")
    body.append('<p class="fempty" id="yempty" hidden>No festivals match. Try another spelling, or choose All.</p>')
    faq = [(f"When is {short_name(f)} in {year}?", f"{short_name(f)} falls on {nice(d)}, for Mumbai. {f['g']}", f["i"]) for f, d in named]
    body.append(f"<h2>Common questions about {year}</h2>")
    for q, a, i in faq:
        body.append(f'<h3>{esc(q)}</h3>\n<p>{esc(a)} <a href="/muhurtha/festivals/{i}/">More about it</a></p>')
    body.append(f'<p>This calendar as data: <a href="/muhurtha/festivals/{year}.json">{year}.json</a></p>')
    body.append("""<script>
(function () {
  var bar = document.getElementById("yk"), chips = [].slice.call(bar.querySelectorAll(".chip"));
  var box = document.getElementById("yq"), empty = document.getElementById("yempty");
  var rows = [].slice.call(document.querySelectorAll(".ymonth .frow")), months = [].slice.call(document.querySelectorAll(".ymonth"));
  var kind = "";
  rows.forEach(function (r) { r.dataset.s = r.querySelector(".fbody").textContent.toLowerCase(); });
  function show(remember) {
    var needle = box.value.trim().toLowerCase();
    chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.k === kind)); });
    rows.forEach(function (r) { r.hidden = (!!kind && r.dataset.k !== kind) || (!!needle && r.dataset.s.indexOf(needle) < 0); });
    months.forEach(function (m) { m.hidden = !m.querySelector(".frow:not([hidden])"); });
    empty.hidden = months.some(function (m) { return !m.hidden; });
    if (remember) {
      var p = new URLSearchParams();
      if (kind) p.set("k", kind);
      if (needle) p.set("q", box.value.trim());
      var q = p.toString();
      history.replaceState(null, "", location.pathname + (q ? "?" + q : ""));
    }
  }
  chips.forEach(function (c) { c.addEventListener("click", function () { kind = c.dataset.k; show(true); }); });
  box.addEventListener("input", function () { show(true); });
  var asked = new URLSearchParams(location.search);
  kind = ["major", "regional", "observance"].indexOf(asked.get("k")) >= 0 ? asked.get("k") : "";
  box.value = asked.get("q") || "";
  bar.hidden = false; box.hidden = false;
  show(false);
})();
</script>""")
    crumbs = [("Home", "https://aniketshetty.com/"), ("Muhurtha", "https://aniketshetty.com/muhurtha/"),
              ("Festivals", f"{BASE}/"), (str(year), url)]
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
          {"@context": "https://schema.org", "@type": "ItemList", "name": f"Hindu festivals {year}", "numberOfItems": len(rows),
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{f['n']}: {d}", "url": f"{BASE}/{f['i']}/"}
                               for i, (d, f) in enumerate(rows)]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, _ in faq]}]
    for block in ld:
        body.append('<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    os.makedirs(f"muhurtha/festivals/{year}", exist_ok=True)
    open(f"muhurtha/festivals/{year}/index.html", "w", encoding="utf-8").write(h + "\n      ".join(body) + "\n      " + tail)
    out = [{"date": d, "id": f["i"], "name": f["n"], "kind": f["k"], "basis": f.get("b"), "traditions": f["t"], "about": f["g"], "url": f"{BASE}/{f['i']}/"} for d, f in rows]
    json.dump({"year": year, "location": "Mumbai", "source": url, "festivals": out}, open(f"muhurtha/festivals/{year}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

for y in years: build(y)

links = f'\n      <!-- year-links --><p>Calendar by year: {year_links()}</p><!-- /year-links -->'
marker = "Dates are for Mumbai.</p>"
assert marker in page
page = page.replace(marker, marker + links, 1)
open(INDEX, "w", encoding="utf-8").write(page)

sm = open("sitemap.xml", encoding="utf-8").read()
for y in years:
    loc = f"  <url><loc>{BASE}/{y}/</loc></url>\n"
    if loc not in sm: sm = sm.replace("</urlset>", loc + "</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write(sm)

# Each festival's date table links to its year's calendar.
linked = 0
for path in glob.glob("muhurtha/festivals/*/index.html"):
    text = open(path, encoding="utf-8").read()
    if '<table class="fdates">' not in text: continue
    new = re.sub(r"<td>(20\d\d)</td>", lambda m: f'<td><a href="/muhurtha/festivals/{m[1]}/">{m[1]}</a></td>' if int(m[1]) in years else m[0], text)
    if new != text:
        open(path, "w", encoding="utf-8").write(new); linked += 1

# The Muhurtha landing page links to the calendars.
landing = open("muhurtha/index.html", encoding="utf-8").read()
landing = re.sub(r"\n *<!-- year-links -->.*?<!-- /year-links -->", "", landing, flags=re.S)
landing = landing.replace("</main>", f'  <!-- year-links --><div class="wrap"><h2>Hindu festival calendar</h2><p><a href="/muhurtha/festivals/">All festival dates</a> · By year: {year_links()}</p></div><!-- /year-links -->\n  </main>', 1)
open("muhurtha/index.html", "w", encoding="utf-8").write(landing)

print({y: len(rows_for(y)) for y in years}, "festival pages linked:", linked)
