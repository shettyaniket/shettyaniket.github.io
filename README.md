# aniketshetty.com

A single static site for all my iOS apps — home page, per-app landing pages, support,
terms, and per-app privacy policies. Plain HTML/CSS, no build step. Free to host.

Live domain: **https://aniketshetty.com** · GitHub repo: **shettyaniket**

## Structure

```
/                       Home — about me, values, story, app gallery
/forehead-flip/         App landing page
/forehead-flip/privacy/ Privacy policy   ← Privacy URL for App Store Connect
/ozora/                 App landing page
/ozora/privacy/         Privacy policy   ← Privacy URL for App Store Connect
/support/               Shared support    ← Support URL (works for every app)
/terms/                 Shared terms / Apple EULA
apps.json               ⭐ edit this to add apps to the home gallery
assets/                 style.css, app.js, family.jpg, icons/
CNAME                   aniketshetty.com  (for GitHub/Cloudflare Pages custom domain)
```

## Adding a new app

1. Add an entry to `apps.json` (the home gallery renders from it automatically):
   ```json
   { "slug": "newapp", "name": "New App", "tagline": "…",
     "platform": "iOS", "appStoreId": "1234567890",
     "icon": "/assets/icons/newapp.png", "accent": "#6366f1", "collectsData": false }
   ```
2. Add an icon at `assets/icons/newapp.png` (optional; falls back to a letter tile).
3. Create `newapp/index.html` (copy an existing app folder) and `newapp/privacy/index.html`.

## Before launch — fill in the TODOs

- **App Store IDs:** Forehead Flip is live — https://apps.apple.com/in/app/forehead-flip/id6777682330 .
  Ozora still shows a "Coming to the App Store" button; once live, put its id in `apps.json` and
  change the button in `ozora/index.html` from `class="btn soon"` to `class="btn"` with the real
  App Store `href`.
- **Ozora copy:** `ozora/index.html` has `<!-- TODO -->` markers — replace with the real pitch/features.
- **App icons:** drop `forehead-flip.png` and `ozora.png` into `assets/icons/`.

## App Store Connect URLs

| Field                  | Forehead Flip                                 | Ozora                              |
|------------------------|-----------------------------------------------|------------------------------------|
| Marketing URL          | `https://aniketshetty.com/forehead-flip/`     | `https://aniketshetty.com/ozora/`  |
| Support URL (required) | `https://aniketshetty.com/support/`           | `https://aniketshetty.com/support/`|
| Privacy URL (required) | `https://aniketshetty.com/forehead-flip/privacy/` | `https://aniketshetty.com/ozora/privacy/` |

## Deploy — GitHub Pages (repo must be public)

```bash
cd /Users/aniketshetty/git/dev-site
git init && git add . && git commit -m "Launch aniketshetty.com"
git branch -M main
git remote add origin git@github.com:shettyaniket/shettyaniket.git
git push -u origin main
```

Then on GitHub:
1. **Settings → Pages → Source:** Deploy from a branch → `main` / root.
2. **Settings → Pages → Custom domain:** enter `aniketshetty.com` (the `CNAME` file already sets this).
3. At your domain registrar, point DNS at GitHub Pages:
   - Four `A` records for the apex `aniketshetty.com` → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
   - One `CNAME` for `www` → `shettyaniket.github.io`
4. Back in Pages, tick **Enforce HTTPS** once the certificate is issued.

## Deploy — Cloudflare Pages (keeps the repo private, free)

1. Push to the `shettyaniket` repo (can stay **private**).
2. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick the repo.
3. Build command: *none* · Output directory: `/` (root).
4. **Custom domains → Set up a domain** → `aniketshetty.com` (Cloudflare wires DNS automatically
   if the domain is on your Cloudflare account).

## Local preview

```bash
python3 -m http.server 4600 --directory /Users/aniketshetty/git/dev-site
# open http://localhost:4600
```
