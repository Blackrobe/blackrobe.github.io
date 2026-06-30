"use strict";

const QUEUE_ORDER = ["Building", "Defense", "Infantry", "Vehicle", "Aircraft", "Ship", "Upgrade", ""];
const QUEUE_COLORS = {
  Building: "#4a90d9", Defense: "#7a5cc4", Infantry: "#3fa34d", Vehicle: "#d98a3f",
  Aircraft: "#46b3b3", Ship: "#3f6fd9", Upgrade: "#b3457a", "": "#6b7280",
};
const qc = (q) => QUEUE_COLORS[q] ?? "#6b7280";

const $ = (id) => document.getElementById(id);
let DATA = null;

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
    $("theme").appendChild(o);
  });
  $("theme").addEventListener("change", onTheme);
  $("faction").addEventListener("change", render);
  $("search").addEventListener("input", render);
  $("showUpg").addEventListener("change", render);
  onTheme();
}

function onTheme() {
  const t = DATA.themes[+$("theme").value];
  const fs = $("faction");
  fs.innerHTML = "";
  t.factions.forEach((f, i) => {
    const o = document.createElement("option");
    o.value = i; o.textContent = `${f.name} (${f.nodes.filter(n => !n.hidden).length})`;
    fs.appendChild(o);
  });
  $("approx").classList.toggle("hidden", !!t.accurate);
  render();
}

function render() {
  const t = DATA.themes[+$("theme").value];
  const fac = t.factions[+$("faction").value];
  if (!fac) return;
  const showUpg = $("showUpg").checked;
  const q = $("search").value.trim().toLowerCase();

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
    const tiles = document.createElement("div");
    tiles.className = "tiles";
    for (const n of list) tiles.appendChild(makeTile(n, q));
    sec.appendChild(tiles);
    grid.appendChild(sec);
  }
  if (!grid.children.length) grid.innerHTML = '<p style="color:var(--muted)">No units match.</p>';
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
  const visual = n.png
    ? `<img class="cameo" loading="lazy" src="icons/${n.png}" alt="">`
    : `<div class="placeholder" style="background:${qc(n.queue)}">${(n.name || n.id).slice(0, 22)}</div>`;
  const cost = n.cost != null
    ? `<div class="cost${n.cost === 0 ? " free" : ""}">$${n.cost}</div>`
    : `<div class="cost free">—</div>`;
  el.innerHTML = `${visual}<div class="nm">${n.name || n.id}</div>${cost}`;
  el.addEventListener("mouseenter", (e) => showTip(n, e));
  el.addEventListener("mousemove", moveTip);
  el.addEventListener("mouseleave", () => $("tip").classList.add("hidden"));
  return el;
}

function showTip(n, e) {
  const s = n.stats || {};
  const rows = [];
  rows.push(["actor", n.id]);
  if (n.queue) rows.push(["queue", n.queue]);
  rows.push(["cost", n.cost != null ? "$" + n.cost : "—"]);
  if (s.hp != null) rows.push(["hp", s.hp]);
  if (s.armor) rows.push(["armor", s.armor]);
  if (s.speed != null) rows.push(["speed", s.speed]);
  if (s.sight) rows.push(["sight", s.sight]);
  if (s.power != null) rows.push(["power", (s.power > 0 ? "+" : "") + s.power]);
  if (n.buildLimit != null) rows.push(["limit", n.buildLimit]);

  let weap = "";
  if (s.weapons && s.weapons.length) {
    weap = '<div class="sec">weapons</div>' + s.weapons.map((w) =>
      `${w.name}${w.damage != null ? " · " + w.damage + " dmg" : ""}${w.range ? " · rng " + w.range : ""}`
    ).join("<br>");
  }
  const tags = (arr) => arr && arr.length
    ? `<div class="tags">${arr.map((x) => `<span class="tag">${x}</span>`).join("")}</div>`
    : '<span style="color:var(--muted)">—</span>';

  const tip = $("tip");
  tip.innerHTML =
    `<h3>${n.name || n.id}</h3>` +
    `<dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>` +
    weap +
    `<div class="sec">prerequisites</div>${tags(n.prereqs)}`;
  tip.classList.remove("hidden");
  moveTip(e);
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
