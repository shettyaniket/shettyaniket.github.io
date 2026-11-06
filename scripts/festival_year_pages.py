#!/usr/bin/env python3
"""Builds /muhurtha/festivals/<year>/ pages and <year>.json from the data in the festivals index,
links them from that index and adds them to the sitemap. Safe to run again."""
import datetime, html, json, re

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
    title = f"Hindu Festivals {year}: Calendar and Dates | Muhurtha"
    first = {f["i"]: d for d, f in reversed(rows)}
    named = [(f, first[f["i"]]) for f in data if f["i"] in FEATURED and f["i"] in first]
    named.sort(key=lambda p: p[1])
    def day(d): return datetime.date.fromisoformat(d)
    short = ", ".join(f'{f["n"].split(" · ")[0]} on {day(d).day} {day(d):%B}' for f, d in named if f["i"] in ("holi", "diwali", "dussehra"))
    desc = f"All {len(rows)} Hindu festival, fast and observance dates for {year}, month by month" + (f": {short}." if short else ".")
    h = head.replace("Hindu festival dates | Muhurtha", esc(title))
    h = h.replace("The date of every major Hindu festival, worked out from the Sun and Moon, with the rule behind each one.", esc(desc))
    h = h.replace(f"{BASE}/", url)
    body = [f"<h1>Hindu festivals {year}</h1>",
            f'<p class="updated">{len(rows)} festivals, fasts and observances in {year}, each worked out by Muhurtha from the Moon and the Sun. '
            'Dates are for Mumbai; a festival can fall a day apart elsewhere, because tithis change at different local times.</p>',
            f"<p>Other years: {year_links(year)}</p>"]
    if named:
        body.append(f'<h2>Main festivals in {year}</h2>\n<table class="fdates"><tr><th>Festival</th><th>Date</th></tr>')
        for f, d in named:
            body.append(f'<tr><td><a href="/muhurtha/festivals/{f["i"]}/">{esc(f["n"])}</a></td><td>{day(d):%A}, {day(d).day} {day(d):%B %Y}</td></tr>')
        body.append("</table>")
    body.append(f"<h2>Full {year} calendar</h2>")
    month = None
    for d, f in rows:
        dt = day(d)
        if dt.month != month:
            if month: body.append("</ul>")
            month = dt.month
            body.append(f'<h3 class="fmonth">{dt:%B %Y}</h3>\n<ul class="frows">')
        body.append(f'<li class="frow"><div class="fday"><b>{dt.day}</b><small>{dt:%a}</small></div><div class="fbody">'
                    f'<a href="/muhurtha/festivals/{f["i"]}/">{esc(f["n"])}</a><p>{esc(f["g"])}</p></div>'
                    f'<span class="fkind {f["k"]}">{KIND[f["k"]]}</span></li>')
    body.append("</ul>")
    body.append(f'<p>This calendar as data: <a href="/muhurtha/festivals/{year}.json">{year}.json</a></p>')
    crumbs = [("Home", "https://aniketshetty.com/"), ("Muhurtha", "https://aniketshetty.com/muhurtha/"),
              ("Festivals", f"{BASE}/"), (str(year), url)]
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
          {"@context": "https://schema.org", "@type": "ItemList", "name": f"Hindu festivals {year}", "numberOfItems": len(rows),
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{f['n']}: {d}", "url": f"{BASE}/{f['i']}/"}
                               for i, (d, f) in enumerate(rows)]}]
    for block in ld:
        body.append('<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    import os
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
print({y: len(rows_for(y)) for y in years})
