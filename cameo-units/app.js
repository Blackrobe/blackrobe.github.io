"use strict";

const QUEUE_ORDER = ["Building", "Defense", "Infantry", "Vehicle", "Aircraft", "Ship", "Upgrade", "Promotions", ""];
const QUEUE_COLORS = {
  Building: "#4a90d9", Defense: "#7a5cc4", Infantry: "#3fa34d", Vehicle: "#d98a3f",
  Aircraft: "#46b3b3", Ship: "#3f6fd9", Upgrade: "#b3457a", Promotions: "#8a6dd1", "": "#6b7280",
};
const qc = (q) => QUEUE_COLORS[q] ?? "#6b7280";

const $ = (id) => document.getElementById(id);
let DATA = null;
let FACNAMES = {}; // token -> display name, for the currently selected faction
let CUR_NODES = []; // nodes of the currently selected faction, for "unlocks" lookups
let TOKEN_NODES = {}; // token -> providing node, for the requires-groups + hover-link feature
const LS_THEME = "cameo-units:theme";
const LS_FACTION = "cameo-units:faction";

async function boot() {
  try {
    DATA = await (await fetch("data/units.json", { cache: "no-cache" })).json();
  } catch (e) {
    $("grid").innerHTML = '<p>Could not load data/units.json — run update.cmd first.</p>';
    return;
  }
  if (DATA.generated) $("gen").textContent = "· data: " + DATA.generated;
  DATA.themes.forEach((t, i) => {
    const o = document.createElement("option");
    o.value = i; o.textContent = `${t.name} (${t.factions.length})`;
    o.dataset.name = t.name;
    $("theme").appendChild(o);
  });
  const savedTheme = localStorage.getItem(LS_THEME);
  if (savedTheme) {
    const opt = [...$("theme").options].find((o) => o.dataset.name === savedTheme);
    if (opt) $("theme").value = opt.value;
  }
  $("theme").addEventListener("change", () => onTheme(false));
  $("faction").addEventListener("change", () => { saveSelection(); render(); });
  $("search").addEventListener("input", () => { toggleSearchClear(); render(); });
  $("searchClear").addEventListener("click", () => {
    $("search").value = "";
    toggleSearchClear();
    render();
    $("search").focus();
  });
  $("showUpg").addEventListener("change", render);
  $("showLinks").addEventListener("change", clearLinks);
  $("offTop").addEventListener("click", scrollToChip);
  $("offBottom").addEventListener("click", scrollToChip);
  $("detailClose").addEventListener("click", closeDetail);
  $("overlay").addEventListener("click", (e) => { if (e.target === $("overlay")) closeDetail(); });
  $("detailBody").addEventListener("click", (e) => {
    const el = e.target.closest(".unlock");
    if (!el) return;
    const target = CUR_NODES.find((n) => n.id === el.dataset.id);
    if (target) openDetail(target);
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDetail(); });
  toggleSearchClear();
  onTheme(true);
}

function toggleSearchClear() {
  $("searchClear").classList.toggle("hidden", !$("search").value);
}

function saveSelection() {
  const t = DATA.themes[+$("theme").value];
  const fac = t && t.factions[+$("faction").value];
  if (t) localStorage.setItem(LS_THEME, t.name);
  if (fac) localStorage.setItem(LS_FACTION, fac.name);
}

function onTheme(restoring) {
  const t = DATA.themes[+$("theme").value];
  const fs = $("faction");
  fs.innerHTML = "";
  t.factions.forEach((f, i) => {
    const o = document.createElement("option");
    o.value = i; o.textContent = `${f.name} (${f.nodes.filter(n => !n.hidden).length})`;
    o.dataset.name = f.name;
    fs.appendChild(o);
  });
  if (restoring) {
    const savedFaction = localStorage.getItem(LS_FACTION);
    if (savedFaction) {
      const opt = [...fs.options].find((o) => o.dataset.name === savedFaction);
      if (opt) fs.value = opt.value;
    }
  }
  $("approx").classList.toggle("hidden", !!t.accurate);
  saveSelection();
  render();
}

function render() {
  const t = DATA.themes[+$("theme").value];
  const fac = t.factions[+$("faction").value];
  if (!fac) return;
  CUR_NODES = fac.nodes;
  const showUpg = $("showUpg").checked;
  const q = $("search").value.trim().toLowerCase();

  // token -> name for this faction (faction-accurate), falls back to global map.
  FACNAMES = {};
  // token -> providing node - used by the Upgrade requires-groups and hover-link highlight.
  TOKEN_NODES = {};
  for (const n of fac.nodes) {
    for (const p of n.provides || []) {
      const k = p.toLowerCase();
      if (!(k in FACNAMES)) FACNAMES[k] = n.name;
      if (!(k in TOKEN_NODES)) TOKEN_NODES[k] = n;
    }
  }

  const groups = {};
  let shown = 0;
  for (const n of fac.nodes) {
    if (n.hidden && !showUpg) continue;
    (groups[n.queue || ""] ||= []).push(n);
    shown++;
  }
  $("meta").textContent = `${shown} units`;

  const grid = $("grid");
  grid.innerHTML = "";
  for (const queue of QUEUE_ORDER) {
    const list = groups[queue];
    if (!list || !list.length) continue;
    list.sort((a, b) => (a.cost ?? 1e9) - (b.cost ?? 1e9) || a.name.localeCompare(b.name));
    const sec = document.createElement("section");
    sec.className = "queue-section";
    sec.style.setProperty("--qc", qc(queue));
    sec.innerHTML = `<h2>${queue || "Other"} · ${list.length}</h2>`;
    if (queue === "Upgrade") {
      sec.appendChild(renderRequiresGroups(list, q, TOKEN_NODES));
    } else {
      const tiles = document.createElement("div");
      tiles.className = "tiles";
      for (const n of list) tiles.appendChild(makeTile(n, q));
      sec.appendChild(tiles);
    }
    grid.appendChild(sec);
  }
  if (!grid.children.length) grid.innerHTML = '<p style="color:var(--muted)">No units match.</p>';
}

// Upgrades grouped by their (translated) prerequisite set, each group headed
// by "Requires:" + the icon(s) of whatever provides that requirement.
function renderRequiresGroups(list, q, tokenNodes) {
  const wrap = document.createElement("div");
  wrap.className = "req-groups";

  const groups = new Map(); // sorted-token-key -> { tokens, nodes }
  for (const n of list) {
    const toks = [...new Set((n.prereqs || []).map((p) => p.toLowerCase()))];
    const key = toks.slice().sort().join("|");
    if (!groups.has(key)) groups.set(key, { tokens: toks, nodes: [] });
    groups.get(key).nodes.push(n);
  }

  const entries = [...groups.entries()].sort((a, b) => {
    if (!a[0] !== !b[0]) return a[0] ? 1 : -1; // no-requirement group first
    return a[0].localeCompare(b[0]);
  });

  for (const [, group] of entries) {
    const box = document.createElement("div");
    box.className = "req-group";
    if (group.tokens.length) {
      const head = document.createElement("div");
      head.className = "req-head";
      head.textContent = "Requires:";
      const icons = document.createElement("div");
      icons.className = "req-icons";
      for (const tok of group.tokens) {
        const rn = tokenNodes[tok];
        // Reuse the exact same tile (hover tip, click-to-detail, hover-link
        // highlighting) just rendered smaller, so it behaves like any other
        // icon instead of being a dead picture.
        icons.appendChild(rn ? makeTile(rn, q, true) : placeholderReqTile(tok));
      }
      box.appendChild(head);
      box.appendChild(icons);
    } else {
      box.innerHTML = `<div class="req-head none">Always available</div>`;
    }
    const tiles = document.createElement("div");
    tiles.className = "tiles";
    for (const n of group.nodes) tiles.appendChild(makeTile(n, q));
    box.appendChild(tiles);
    wrap.appendChild(box);
  }
  return wrap;
}

function placeholderReqTile(label) {
  const el = document.createElement("div");
  el.className = "tile compact dim";
  el.innerHTML = `<div class="placeholder" style="background:#333b48">${label.slice(0, 22)}</div>`;
  return el;
}

function matches(n, q) {
  if (!q) return true;
  return (n.name || "").toLowerCase().includes(q) ||
    n.id.toLowerCase().includes(q) ||
    (n.prereqs || []).some((p) => p.toLowerCase().includes(q)) ||
    (n.provides || []).some((p) => p.toLowerCase().includes(q));
}

function makeTile(n, q, compact) {
  const el = document.createElement("div");
  el.className = "tile" + (compact ? " compact" : "") + (matches(n, q) ? "" : " dim");
  el.dataset.id = n.id;
  const visual = n.png
    ? `<img class="cameo" loading="lazy" src="icons/${n.png}" alt="">`
    : `<div class="placeholder" style="background:${qc(n.queue)}">${(n.name || n.id).slice(0, 22)}</div>`;
  const cost = n.cost != null
    ? `<div class="cost${n.cost === 0 ? " free" : ""}">$${n.cost}</div>`
    : `<div class="cost free">—</div>`;
  el.innerHTML = `${visual}<div class="nm">${n.name || n.id}</div>${cost}`;
  el.addEventListener("mouseenter", (e) => { showTip(n, e); applyLinks(n); });
  el.addEventListener("mousemove", moveTip);
  el.addEventListener("mouseleave", () => { $("tip").classList.add("hidden"); clearLinks(); });
  el.addEventListener("click", () => { $("tip").classList.add("hidden"); openDetail(n); });
  return el;
}

// Hover-link highlight: green outline on the hovered tile, orange on what it
// requires, blue on what it unlocks (reverse-prerequisite). Toggled by #showLinks.
function clearLinks() {
  $("grid").querySelectorAll(".hover-focus,.req-link,.unlock-link").forEach((el) => {
    el.classList.remove("hover-focus", "req-link", "unlock-link");
  });
  for (const box of [$("offTop"), $("offBottom")]) {
    box.classList.add("hidden");
    box.innerHTML = "";
  }
}

function applyLinks(n) {
  if (!$("showLinks").checked) return;
  clearLinks();
  const grid = $("grid");
  // A node can appear as more than one tile (its own section, plus a compact
  // copy in any Upgrade "Requires:" header), so highlight every copy.
  const tilesFor = (id) => [...grid.querySelectorAll(`.tile[data-id="${id}"]`)];

  for (const el of tilesFor(n.id)) el.classList.add("hover-focus");

  const offscreen = [];
  const markLinked = (id, cls) => {
    for (const el of tilesFor(id)) {
      el.classList.add(cls);
      // Compact copies (Upgrade "Requires:" icons) are secondary references
      // to the same unit - skip them for the offscreen indicator so it only
      // ever points at a unit's one "real" tile.
      if (el.classList.contains("compact")) continue;
      const r = el.getBoundingClientRect();
      if (r.bottom < headerBottom()) offscreen.push({ el, cls, dir: "above" });
      else if (r.top > innerHeight) offscreen.push({ el, cls, dir: "below" });
    }
  };

  for (const tok of n.prereqs || []) {
    const rn = TOKEN_NODES[tok.toLowerCase()];
    if (rn) markLinked(rn.id, "req-link");
  }
  for (const u of unlocks(n)) markLinked(u.id, "unlock-link");

  showOffscreenIndicators(offscreen);
}

function headerBottom() {
  return document.querySelector("header").getBoundingClientRect().bottom;
}

// Small floating strips above/below the viewport listing highlighted tiles
// that scrolled out of view, so a hover's prereqs/unlocks aren't invisible.
function showOffscreenIndicators(items) {
  const above = items.filter((i) => i.dir === "above");
  const below = items.filter((i) => i.dir === "below");
  fillIndicator($("offTop"), above, headerBottom() + "px", null);
  fillIndicator($("offBottom"), below, null, "28px"); // clear the fixed footer bar
}

function fillIndicator(box, items, top, bottom) {
  if (!items.length) {
    box.classList.add("hidden");
    box.innerHTML = "";
    return;
  }
  box.style.top = top ?? "";
  box.style.bottom = bottom ?? "";
  box.innerHTML = items.map(({ el, cls }) => {
    const src = el.querySelector("img")?.src ?? "";
    const label = el.querySelector(".nm")?.textContent ?? "";
    const visual = src
      ? `<img class="off-chip ${cls}" src="${src}" alt="">`
      : `<div class="off-chip ${cls} placeholder"></div>`;
    return `<div class="off-item" data-id="${el.dataset.id}">${visual}<div class="off-nm">${label}</div></div>`;
  }).join("");
  box.classList.remove("hidden");
}

function scrollToChip(e) {
  const item = e.target.closest(".off-item");
  if (!item) return;
  const target = $("grid").querySelector(`.tile[data-id="${item.dataset.id}"]`);
  if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
}

function statRows(n) {
  const s = n.stats || {};
  const rows = [];
  rows.push(["actor", n.id]);
  if (n.queue) rows.push(["queue", n.queue]);
  rows.push(["cost", n.cost != null ? "$" + n.cost : "—"]);
  if (s.hp != null) rows.push(["hp", s.hp]);
  if (s.armor) rows.push(["armor", s.armor]);
  if (s.speed != null) rows.push(["speed", s.speed.toFixed(2) + " tiles/sec"]);
  if (s.sight) rows.push(["sight", s.sight.toFixed(2) + " tiles"]);
  if (s.power != null) rows.push(["power", (s.power > 0 ? "+" : "") + s.power]);
  if (n.buildLimit != null) rows.push(["limit", n.buildLimit]);
  return rows;
}

function showTip(n, e) {
  const tip = $("tip");
  tip.innerHTML =
    `<h3>${n.name || n.id}</h3>` +
    `<dl>${statRows(n).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>` +
    `<div class="sec">click for full details</div>`;
  tip.classList.remove("hidden");
  moveTip(e);
}

function prereqName(token) {
  const k = token.toLowerCase();
  return FACNAMES[k] || (DATA.prereqNames && DATA.prereqNames[k]) || null;
}

// Other units in the same faction that need one of this unit's provided
// tokens as a prerequisite (the inverse of "Prerequisites").
function unlocks(n) {
  const tokens = new Set((n.provides || []).map((p) => p.toLowerCase()));
  if (!tokens.size) return [];
  const seen = new Set();
  const out = [];
  for (const other of CUR_NODES) {
    if (other.id === n.id || seen.has(other.id)) continue;
    if ((other.prereqs || []).some((p) => tokens.has(p.toLowerCase()))) {
      seen.add(other.id);
      out.push(other);
    }
  }
  return out;
}

function weaponListHtml(list) {
  return "<ul>" + list.map((w) => {
    const bits = [];
    if (w.damage != null) bits.push(w.damage + " dmg");
    if (w.range != null) bits.push("range " + w.range.toFixed(2) + " tiles");
    if (w.reload != null) bits.push("reload " + w.reload.toFixed(2) + "s");
    return `<li class="weap">` +
      `<div class="wl1"><span class="wn">${w.name}</span>` +
      (w.dps != null ? `<span class="dps">${w.dps.toFixed(1)} DPS</span>` : "") + `</div>` +
      (bits.length ? `<div class="ws">${bits.join(" · ")}</div>` : "") +
      "</li>";
  }).join("") + "</ul>";
}

function openDetail(n) {
  const visual = n.png
    ? `<img src="icons/${n.png}" alt="">`
    : `<div class="ph" style="background:${qc(n.queue)}"></div>`;

  const description = n.description
    ? `<p class="descr">${n.description}</p>`
    : "";

  const s = n.stats || {};
  let weapons = '<p class="empty">None</p>';
  if (s.weapons && s.weapons.length) {
    const hasEliteSplit = s.weapons.some((w) => w.elite === true);
    if (hasEliteSplit) {
      const standard = s.weapons.filter((w) => w.elite !== true);
      const elite = s.weapons.filter((w) => w.elite === true);
      weapons =
        `<h4>Standard</h4>${weaponListHtml(standard)}` +
        `<h4>Elite (rank 3)</h4>${weaponListHtml(elite)}`;
    } else {
      weapons = weaponListHtml(s.weapons);
    }
  }

  let prereqs = '<p class="empty">None</p>';
  if (n.prereqs && n.prereqs.length) {
    prereqs = '<div class="prereqs">' + n.prereqs.map((p) => {
      const name = prereqName(p);
      return name
        ? `<span class="prereq">${name}</span>`
        : `<span class="prereq raw">${p}</span>`;
    }).join("") + "</div>";
  }

  const unlocked = unlocks(n);
  let unlocksHtml = '<p class="empty">Nothing</p>';
  if (unlocked.length) {
    unlocksHtml = '<div class="prereqs">' + unlocked.map((u) =>
      `<span class="prereq unlock" data-id="${u.id}">${u.name || u.id}</span>`
    ).join("") + "</div>";
  }

  $("detailBody").innerHTML =
    `<div class="head">${visual}<div><h2>${n.name || n.id}</h2>` +
    `<div class="sub">${n.id}${n.queue ? " · " + n.queue : ""}${n.cost != null ? " · $" + n.cost : ""}</div></div></div>` +
    description +
    `<h3>Stats</h3><dl class="stats">${statRows(n).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>` +
    `<h3>Weapons</h3>${weapons}` +
    `<h3>Prerequisites</h3>${prereqs}` +
    `<h3>Unlocks</h3>${unlocksHtml}`;
  $("overlay").classList.remove("hidden");
}

function closeDetail() {
  $("overlay").classList.add("hidden");
}

function moveTip(e) {
  const tip = $("tip");
  const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
  let x = e.clientX + pad, y = e.clientY + pad;
  if (x + w > innerWidth) x = e.clientX - w - pad;
  if (y + h > innerHeight) y = e.clientY - h - pad;
  tip.style.left = Math.max(4, x) + "px";
  tip.style.top = Math.max(4, y) + "px";
}

boot();
