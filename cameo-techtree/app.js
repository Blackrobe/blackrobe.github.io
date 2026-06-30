"use strict";

const QUEUE_COLORS = {
  Building:  "#4a90d9",
  Defense:   "#7a5cc4",
  Infantry:  "#3fa34d",
  Vehicle:   "#d98a3f",
  Armor:     "#d98a3f",
  Aircraft:  "#46b3b3",
  Ship:      "#3f6fd9",
  Naval:     "#3f6fd9",
  Upgrade:   "#b3457a",
  Support:   "#c4a23f",
  Defaultx:  "#888888",
};
const DEFAULT_COLOR = "#6b7280";

function queueColor(q) {
  if (!q) return DEFAULT_COLOR;
  for (const key in QUEUE_COLORS) {
    if (q.toLowerCase().startsWith(key.toLowerCase())) return QUEUE_COLORS[key];
  }
  return DEFAULT_COLOR;
}

let DATA = null;
let cy = null;

const $ = (id) => document.getElementById(id);

async function boot() {
  try {
    const res = await fetch("data/techtree.json", { cache: "no-cache" });
    DATA = await res.json();
  } catch (e) {
    $("cy").innerHTML = '<p style="padding:20px">Could not load data/techtree.json</p>';
    return;
  }
  if (DATA.generated) $("gen").textContent = "· data: " + DATA.generated;

  const themeSel = $("theme");
  DATA.themes.forEach((t, i) => {
    const o = document.createElement("option");
    o.value = i;
    o.textContent = `${t.name} (${t.factions.length})`;
    themeSel.appendChild(o);
  });
  themeSel.addEventListener("change", onThemeChange);
  $("faction").addEventListener("change", render);
  $("search").addEventListener("input", onSearch);
  $("hideHidden").addEventListener("change", render);
  $("infoClose").addEventListener("click", () => $("info").classList.add("hidden"));

  buildLegend();
  onThemeChange();
}

function onThemeChange() {
  const t = DATA.themes[+$("theme").value];
  const facSel = $("faction");
  facSel.innerHTML = "";
  t.factions.forEach((f, i) => {
    const o = document.createElement("option");
    o.value = i;
    o.textContent = `${f.name} (${f.nodes.length})`;
    facSel.appendChild(o);
  });
  render();
}

function currentFaction() {
  const t = DATA.themes[+$("theme").value];
  return t.factions[+$("faction").value];
}

function render() {
  const fac = currentFaction();
  if (!fac) return;
  const hideHidden = $("hideHidden").checked;

  const visible = fac.nodes.filter((n) => !(hideHidden && n.hidden));
  const ids = new Set(visible.map((n) => n.id));

  const elements = [];
  for (const n of visible) {
    elements.push({
      data: {
        id: n.id,
        label: n.name || n.id,
        queue: n.queue || "",
        color: queueColor(n.queue),
        node: n,
      },
    });
  }
  let edgeId = 0;
  for (const e of fac.edges) {
    if (ids.has(e.from) && ids.has(e.to)) {
      elements.push({
        data: { id: "e" + edgeId++, source: e.from, target: e.to, token: e.token },
      });
    }
  }

  if (cy) cy.destroy();
  cy = cytoscape({
    container: $("cy"),
    elements,
    style: cyStyle(),
    layout: {
      name: "dagre",
      rankDir: "LR",
      nodeSep: 14,
      rankSep: 70,
      edgeSep: 8,
    },
    wheelSensitivity: 0.25,
  });

  cy.on("tap", "node", (evt) => showInfo(evt.target.data("node")));
  cy.on("tap", (evt) => { if (evt.target === cy) $("info").classList.add("hidden"); });

  $("meta").textContent =
    `${visible.length} actors · ${elements.length - visible.length} edges`;
  const theme = DATA.themes[+$("theme").value];
  $("approx").classList.toggle("hidden", !!theme.accurate);
  onSearch();
}

function cyStyle() {
  return [
    {
      selector: "node",
      style: {
        "background-color": "data(color)",
        label: "data(label)",
        color: "#fff",
        "font-size": 10,
        "text-valign": "center",
        "text-halign": "center",
        "text-outline-color": "#0009",
        "text-outline-width": 2,
        width: "label",
        height: 22,
        padding: "6px",
        shape: "round-rectangle",
        "text-wrap": "none",
      },
    },
    {
      selector: "edge",
      style: {
        width: 1.4,
        "line-color": "#4a5568",
        "target-arrow-color": "#4a5568",
        "target-arrow-shape": "triangle",
        "arrow-scale": 0.8,
        "curve-style": "bezier",
        opacity: 0.7,
      },
    },
    { selector: ".dim", style: { opacity: 0.12 } },
    { selector: ".hit", style: { "border-width": 3, "border-color": "#f0b429" } },
    {
      selector: "node:selected",
      style: { "border-width": 3, "border-color": "#fff" },
    },
  ];
}

function onSearch() {
  if (!cy) return;
  const q = $("search").value.trim().toLowerCase();
  cy.batch(() => {
    cy.elements().removeClass("dim hit");
    if (!q) return;
    const match = cy.nodes().filter((n) => {
      const nd = n.data("node");
      return (
        (nd.name || "").toLowerCase().includes(q) ||
        nd.id.toLowerCase().includes(q) ||
        (nd.provides || []).some((p) => p.toLowerCase().includes(q)) ||
        (nd.prereqs || []).some((p) => p.toLowerCase().includes(q))
      );
    });
    if (match.length) {
      cy.elements().addClass("dim");
      const keep = match.union(match.connectedEdges()).union(match.neighborhood());
      keep.removeClass("dim");
      match.addClass("hit");
    }
  });
}

function showInfo(n) {
  const body = $("infoBody");
  const tags = (arr) =>
    (arr && arr.length)
      ? `<div class="taglist">${arr
          .map((t) => `<span class="tag" data-q="${t}">${t}</span>`)
          .join("")}</div>`
      : '<span style="color:var(--muted)">—</span>';
  body.innerHTML = `
    <h2>${n.name || n.id}</h2>
    <dl>
      <dt>actor</dt><dd>${n.id}</dd>
      <dt>queue</dt><dd>${n.queue || "—"}</dd>
      <dt>cost</dt><dd>${n.cost != null ? "$" + n.cost : "—"}</dd>
      ${n.buildLimit != null ? `<dt>limit</dt><dd>${n.buildLimit}</dd>` : ""}
      ${n.icon ? `<dt>icon</dt><dd>${n.icon}</dd>` : ""}
    </dl>
    <p style="margin:8px 0 2px;color:var(--muted)">prerequisites</p>${tags(n.prereqs)}
    <p style="margin:8px 0 2px;color:var(--muted)">provides</p>${tags(n.provides)}
  `;
  body.querySelectorAll(".tag").forEach((el) =>
    el.addEventListener("click", () => {
      $("search").value = el.dataset.q;
      onSearch();
    })
  );
  $("info").classList.remove("hidden");
}

function buildLegend() {
  const seen = ["Building", "Defense", "Infantry", "Vehicle", "Aircraft", "Ship", "Upgrade", "Support"];
  $("legend").innerHTML = seen
    .map(
      (q) =>
        `<div class="row"><span class="swatch" style="background:${queueColor(q)}"></span>${q}</div>`
    )
    .join("");
}

boot();
