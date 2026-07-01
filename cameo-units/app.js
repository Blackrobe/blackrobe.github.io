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
  $("search").addEventListener("input", render);
  $("showUpg").addEventListener("change", render);
  $("showLinks").addEventListener("change", clearLinks);
  $("detailClose").addEventListener("click", closeDetail);
  $("overlay").addEventListener("click", (e) => { if (e.target === $("overlay")) closeDetail(); });
  $("detailBody").addEventListener("click", (e) => {
    const el = e.target.closest(".unlock");
    if (!el) return;
    const target = CUR_NODES.find((n) => n.id === el.dataset.id);
    if (target) openDetail(target);
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDetail(); });
  onTheme(true);
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
      const items = group.tokens.map((tok) => {
        const rn = tokenNodes[tok];
        const label = rn ? (rn.name || rn.id) : tok;
        const icon = rn && rn.png
          ? `<img class="req-icon" src="icons/${rn.png}" alt="">`
          : `<div class="req-icon ph"></div>`;
        return `<div class="req-item">${icon}<span>${label}</span></div>`;
      }).join("");
      box.innerHTML = `<div class="req-head">Requires:</div><div class="req-icons">${items}</div>`;
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

function matches(n, q) {
  if (!q) return true;
  return (n.name || "").toLowerCase().includes(q) ||
    n.id.toLowerCase().includes(q) ||
    (n.prereqs || []).some((p) => p.toLowerCase().includes(q)) ||
    (n.provides || []).some((p) => p.toLowerCase().includes(q));
}

function makeTile(n, q) {
  const el = document.createElement("div");
  el.className = "tile" + (matches(n, q) ? "" : " dim");
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
}

function applyLinks(n) {
  if (!$("showLinks").checked) return;
  clearLinks();
  const grid = $("grid");
  const tileFor = (id) => grid.querySelector(`.tile[data-id="${id}"]`);

  const self = tileFor(n.id);
  if (self) self.classList.add("hover-focus");

  for (const tok of n.prereqs || []) {
    const rn = TOKEN_NODES[tok.toLowerCase()];
    const el = rn && tileFor(rn.id);
    if (el) el.classList.add("req-link");
  }

  for (const u of unlocks(n)) {
    const el = tileFor(u.id);
    if (el) el.classList.add("unlock-link");
  }
}

function statRows(n) {
  const s = n.stats || {};
  const rows = [];
  rows.push(["actor", n.id]);
  if (n.queue) rows.push(["queue", n.queue]);
  rows.push(["cost", n.cost != null ? "$" + n.cost : "—"]);
  if (s.hp != null) rows.push(["hp", s.hp]);
  if (s.armor) rows.push(["armor", s.armor]);
  if (s.speed != null) rows.push(["speed", s.speed]);
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
