#!/usr/bin/env python3
"""Makes /for/<name>/index.html from scripts/for_template.html.

    python3 scripts/for_page.py "Priya" --from "Rahul"

The page is unlisted: noindex, and not in the sitemap. The name is only in the address and the greeting."""
import argparse, html, json, os, re, subprocess, shutil, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("name", nargs="?", default="")
ap.add_argument("--generic", action="store_true", help="one page at /for/ that takes ?name= and ?from= from the address")
ap.add_argument("--from", dest="sender", default="")
a = ap.parse_args()
slug = "" if a.generic else re.sub(r"[^a-z0-9]+", "-", a.name.lower()).strip("-")
assert a.generic or slug, "the name needs letters or digits, or use --generic"
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "for", slug) if slug else os.path.join(root, "for")
os.makedirs(out, exist_ok=True)

# a preview picture for WhatsApp and Messages: pastel card, the name, and a heart
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#ffd9e8"/><rect x="600" width="600" height="630" fill="#f0dcff"/>
<g font-size="64" opacity=".55"><text x="80" y="120">&#x1F495;</text><text x="1040" y="200">&#x1F497;</text><text x="140" y="560">&#x1F496;</text><text x="980" y="560">&#x1F495;</text></g>
<circle cx="600" cy="250" r="150" fill="#fff" opacity=".85"/>
<text x="600" y="305" font-size="170" text-anchor="middle">&#x1F43B;</text>
<text x="600" y="470" font-size="68" font-weight="700" text-anchor="middle" fill="#5a2342" font-family="Helvetica Neue, Arial">A few questions for {html.escape(a.name or "you")}</text>
<text x="600" y="540" font-size="40" text-anchor="middle" fill="#b14b7c" font-family="Helvetica Neue, Arial">Answer honestly &#x1F495;</text></svg>'''
og = ""
tmp = tempfile.mkdtemp()
try:
    p = os.path.join(tmp, "preview.svg"); open(p, "w", encoding="utf-8").write(svg)
    subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", tmp, p], capture_output=True, timeout=60)
    png = p + ".png"
    if os.path.exists(png):
        shutil.copy(png, os.path.join(out, "preview.png"))
        og = (f'<meta property="og:image" content="https://aniketshetty.com/for/{slug + "/" if slug else ""}preview.png">\n'
              '<meta name="twitter:card" content="summary_large_image">')
finally:
    shutil.rmtree(tmp, ignore_errors=True)

t = open(os.path.join(root, "scripts", "for_template.html"), encoding="utf-8").read()
q = lambda k, d: '(new URLSearchParams(location.search).get("%s") || %s).trim().slice(0, 40)' % (k, json.dumps(d))
if a.generic:
    t = (t.replace("A few questions for {{NAME_HTML}} 💕", "A few questions for you 💕").replace("{{NAME_HTML}}", '<span class="nm">gorgeous</span>')
           .replace("{{NAME_JS}}", q("name", "")).replace("{{FROM_JS}}", q("from", a.sender or "Aniket")).replace("{{OG_IMAGE}}", og))
else:
    t = (t.replace("{{NAME_HTML}}", '<span class="nm">%s</span>' % html.escape(a.name)).replace("{{NAME_JS}}", json.dumps(a.name).replace("</", "<\\/"))
           .replace("{{FROM_JS}}", json.dumps(a.sender).replace("</", "<\\/")).replace("{{OG_IMAGE}}", og))
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(t)
print(f"https://aniketshetty.com/for/{slug}/", "(preview picture)" if og else "(no preview picture)")
