# Cameo Tech Tree

Interactive production / prerequisite graph for the [Cameo-mod](https://github.com/cameo-mod/Cameo-mod)
factions. Live at **https://blackrobe.github.io/cameo-techtree/**.

Pick a theme + faction; nodes are buildable actors coloured by production queue,
edges point from a prerequisite to what it unlocks. Click a node for cost /
queue / prerequisites; use **Find** to highlight an actor or prereq token.
"hide upgrades/research" (on by default) trims the tech/upgrade actors so the
view shows the core production tree.

## Updating the data

The site is a static page that reads `data/techtree.json`. Regenerate it from
the **upstream** Cameo-mod repo, then commit & push:

```cmd
update.cmd
```

That shallow-clones `cameo-mod/Cameo-mod@master` (sparse: `mods/cameo` only)
into `tools/.cache/`, parses the active rules, and rewrites
`data/techtree.json`. Re-runs reuse the cache (fetch + reset).

Options (passed through to `tools/extract.py`):

| flag | meaning |
|------|---------|
| `--ref <branch/tag>` | parse a different upstream ref (default `master`) |
| `--mod "<path>\mods\cameo"` | parse a **local** checkout instead of fetching upstream |
| `--repo <git-url>` | parse a different fork |
| `--out <file>` | write somewhere other than `data/techtree.json` |

Requires Python 3 and `git` on PATH. After regenerating:

```cmd
git add cameo-techtree/data/techtree.json
git commit -m "Update Cameo tech tree data"
git push
```

## How faction assignment works

* **Content-pack themes** (Tiberian Dawn, Dune 2000, Red Alert 2 Mod) are split
  by the per-faction folder structure under `ContentPacks/` — authoritative.
* **Monolithic themes** (Red Alert, StarCraft, …) have no per-faction files, so
  factions are inferred by propagating membership through the prerequisite
  graph from each faction's root buildings. This is approximate; the UI shows a
  "⚠ approximate faction split" badge. Themes whose factions don't separate
  cleanly (e.g. Tiberian Sun) are shown as a single "All units" roster rather
  than several near-identical trees. Seed tokens live in `SEED_TOKENS` in
  `tools/extract.py` and can be refined per theme.

## Files

```
index.html      page shell + CDN libs (cytoscape + dagre layout)
app.js          loads techtree.json, builds the graph, search/info panel
style.css       dark theme
tools/extract.py  MiniYaml parser + inheritance resolver + graph builder
update.cmd      one-command regenerate-from-upstream
data/techtree.json  generated data (committed)
```
