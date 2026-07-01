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


def theme_faction_from_contentyaml(content_path):
    """Theme/faction for a ContentPacks/<Theme>[/<Faction>]/content.yaml path.

    A theme-level wrapper (ContentPacks/<Theme>/content.yaml) -> (Theme, None).
    A faction pack (ContentPacks/<Theme>/<Faction>/content.yaml) -> (Theme, Faction).
    """
    parts = os.path.normpath(content_path).split(os.sep)
    if "ContentPacks" not in parts:
        return None, None
    after = parts[parts.index("ContentPacks") + 1:]
    if not after:
        return None, None
    theme = after[0]
    faction = after[1] if len(after) >= 3 else None  # [Theme, Faction, content.yaml]
    return theme, faction


def collect_active_files(mod_dir):
    """Return list of (abs_path, theme, faction) for active rules files.

    Themes/factions are attributed from the including content.yaml's folder, so
    a wrapper pack that simply loads a monolithic ruleset still tags its theme.
    """
    files = []
    seen = set()

    def add(path, theme, faction):
        if path and path not in seen and os.path.isfile(path):
            seen.add(path)
            files.append((path, theme, faction))

    def resolve_include(value):
        if not value:
            return None
        v = value.strip()
        return resolve_pkg_path(v if "|" in v else "cameo|" + v, mod_dir)

    def process_content(content_path, _depth=0):
        theme, faction = theme_faction_from_contentyaml(content_path)
        with open(content_path, encoding="utf-8") as cf:
            for cn in parse_miniyaml(cf.read()):
                if cn.key == "Rules":
                    for rc in cn.children:
                        add(resolve_pkg_path(rc.key, mod_dir), theme, faction)
                elif cn.key == "Include" and _depth < 4:
                    nested = resolve_include(cn.value)
                    if nested and os.path.isfile(nested):
                        process_content(nested, _depth + 1)

    mod_yaml = os.path.join(mod_dir, "mod.yaml")
    with open(mod_yaml, encoding="utf-8") as f:
        roots = parse_miniyaml(f.read())
    for node in roots:
        if node.key == "Rules":  # base/shared rules (no theme)
            for c in node.children:
                add(resolve_pkg_path(c.key, mod_dir), None, None)
        elif node.key == "Include":
            inc = resolve_include(node.value)
            if inc and os.path.isfile(inc):
                process_content(inc)
    return files


def collect_section_files(mod_dir, section):
    """Return absolute paths of active files under a mod.yaml top section."""
    mod_yaml = os.path.join(mod_dir, "mod.yaml")
    with open(mod_yaml, encoding="utf-8") as f:
        roots = parse_miniyaml(f.read())
    out = []
    for node in roots:
        if node.key == section:
            for c in node.children:
                p = resolve_pkg_path(c.key, mod_dir)
                if p and os.path.isfile(p):
                    out.append(p)
    return out


def collect_section_files_recursive(mod_dir, section):
    """Like collect_section_files, but also follows content-pack Include:
    chains the same way collect_active_files does for Rules (a content-pack
    wrapper's own top-level <section>/Include children are merged in as if
    written directly in mod.yaml at that point)."""
    files = []
    seen = set()

    def add(path):
        if path and path not in seen and os.path.isfile(path):
            seen.add(path)
            files.append(path)

    def resolve_include(value):
        if not value:
            return None
        v = value.strip()
        return resolve_pkg_path(v if "|" in v else "cameo|" + v, mod_dir)

    def process_nodes(nodes, _depth=0):
        for node in nodes:
            if node.key == section:
                for c in node.children:
                    add(resolve_pkg_path(c.key, mod_dir))
            elif node.key == "Include" and _depth < 4:
                nested = resolve_include(node.value)
                if nested and os.path.isfile(nested):
                    with open(nested, encoding="utf-8") as nf:
                        process_nodes(parse_miniyaml(nf.read()), _depth + 1)

    mod_yaml = os.path.join(mod_dir, "mod.yaml")
    with open(mod_yaml, encoding="utf-8") as f:
        process_nodes(parse_miniyaml(f.read()))
    return files


def collect_weapon_files(mod_dir):
    """Return absolute paths of active weapon-definition files."""
    mod_yaml = os.path.join(mod_dir, "mod.yaml")
    with open(mod_yaml, encoding="utf-8") as f:
        roots = parse_miniyaml(f.read())
    out = []
    for node in roots:
        if node.key == "Weapons":
            for c in node.children:
                p = resolve_pkg_path(c.key, mod_dir)
                if p and os.path.isfile(p):
                    out.append(p)
    return out


_FLUENT_RE = re.compile(r"^([A-Za-z][\w-]*)\s*=\s*(.*)$")
_FLUENT_ATTR_RE = re.compile(r"^\s+\.([A-Za-z][\w-]*)\s*=\s*(.*)$")


def load_fluent(mod_dir):
    """Parse the mod's Fluent (.ftl) messages into {key: text}.

    Handles top-level `key = value` messages (used for actor Tooltip name
    keys) and `.attribute = value` messages (used for long-form Buildable
    Description text, e.g. `template-mbt.description`), including their
    indented multi-line continuations.
    """
    messages = {}
    for path in collect_section_files_recursive(mod_dir, "FluentMessages"):
        with open(path, encoding="utf-8") as f:
            last_key = None
            cur_key = None
            for raw in f:
                s = raw.rstrip("\n")
                if not s.strip():
                    last_key = cur_key = None
                    continue
                if s.lstrip().startswith("#"):
                    continue

                m_attr = _FLUENT_ATTR_RE.match(s) if last_key else None
                if m_attr:
                    cur_key = f"{last_key}.{m_attr.group(1)}"
                    if m_attr.group(2).strip():
                        messages[cur_key] = m_attr.group(2).strip()
                    continue

                m = _FLUENT_RE.match(s)
                if m:
                    last_key = cur_key = m.group(1)
                    if m.group(2).strip():
                        messages[last_key] = m.group(2).strip()
                    continue

                # Indented continuation of the previous key/attribute's value.
                if cur_key and s[:1].isspace():
                    extra = s.strip()
                    if extra:
                        messages[cur_key] = (messages.get(cur_key, "") + " " + extra).strip()
    return messages


def build_weapon_stats(mod_dir):
    """name(lower) -> {range, reload, damage} for all resolved weapons."""
    wrs = RuleSet()
    for path in collect_weapon_files(mod_dir):
        with open(path, encoding="utf-8") as f:
            wrs.add_file(f.read(), None, None)
    stats = {}
    for low in list(wrs.raw):
        if low.startswith("^"):
            continue
        w = wrs.resolve(low)
        if w is None:
            continue
        rng = w.child_value("Range")
        reload = w.child_value("ReloadDelay")
        dmg = None
        for c in w.children:
            if c.key == "Warhead" or c.key.startswith("Warhead@"):
                d = c.child_value("Damage")
                if d and d.lstrip("-").isdigit():
                    dmg = max(dmg or 0, int(d))
        stats[low] = {
            "range": rng,
            "reload": int(reload) if (reload and reload.isdigit()) else None,
            "damage": dmg,
        }
    return stats


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
    description = b.child_value("Description")
    return {
        "queues": queues,
        "prereqs": prereqs,
        "buildLimit": int(build_limit) if (build_limit and build_limit.lstrip("-").isdigit()) else None,
        "icon": icon,
        "description": description,
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


def _int_or_none(s):
    if s and s.lstrip("-").isdigit():
        return int(s)
    return None


def _wdist_to_tiles(raw):
    """Convert a raw WDist value (1024 units/cell; this mod always authors
    plain integers, never the 'Nc' cell notation) to tiles."""
    n = _int_or_none(raw)
    return round(n / 1024, 2) if n is not None else None


def classify_elite(cond):
    """True/False/None: whether an Armament's RequiresCondition gates it to
    the elite veterancy rank, the pre-elite rank, or neither."""
    if not cond:
        return None
    clauses = {c.strip().lower() for c in cond.split("&&")}
    if "!rank-elite" in clauses:
        return False
    if "rank-elite" in clauses:
        return True
    return None


def actor_stats(node, weapon_stats):
    """Combat/utility stats dict for tooltips (None fields omitted by caller)."""
    stats = {}
    h = node.child("Health")
    if h is not None:
        hp = _int_or_none(h.child_value("HP"))
        # Engine stores HP ×100; the in-game UI shows HP/100.
        stats["hp"] = round(hp / 100) if hp is not None else None
    a = node.child("Armor")
    if a is not None and a.child_value("Type"):
        stats["armor"] = a.child_value("Type")
    m = node.child("Mobile")
    if m is not None and m.child_value("Speed"):
        stats["speed"] = _int_or_none(m.child_value("Speed"))
    rev = node.child("RevealsShroud")
    if rev is not None and rev.child_value("Range"):
        stats["sight"] = _wdist_to_tiles(rev.child_value("Range"))
    pw = node.child("Power")
    if pw is None:
        pw = node.child("ScalePower")
    if pw is not None and pw.child_value("Amount"):
        stats["power"] = _int_or_none(pw.child_value("Amount"))

    # Armaments -> weapon names + best damage/range. Actors that can fire while
    # garrisoned/deployed etc. often declare a second Armament for the same
    # Weapon (different mount/muzzle, identical stats) - dedupe by weapon name
    # so those show once instead of as visual duplicates.
    weapons = []
    seen_weapons = set()
    for c in node.children:
        if c.key == "Armament" or c.key.startswith("Armament@"):
            wname = c.child_value("Weapon")
            if not wname or wname.lower() in seen_weapons:
                continue
            seen_weapons.add(wname.lower())
            ws = weapon_stats.get(wname.lower(), {})
            dmg = ws.get("damage")
            weapons.append({
                "name": wname,
                # Warhead Damage is stored ×100, same convention as Health.HP.
                "damage": round(dmg / 100) if dmg is not None else None,
                "range": _wdist_to_tiles(ws.get("range") or c.child_value("Range")),
                "elite": classify_elite(c.child_value("RequiresCondition")),
            })
    if weapons:
        stats["weapons"] = weapons
    return {k: v for k, v in stats.items() if v not in (None, "")}


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
    "Warcraft2": [
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
    "Warcraft2": "Warcraft 2",
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
    if any("promotion" in q.lower() for q in queues):
        return "Promotions", True
    # Upgrades / Research / Addons / Disabled etc.
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


def extract_actor(name, node, weapon_stats):
    b = actor_buildable(node)
    if b is None:
        return None
    bucket, hidden = normalize_queue(b["queues"])
    icon_seq = b["icon"] or "icon"
    seq_image = actor_render_image(node) or name.lower()
    return {
        "id": name,
        "name": actor_name(node) or name,
        "queue": bucket,
        "rawQueues": b["queues"],
        "cost": actor_cost(node),
        "buildLimit": b["buildLimit"],
        "description": b["description"],
        "iconSeq": icon_seq,
        "seqImage": seq_image,
        "hidden": hidden,
        "stats": actor_stats(node, weapon_stats),
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
    "Warcraft2": {
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


def icon_basename(actor_id):
    """Canonical PNG filename for an actor (matches the engine exporter)."""
    return re.sub(r"[^a-z0-9._-]+", "_", actor_id.lower()) + ".png"


def assign_existing_icons(tree, icons_dir):
    """Set node['png'] from PNGs already present in icons_dir (no copying).

    Used by --no-icons so a metadata-only regenerate keeps the committed icons
    referenced instead of silently dropping them from units.json."""
    kept = 0
    for th in tree["themes"]:
        for fa in th["factions"]:
            for n in fa["nodes"]:
                name = icon_basename(n["id"])
                if os.path.isfile(os.path.join(icons_dir, name)):
                    n["png"] = name
                    kept += 1
    return kept


def resolve_and_copy_icons(mod_dir, tree, icons_dir, cameo_dir=None):
    """Populate icons_dir with a cameo PNG per actor and set node['png'].

    Priority per actor: (1) an engine-exported cameo `<canonical>.png` in
    cameo_dir (full coverage incl. SHP cameos), else (2) a single on-disk PNG
    cameo resolved from the Sequences YAML. icons_dir is rebuilt each run so it
    never accumulates stale art. Returns (from_engine, from_png, total)."""
    import shutil

    seq_rs = RuleSet()
    for path in collect_section_files(mod_dir, "Sequences"):
        with open(path, encoding="utf-8") as f:
            seq_rs.add_file(f.read(), None, None)

    # Index every asset file by lowercased basename.
    file_index = {}
    for root, _dirs, files in os.walk(mod_dir):
        for fn in files:
            file_index.setdefault(fn.lower(), os.path.join(root, fn))

    def icon_filename(image, icon_seq):
        img = seq_rs.resolve(image)
        if img is None:
            return None, None
        seq = img.child(icon_seq)
        if seq is None:
            return None, None
        fname = seq.child_value("Filename")
        if not fname:
            defaults = img.child("Defaults")
            if defaults is not None:
                fname = defaults.child_value("Filename")
        return fname, seq.child_value("Start")

    # Rebuild icons_dir from scratch.
    if os.path.isdir(icons_dir):
        for fn in os.listdir(icons_dir):
            if fn.lower().endswith(".png"):
                os.remove(os.path.join(icons_dir, fn))
    os.makedirs(icons_dir, exist_ok=True)

    from_engine = from_png = total = 0
    png_seen = {}
    for th in tree["themes"]:
        for fa in th["factions"]:
            for n in fa["nodes"]:
                total += 1
                out_name = icon_basename(n["id"])
                dst = os.path.join(icons_dir, out_name)

                # (1) engine-exported cameo (covers SHP + sheet cameos).
                if cameo_dir:
                    eng = os.path.join(cameo_dir, out_name)
                    if os.path.isfile(eng):
                        if not os.path.exists(dst):
                            try:
                                shutil.copyfile(eng, dst)
                            except OSError:
                                pass
                        n["png"] = out_name
                        from_engine += 1
                        continue

                # (2) single-frame PNG cameo straight from the mod assets.
                fname, start = icon_filename(n.get("seqImage", ""), n.get("iconSeq", "icon"))
                if not fname:
                    continue
                fname = fname.strip()
                if not fname.lower().endswith(".png") or start not in (None, "0"):
                    continue
                key = fname.lower()
                if key not in png_seen:
                    src = file_index.get(key)
                    if not src:
                        continue
                    try:
                        shutil.copyfile(src, dst)
                        png_seen[key] = out_name
                    except OSError:
                        continue
                    n["png"] = out_name
                else:
                    n["png"] = png_seen[key]
                from_png += 1
    return from_engine, from_png, total


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


def build(rs, weapon_stats):
    # Extract all buildable actors.
    actors = {}
    for low, node in rs.actors():
        rec = extract_actor(node.key, node, weapon_stats)
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

    # --- Content-pack themes: folder attribution, faction-prereq override ---
    # Folder usually equals faction, but the mod occasionally files an actor in
    # the wrong faction folder (e.g. GDI's EYE lives under Nod/). The faction
    # prerequisite is authoritative, so if an actor's prereqs name a sibling
    # faction (its alias appears as a token segment), trust that over the folder.
    content_aliases = {
        t: {f: f.lower() for f in content_factions[t]} for t in CONTENT_THEMES
    }
    for name, rec in actors.items():
        attrs = rs.attribution.get(name.lower(), ())
        themes_here = {t for (t, _f) in attrs if t in CONTENT_THEMES}
        if not themes_here:
            continue
        segs = dot_segments(*rec["prereqs"])
        for theme in themes_here:
            prereq_factions = [
                f for f, alias in content_aliases[theme].items() if alias in segs
            ]
            if prereq_factions:
                for f in prereq_factions:
                    add_member(theme, f, name)
                continue
            folder_factions = [
                f for (t, f) in attrs
                if t == theme and f and f.lower() != "shared"
            ]
            for f in (folder_factions or content_factions[theme]):
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
    repo_root = os.path.normpath(os.path.join(here, "..", ".."))
    ap.add_argument(
        "--out", default=os.path.normpath(os.path.join(here, "..", "data", "techtree.json"))
    )
    ap.add_argument(
        "--units-out",
        default=os.path.join(repo_root, "cameo-units", "data", "units.json"),
        help="also write the richer units dataset (with icons) here",
    )
    ap.add_argument(
        "--icons-out",
        default=os.path.join(repo_root, "cameo-units", "icons"),
        help="copy resolved PNG cameos here",
    )
    ap.add_argument(
        "--cameo-dir",
        default=os.path.join(here, ".cache", "cameos"),
        help="engine-exported cameo PNGs (from OpenRA.Utility --export-cameos); "
             "full-coverage source, preferred over on-disk PNG cameos",
    )
    ap.add_argument("--no-icons", action="store_true", help="skip icon resolution/copy")
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

    weapon_stats = build_weapon_stats(mod_dir)
    print(f"loaded weapon stats: {len(weapon_stats)}")
    tree = build(rs, weapon_stats)
    today = datetime.date.today().isoformat()
    tree["generated"] = today + (f" · {args.ref} {commit}" if commit else "")
    tree["source"] = source

    # Resolve Fluent name keys to display text, and build a prerequisite-token ->
    # display-name map (token resolves to a provider actor's translated name;
    # untranslatable tokens such as conditions stay as-is in the viewer).
    fluent = load_fluent(mod_dir)
    prereq_names = {}
    for th in tree["themes"]:
        for fa in th["factions"]:
            for n in fa["nodes"]:
                n["name"] = fluent.get(n["name"], n["name"])
                if n.get("description"):
                    n["description"] = fluent.get(n["description"], n["description"])
                for tok in n.get("provides", ()):
                    prereq_names.setdefault(tok.lower(), n["name"])
                prereq_names.setdefault(n["id"].lower(), n["name"])
    tree["prereqNames"] = prereq_names

    if not args.no_icons:
        cameo_dir = args.cameo_dir if os.path.isdir(args.cameo_dir) else None
        eng, png, total = resolve_and_copy_icons(mod_dir, tree, args.icons_out, cameo_dir)
        src = "engine+png" if cameo_dir else "png-only"
        print(f"icons ({src}): {eng} engine + {png} png = {eng + png}/{total} -> {args.icons_out}")
    else:
        # Don't recopy, but keep png references consistent with what's already
        # committed in icons_out (otherwise units.json would drop all icons).
        kept = assign_existing_icons(tree, args.icons_out)
        print(f"icons (no-copy): kept {kept} existing references in {args.icons_out}")

    # Graph dataset (techtree): drop the heavier per-node fields it doesn't use.
    graph = json.loads(json.dumps(tree))
    graph.pop("prereqNames", None)
    for th in graph["themes"]:
        for fa in th["factions"]:
            for n in fa["nodes"]:
                for k in ("stats", "iconSeq", "seqImage", "png", "description"):
                    n.pop(k, None)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, separators=(",", ":"))

    # Units dataset (grid view): keep stats + icon paths.
    if args.units_out:
        for th in tree["themes"]:
            for fa in th["factions"]:
                for n in fa["nodes"]:
                    n.pop("seqImage", None)
                    n.pop("iconSeq", None)
        os.makedirs(os.path.dirname(args.units_out), exist_ok=True)
        with open(args.units_out, "w", encoding="utf-8") as f:
            json.dump(tree, f, ensure_ascii=False, separators=(",", ":"))
        print(f"wrote {args.units_out}")

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
