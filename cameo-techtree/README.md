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
into `tools/.cache/`, parses the active rules, and rewrites **both** datasets:

* `cameo-techtree/data/techtree.json` — the graph view (this folder).
* `cameo-units/data/units.json` + `cameo-units/icons/*.png` — the
  [roster view](../cameo-units/) (cameo icons + cost/HP/armour/weapon stats).

Re-runs reuse the cache (fetch + reset). Add `--no-icons` to skip copying
cameos. The extractor follows the upstream content-pack `Include` structure, so
it keeps working as themes migrate to per-faction wrapper packs.

Options (passed through to `tools/extract.py`):

| flag | meaning |
|------|---------|
| `--ref <branch/tag>` | parse a different upstream ref (default `master`) |
| `--mod "<path>\mods\cameo"` | parse a **local** checkout instead of fetching upstream |
| `--repo <git-url>` | parse a different fork |
| `--out <file>` | write somewhere other than `data/techtree.json` |

### Regenerating cameo icons

The cameo PNGs in `cameo-units/icons/` are rendered from the mod sprites by an
OpenRA utility command, `--export-cameos` (source kept for reference at
`tools/engine/ExportCameosCommand.cs`; it lives in `OpenRA.Mods.Cameo/` in the
Cameo-mod repo and must be compiled into the mod — `./make all`). It renders
every buildable actor's icon sequence — SHP and PNG alike — to a single PNG, so
this is what gives ~100% coverage instead of the ~half that ship as loose PNGs.

Run it once into the extractor's cache, then regenerate:

```cmd
update-icons.cmd          :: runs OpenRA.Utility --export-cameos into tools\.cache\cameos
update.cmd                :: extract.py then prefers those cameos
```

`extract.py` auto-uses `tools\.cache\cameos\` when present (override with
`--cameo-dir`); without it, it falls back to copying the loose on-disk PNG
cameos only. The icons folder is rebuilt each run, so stale art is dropped.

### Publishing

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
