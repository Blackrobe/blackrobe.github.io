#!/usr/bin/env python
"""Extract the Cameo-mod production/tech tree into techtree.json.

Parses OpenRA "MiniYaml" rules for the active mod (per mod.yaml), resolves
trait inheritance, then walks Buildable / ProvidesPrerequisite traits to build
a per-faction prerequisite graph the static viewer renders.

Run:  python extract.py [--mod <path-to-mods/cameo>] [--out <techtree.json>]
Defaults assume the Cameo-mod checkout sits next to this github.io repo.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# MiniYaml parsing
# ---------------------------------------------------------------------------


class Node:
    __slots__ = ("key", "value", "children")

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.children = []

    def child(self, key):
        for c in self.children:
            if c.key == key:
                return c
        return None

    def child_value(self, key, default=None):
        c = self.child(key)
        if c is None or c.value is None:
            return default
        return c.value


def _strip_comment(line):
    # OpenRA treats '#' as a comment start unless escaped as '\#'.
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "#":
            if i > 0 and line[i - 1] == "\\":
                out[-1] = "#"  # replace the backslash with literal '#'
                i += 1
                continue
            break
        out.append(ch)
        i += 1
    return "".join(out)


def _indent_of(line):
    n = 0
    for ch in line:
        if ch == "\t":
            n += 1
        else:
            break
    return n


def parse_miniyaml(text):
    """Parse MiniYaml text into a list of top-level Nodes."""
    roots = []
    # stack of (indent, node)
    stack = []
    for raw in text.splitlines():
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = _indent_of(line)
        content = line.strip()
        if ":" in content:
            key, _, value = content.partition(":")
            key = key.strip()
            value = value.strip()
            value = value if value != "" else None
        else:
            key = content
            value = None
        node = Node(key, value)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            roots.append(node)
        else:
            stack[-1][1].children.append(node)
        stack.append((indent, node))
    return roots


# ---------------------------------------------------------------------------
# Node merging (MiniYaml combine semantics) + inheritance
# ---------------------------------------------------------------------------


def merge_children(base, override):
    """Merge override children into base children (OpenRA combine rules).

    Returns a new list. '-Key' removes; matching key merges recursively;
    new key appends. Value on override replaces base value when present.
    """
    result = [clone_node(c) for c in base]

    def find(key):
        for c in result:
            if c.key == key:
                return c
        return None

    for o in override:
        if o.key.startswith("-") and o.value is None and not o.children:
            target = o.key[1:]
            result[:] = [c for c in result if c.key != target]
            continue
        existing = find(o.key)
        if existing is None:
            result.append(clone_node(o))
        else:
            if o.value is not None:
                existing.value = o.value
            existing.children = merge_children(existing.children, o.children)
    return result


def clone_node(node):
    n = Node(node.key, node.value)
    n.children = [clone_node(c) for c in node.children]
    return n


# ---------------------------------------------------------------------------
# Rule set: load all active files, merge actors, resolve inheritance
# ---------------------------------------------------------------------------


class RuleSet:
    def __init__(self):
        # name(lower) -> merged Node (pre-inheritance)
        self.raw = {}
        # name(lower) -> resolved Node (post-inheritance)
        self._resolved = {}
        # name(lower) -> set of (theme, faction) attributions
        self.attribution = {}

    def add_file(self, text, theme, faction):
        for node in parse_miniyaml(text):
            name = node.key
            low = name.lower()
            if low in self.raw:
                self.raw[low].children = merge_children(
                    self.raw[low].children, node.children
                )
                if node.value is not None:
                    self.raw[low].value = node.value
            else:
                self.raw[low] = clone_node(node)
            if theme is not None:
                self.attribution.setdefault(low, set()).add((theme, faction))

    def resolve(self, name, _seen=None):
        low = name.lower()
        if low in self._resolved:
            return self._resolved[low]
        node = self.raw.get(low)
        if node is None:
            return None
        if _seen is None:
            _seen = set()
        if low in _seen:
            return node  # inheritance cycle guard
        _seen.add(low)

        # Gather inherited parents (Inherits / Inherits@tag) in order.
        merged = []
        own = []
        for c in node.children:
            if c.key == "Inherits" or c.key.startswith("Inherits@"):
                parent = self.resolve(c.value, _seen) if c.value else None
                if parent is not None:
                    merged = merge_children(merged, parent.children)
            else:
                own.append(c)
        merged = merge_children(merged, own)

        out = Node(node.key, node.value)
        out.children = merged
        self._resolved[low] = out
        return out

    def actors(self):
        for low in self.raw:
            if low.startswith("^"):
                continue
            yield low, self.resolve(low)


# ---------------------------------------------------------------------------
# mod.yaml loading
# ---------------------------------------------------------------------------


def resolve_pkg_path(ref, mod_dir):
    """Resolve a 'prefix|relative' rules reference to a filesystem path."""
    ref = ref.strip()
    if "|" in ref:
        prefix, _, rel = ref.partition("|")
        prefix = prefix.strip()
        rel = rel.strip()
        if prefix == "cameo":
            return os.path.join(mod_dir, rel)
        if prefix == "ContentPacks":
            return os.path.join(mod_dir, "ContentPacks", rel)
        # common| and engine refs: not part of the mod's own tech tree
        return None
    return os.path.join(mod_dir, ref)


def faction_from_path(path, mod_dir):
    """Infer (theme, faction) from a ContentPacks path; else (None, None)."""
    norm = os.path.normpath(path)
    parts = norm.split(os.sep)
    if "ContentPacks" in parts:
        i = parts.index("ContentPacks")
        theme = parts[i + 1] if i + 1 < len(parts) else None
        faction = parts[i + 2] if i + 2 < len(parts) else None
        return theme, faction
    return None, None


def collect_active_files(mod_dir):
    """Return list of (abs_path, theme, faction) for active rules files."""
    mod_yaml = os.path.join(mod_dir, "mod.yaml")
    with open(mod_yaml, encoding="utf-8") as f:
        roots = parse_miniyaml(f.read())

    files = []
    seen = set()

    def add(path, theme, faction):
        if path and path not in seen and os.path.isfile(path):
            seen.add(path)
            files.append((path, theme, faction))

    # Rules: section (monolithic + base)
    for node in roots:
        if node.key == "Rules":
            for c in node.children:
                p = resolve_pkg_path(c.key, mod_dir)
                if p:
                    theme = monolithic_theme(c.key)
                    add(p, theme, None)
        if node.key == "Include":
            # Include: ContentPacks/Theme/Faction/content.yaml
            inc = resolve_pkg_path("cameo|" + node.value, mod_dir) if node.value else None
            if inc and os.path.isfile(inc):
                with open(inc, encoding="utf-8") as cf:
                    for cn in parse_miniyaml(cf.read()):
                        if cn.key == "Rules":
                            for rc in cn.children:
                                p = resolve_pkg_path(rc.key, mod_dir)
                                theme, faction = faction_from_path(p or "", mod_dir)
                                add(p, theme, faction)
    return files


MONOLITHIC_THEMES = {
    "redalert.yaml": "RedAlert",
    "tiberiansun.yaml": "TiberianSun",
    "redalert2.yaml": "RedAlert2",
    "starcraft.yaml": "StarCraft",
    "warcraft2.yaml": "WarCraft2",
    "outpost2.yaml": "Outpost2",
    "tkm.yaml": "TKM",
}


def monolithic_theme(ref):
    base = ref.split("|")[-1].split("/")[-1]
    return MONOLITHIC_THEMES.get(base)


# ---------------------------------------------------------------------------
# Actor field extraction
# ---------------------------------------------------------------------------

# Queue name -> display bucket (used for colouring / classification).
UPGRADE_QUEUES = {"Upgrade", "Upgrades"}


def split_list(value):
    if not value:
        return []
    return [t.strip() for t in value.split(",") if t.strip()]


def actor_provides(name, node):
    """Prerequisite tokens this actor provides (lowercased)."""
    tokens = set()
    for c in node.children:
        if c.key == "ProvidesPrerequisite" or c.key.startswith("ProvidesPrerequisite@"):
            pre = c.child_value("Prerequisite")
            if pre:
                tokens.add(pre.strip().lower())
            else:
                # OpenRA default: the actor's own (lowercased) name.
                tokens.add(name.lower())
    # An actor name is also directly referenceable as a prerequisite.
    tokens.add(name.lower())
    return tokens


def actor_buildable(node):
    """Return dict of buildable fields, or None if not buildable."""
    b = node.child("Buildable")
    if b is None:
        return None
    queue = b.child_value("Queue")
    queues = split_list(queue)
    prereqs = split_list(b.child_value("Prerequisites"))
    build_limit = b.child_value("BuildLimit")
    icon = b.child_value("Icon")
    return {
        "queues": queues,
        "prereqs": prereqs,
        "buildLimit": int(build_limit) if (build_limit and build_limit.lstrip("-").isdigit()) else None,
        "icon": icon,
    }


def actor_name(node):
    t = node.child("Tooltip")
    if t is None:
        t = node.child("EditorOnlyTooltip")
    if t is not None:
        nm = t.child_value("Name")
        if nm:
            return nm
    return None


def actor_cost(node):
    v = node.child("Valued")
    if v is not None:
        c = v.child_value("Cost")
        if c and c.lstrip("-").isdigit():
            return int(c)
    return None


def actor_render_image(node):
    rs = node.child("RenderSprites")
    if rs is not None:
        return rs.child_value("Image")
    return None


# ---------------------------------------------------------------------------
# Faction / theme model
# ---------------------------------------------------------------------------

# Content-pack themes: faction attribution comes from folder structure.
CONTENT_THEMES = {
    "TiberianDawn": "Tiberian Dawn",
    "D2k": "Dune 2000",
    "RedAlert2Mod": "Red Alert 2 (Mod)",
}

# Monolithic themes: faction attribution by dot-segment suffix in the actor
# name or its prerequisite tokens. (id, display, [suffix aliases]).
MONO_FACTIONS = {
    "RedAlert": [
        ("allies", "Allies", ["allies"]),
        ("soviet", "Soviet", ["soviet"]),
        ("japan", "Japan", ["japan", "modjapan"]),
    ],
    "TiberianSun": [
        ("tsgdi", "GDI", ["tsgdi", "gdi"]),
        ("tsnod", "Nod", ["tsnod", "nod"]),
        ("forgotten", "Forgotten", ["forgotten"]),
    ],
    "RedAlert2": [
        ("ra2america", "Allies", ["america", "ra2america", "usa", "allies"]),
        ("ra2russia", "Soviet", ["russia", "ra2russia", "soviet"]),
        ("yuri", "Yuri", ["yuri"]),
    ],
    "StarCraft": [
        ("terran", "Terran", ["terran"]),
        ("protoss", "Protoss", ["protoss"]),
        ("zerg", "Zerg", ["zerg"]),
    ],
    "WarCraft2": [
        ("human2", "Human", ["human2", "human"]),
        ("orc2", "Orc", ["orc2", "orc"]),
    ],
    "Outpost2": [
        ("plymouthl", "Plymouth", ["plymouth", "plymouthl"]),
        ("edenl", "Eden", ["eden", "edenl"]),
    ],
    "TKM": [
        ("tkm", "TKM", ["tkm"]),
    ],
}
MONO_THEME_NAMES = {
    "RedAlert": "Red Alert",
    "TiberianSun": "Tiberian Sun",
    "RedAlert2": "Red Alert 2",
    "StarCraft": "StarCraft",
    "WarCraft2": "Warcraft 2",
    "Outpost2": "Outpost 2",
    "TKM": "TKM",
}

# Production-queue normalisation -> display bucket. Anything not mapped to a
# "real" bucket is treated as tech/upgrade-only (hidden by default).
REAL_QUEUE_RULES = [
    ("building", "Building"),
    ("defence", "Defense"),
    ("defense", "Defense"),
    ("infantry", "Infantry"),
    ("vehicle", "Vehicle"),
    ("armor", "Vehicle"),
    ("tank", "Vehicle"),
    ("aircraft", "Aircraft"),
    ("air", "Aircraft"),
    ("naval", "Ship"),
    ("ship", "Ship"),
]


def normalize_queue(queues):
    """Return (display_bucket, hidden) for a list of queue names."""
    for q in queues:
        ql = q.lower()
        for needle, bucket in REAL_QUEUE_RULES:
            if needle in ql:
                return bucket, False
    if not queues:
        return "", True
    # Upgrades / Research / Promotions / Addons / Disabled etc.
    return "Upgrade", True


_SEG_RE = re.compile(r"[^a-z0-9]+")


def dot_segments(*texts):
    segs = set()
    for t in texts:
        if not t:
            continue
        for piece in _SEG_RE.split(t.lower()):
            if piece:
                segs.add(piece)
    return segs


# ---------------------------------------------------------------------------
# Build the tech tree structure
# ---------------------------------------------------------------------------


def extract_actor(name, node):
    b = actor_buildable(node)
    if b is None:
        return None
    bucket, hidden = normalize_queue(b["queues"])
    icon = b["icon"] or actor_render_image(node) or name.lower()
    return {
        "id": name,
        "name": actor_name(node) or name,
        "queue": bucket,
        "rawQueues": b["queues"],
        "cost": actor_cost(node),
        "buildLimit": b["buildLimit"],
        "icon": icon,
        "hidden": hidden,
        # prereq tokens stripped of ~ / ! decoration, negations dropped
        "prereqs": [
            p.lstrip("~").strip()
            for p in b["prereqs"]
            if not p.lstrip("~").startswith("!")
        ],
        "provides": sorted(actor_provides(name, node)),
    }


# Explicit faction-root seed tokens for monolithic themes whose units gate on
# building prerequisites that carry no faction suffix (so propagation has a
# starting point). Tokens are lowercased prerequisite names.
SEED_TOKENS = {
    "RedAlert": {
        "allies": ["rafact.allies", "barr", "rafix.allies", "dome.allies"],
        "soviet": ["rafact.soviet", "tent", "rafix.soviet", "dome.soviet"],
        "japan": ["rafact.japan", "modtentj", "modtent", "rafix.japan", "dome.japan"],
    },
    "TiberianSun": {
        "tsgdi": ["fact.gdi", "fact.tsgdi"],
        "tsnod": ["fact.nod", "fact.tsnod"],
        "forgotten": ["fact.forgotten"],
    },
    "StarCraft": {
        "terran": ["sccommandcenter", "scbarracks", "scfactory", "scstarport"],
        "protoss": ["scnexus", "scgateway", "scstargate", "scrobofacility"],
        "zerg": ["schatchery", "sclair", "schive", "scspawningpool"],
    },
    "WarCraft2": {
        "human2": ["wc2townhall", "wc2barracks.human", "wc2keep", "wc2castle"],
        "orc2": ["wc2greathall", "wc2barracks.orc", "wc2stronghold", "wc2fortress"],
    },
    "Outpost2": {
        "plymouthl": ["op2commandcenter.plymouth", "op2.plymouth"],
        "edenl": ["op2commandcenter.eden", "op2.eden"],
    },
    "RedAlert2": {
        "ra2america": ["ra2conyard.america", "gapowr", "gapile"],
        "ra2russia": ["ra2conyard.russia", "napowr", "nahand"],
        "yuri": ["ra2conyard.yuri", "yapowr", "yabrck"],
    },
    "TKM": {"tkm": []},
}


def propagate_factions(theme, theme_ids, actors):
    """Assign monolithic-theme actors to factions by prerequisite reachability.

    Seeds = explicit faction-root tokens + actors whose NAME carries a faction
    suffix. A token propagates a faction only when every actor that provides it
    is already a member of that faction (prevents shared tokens from leaking
    faction across the roster). Returns {faction_id: set(actor_ids)}.
    """
    fac_defs = MONO_FACTIONS[theme]
    seeds = SEED_TOKENS.get(theme, {})

    # token -> set of provider actor ids (within this theme)
    token_providers = {}
    for aid in theme_ids:
        for tok in actors[aid]["provides"]:
            token_providers.setdefault(tok, set()).add(aid)

    members = {fid: set() for (fid, _d, _a) in fac_defs}

    # Direct seeds from actor-name faction suffix.
    for aid in theme_ids:
        name_segs = dot_segments(aid)
        for (fid, _disp, aliases) in fac_defs:
            if any(a in name_segs for a in aliases):
                members[fid].add(aid)

    prereqs = {aid: [p.lower() for p in actors[aid]["prereqs"]] for aid in theme_ids}

    changed = True
    while changed:
        changed = False
        for (fid, _disp, _a) in fac_defs:
            mem = members[fid]
            # Faction tokens this round: explicit seeds + tokens whose every
            # provider is already a faction member.
            ftokens = set(seeds.get(fid, ()))
            for tok, provs in token_providers.items():
                if provs <= mem:
                    ftokens.add(tok)
            for aid in theme_ids:
                if aid in mem:
                    continue
                if any(p in ftokens for p in prereqs[aid]):
                    mem.add(aid)
                    changed = True
    return members


def build(rs):
    # Extract all buildable actors.
    actors = {}
    for low, node in rs.actors():
        rec = extract_actor(node.key, node)
        if rec is not None:
            actors[node.key] = rec

    # Discover content-pack factions present (from folder attribution).
    content_factions = {t: [] for t in CONTENT_THEMES}
    for low, attrs in rs.attribution.items():
        for (theme, faction) in attrs:
            if theme in CONTENT_THEMES and faction and faction.lower() != "shared":
                if faction not in content_factions[theme]:
                    content_factions[theme].append(faction)
    for t in content_factions:
        content_factions[t].sort()

    # theme_id -> faction_id -> list of actor ids
    membership = {}

    def add_member(theme, faction, actor_id):
        membership.setdefault(theme, {}).setdefault(faction, [])
        if actor_id not in membership[theme][faction]:
            membership[theme][faction].append(actor_id)

    # --- Content-pack themes: folder attribution -------------------------
    for name, rec in actors.items():
        attrs = rs.attribution.get(name.lower(), ())
        for (theme, faction) in attrs:
            if theme not in CONTENT_THEMES:
                continue
            if faction and faction.lower() != "shared":
                add_member(theme, faction, name)
            else:
                for f in content_factions[theme]:
                    add_member(theme, f, name)

    # --- Monolithic themes: graph propagation ----------------------------
    # Themes whose faction separation is too weak to be meaningful are shown
    # as a single combined roster instead of N near-identical trees.
    mono_merged = {}
    for theme in MONO_FACTIONS:
        theme_ids = [
            n for n, rec in actors.items()
            if any(t == theme for (t, _f) in rs.attribution.get(n.lower(), ()))
        ]
        if not theme_ids:
            continue
        fac_ids = [f[0] for f in MONO_FACTIONS[theme]]
        assigned = propagate_factions(theme, theme_ids, actors)
        claimed = set().union(*assigned.values()) if assigned else set()
        # Separation ratio over VISIBLE actors (upgrades dominate and are shared).
        vis = [a for a in theme_ids if not actors[a]["hidden"]]
        vis_claimed = [a for a in vis if a in claimed]
        ratio = (len(vis_claimed) / len(vis)) if vis else 0
        single = len(fac_ids) == 1
        if single or ratio < 0.30:
            mono_merged[theme] = True
            for aid in theme_ids:
                add_member(theme, "all", aid)
        else:
            mono_merged[theme] = False
            for fid in fac_ids:
                for aid in assigned.get(fid, ()):
                    add_member(theme, fid, aid)
            for aid in theme_ids:  # unclaimed -> shared across all factions
                if aid not in claimed:
                    for fid in fac_ids:
                        add_member(theme, fid, aid)

    # Assemble output themes.
    themes_out = []
    theme_order = list(CONTENT_THEMES) + list(MONO_FACTIONS)
    for theme in theme_order:
        if theme not in membership:
            continue
        if theme in CONTENT_THEMES:
            theme_name = CONTENT_THEMES[theme]
            fac_defs = [(f, f) for f in content_factions[theme]]
        elif mono_merged.get(theme):
            theme_name = MONO_THEME_NAMES[theme]
            fac_defs = [("all", "All units")]
        else:
            theme_name = MONO_THEME_NAMES[theme]
            fac_defs = [(fid, disp) for (fid, disp, _a) in MONO_FACTIONS[theme]]

        factions_out = []
        for (fid, fdisp) in fac_defs:
            ids = membership[theme].get(fid)
            if not ids:
                continue
            nodes = [actors[i] for i in ids]
            # provider index within this faction
            token_providers = {}
            for n in nodes:
                for tok in n["provides"]:
                    token_providers.setdefault(tok, []).append(n["id"])
            id_set = set(ids)
            edges = []
            for n in nodes:
                for tok in n["prereqs"]:
                    tl = tok.lower()
                    for prov in token_providers.get(tl, ()):
                        if prov != n["id"] and prov in id_set:
                            edges.append({"from": prov, "to": n["id"], "token": tok})
            # strip internal field
            clean_nodes = [
                {k: v for k, v in n.items() if k != "rawQueues"} for n in nodes
            ]
            factions_out.append(
                {
                    "id": fid,
                    "name": fdisp,
                    "nodes": clean_nodes,
                    "edges": edges,
                }
            )
        if factions_out:
            themes_out.append({
                "id": theme,
                "name": theme_name,
                # Content packs split by folder (authoritative); monolithic
                # themes split by prerequisite-graph heuristic (approximate).
                "accurate": theme in CONTENT_THEMES,
                "factions": factions_out,
            })

    return {"themes": themes_out}


# ---------------------------------------------------------------------------
# Remote upstream fetch (default data source)
# ---------------------------------------------------------------------------

UPSTREAM_REPO = "https://github.com/cameo-mod/Cameo-mod.git"
UPSTREAM_REF = "master"


def _git(*args, cwd=None):
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def fetch_remote(repo, ref, cache_dir):
    """Shallow + sparse checkout of <repo>@<ref>, limited to mods/cameo.

    Re-uses the cache dir on subsequent runs (fetch + reset). Returns the path
    to mods/cameo and the resolved short commit hash.
    """
    git_dir = os.path.join(cache_dir, ".git")
    if not os.path.isdir(git_dir):
        os.makedirs(cache_dir, exist_ok=True)
        print(f"cloning {repo} @ {ref} (sparse: mods/cameo)…")
        _git("clone", "--depth", "1", "--filter=blob:none", "--sparse",
             "--branch", ref, repo, cache_dir)
        _git("sparse-checkout", "set", "mods/cameo", cwd=cache_dir)
    else:
        print(f"updating cached {repo} @ {ref}…")
        _git("fetch", "--depth", "1", "origin", ref, cwd=cache_dir)
        _git("reset", "--hard", "FETCH_HEAD", cwd=cache_dir)
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=cache_dir,
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return os.path.join(cache_dir, "mods", "cameo"), commit


# ---------------------------------------------------------------------------
# main (extraction logic added after convention review)
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(
        description="Generate techtree.json from the upstream Cameo-mod repo."
    )
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--repo", default=UPSTREAM_REPO,
                    help="upstream git URL (default: cameo-mod/Cameo-mod)")
    ap.add_argument("--ref", default=UPSTREAM_REF, help="branch/tag (default: master)")
    ap.add_argument("--mod", default=None,
                    help="use a LOCAL mods/cameo dir instead of fetching upstream")
    ap.add_argument("--cache", default=os.path.join(here, ".cache", "Cameo-mod"),
                    help="where to keep the sparse upstream clone")
    ap.add_argument(
        "--out", default=os.path.normpath(os.path.join(here, "..", "data", "techtree.json"))
    )
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    commit = None
    if args.mod:
        mod_dir = args.mod
        source = f"local:{mod_dir}"
    else:
        try:
            mod_dir, commit = fetch_remote(args.repo, args.ref, args.cache)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            sys.exit(f"upstream fetch failed ({e}). Pass --mod <path> to use a local checkout.")
        source = f"{args.repo}@{args.ref} ({commit})"

    if not os.path.isdir(mod_dir):
        sys.exit(f"mod dir not found: {mod_dir}")
    print(f"source: {source}")

    rs = RuleSet()
    files = collect_active_files(mod_dir)
    for path, theme, faction in files:
        with open(path, encoding="utf-8") as f:
            rs.add_file(f.read(), theme, faction)

    print(f"loaded {len(files)} rules files, {len(rs.raw)} actor/template nodes")

    if args.debug:
        world = rs.resolve("World")
        if world:
            facs = []
            for c in world.children:
                if c.key == "FactionCA" or c.key.startswith("FactionCA@") or c.key == "Faction" or c.key.startswith("Faction@"):
                    facs.append((
                        c.child_value("InternalName"),
                        c.child_value("Name"),
                        c.child_value("Side"),
                        c.child_value("Game"),
                        c.child_value("Selectable"),
                    ))
            print(f"\n== {len(facs)} faction defs (internal | name | side | game | selectable) ==")
            for f in sorted(facs, key=lambda x: (str(x[3]), str(x[0]))):
                print("  " + " | ".join(str(x) for x in f))

        queues = {}
        for low, node in rs.actors():
            b = actor_buildable(node)
            if b:
                for q in b["queues"]:
                    queues[q] = queues.get(q, 0) + 1
        print(f"\n== queues == {dict(sorted(queues.items(), key=lambda x:-x[1]))}")
        return

    tree = build(rs)
    today = datetime.date.today().isoformat()
    tree["generated"] = today + (f" · {args.ref} {commit}" if commit else "")
    tree["source"] = source

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, separators=(",", ":"))

    total_nodes = sum(len(fa["nodes"]) for th in tree["themes"] for fa in th["factions"])
    total_edges = sum(len(fa["edges"]) for th in tree["themes"] for fa in th["factions"])
    print(f"\nwrote {args.out}")
    print(f"themes: {len(tree['themes'])}  nodes: {total_nodes}  edges: {total_edges}")
    for th in tree["themes"]:
        facs = ", ".join(
            f"{fa['name']}:{sum(1 for n in fa['nodes'] if not n['hidden'])}"
            for fa in th["factions"]
        )
        print(f"  {th['name']:18} (visible) {facs}")


if __name__ == "__main__":
    main()
