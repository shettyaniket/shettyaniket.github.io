// Renders the app gallery from /apps.json — add an app there, no HTML edits needed.
async function loadApps() {
  const grid = document.getElementById("app-grid");
  if (!grid) return;
  try {
    const res = await fetch("/apps.json", { cache: "no-cache" });
    const apps = await res.json();
    grid.innerHTML = apps.map(cardHTML).join("");
  } catch (e) {
    grid.innerHTML = '<p class="muted">Could not load apps.</p>';
  }
}

function cardHTML(app) {
  const accent = app.accent || "var(--accent)";
  const icon = app.icon
    ? `<img class="app-icon" src="${app.icon}" alt="${app.name} icon" style="background:${accent}" onerror="this.replaceWith(letterTile('${app.name}','${accent}'))">`
    : `<div class="app-icon" style="background:${accent}">${(app.name || "?")[0]}</div>`;
  return `
    <a class="app-card" href="/${app.slug}/">
      ${icon}
      <div class="app-meta">
        <h3>${app.name} <span class="pill-os">${app.platform || "iOS"}</span></h3>
        <p>${app.tagline || ""}</p>
      </div>
    </a>`;
}

// Fallback letter tile if an icon image is missing.
function letterTile(name, accent) {
  const d = document.createElement("div");
  d.className = "app-icon";
  d.style.background = accent;
  d.textContent = (name || "?")[0];
  return d;
}

loadApps();
