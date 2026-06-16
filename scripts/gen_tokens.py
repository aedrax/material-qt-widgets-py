#!/usr/bin/env python3
"""Generate material_qt token modules from the Material SCSS source of truth.

Parses the ``@function values()`` maps in ``tokens/versions/v0_192/*.scss`` and
writes pure-Python dicts/tuples into ``src/material_qt/tokens/_generated/``.

The elevation key/ambient shadow tuples do not live in a flat SCSS map (they are
computed by clamp() expressions in ``elevation/internal/_elevation.scss``); those
are hand-transcribed below from the documented per-level values, with a comment.

Usage::

    python scripts/gen_tokens.py [--repo-root PATH] [--check]

The generated files are committed; run this when bumping the token version.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION = "v0_192"
HEADER = f"# GENERATED FROM tokens/versions/{VERSION} — DO NOT EDIT\n"

# ---------------------------------------------------------------------------
# SCSS parsing helpers
# ---------------------------------------------------------------------------

_PAIR_RE = re.compile(r"'(?P<key>[^']+)'\s*:\s*(?P<val>.+?)(?:,\s*)?$")


def _strip_if(value: str) -> str:
    """Pull the concrete value out of an ``if($exclude-hardcoded-values, null, X)``."""
    value = value.strip()
    m = re.match(r"if\(\s*\$exclude-hardcoded-values\s*,\s*null\s*,\s*(.*)\)$", value)
    if m:
        return m.group(1).strip()
    return value


def parse_flat_map(scss_text: str, func_name: str = "values") -> dict[str, str]:
    """Parse a single ``@function <func_name>(...) { @return ( ... ); }`` map.

    Returns raw string values (with the surrounding ``if(...)`` already stripped).
    Multi-line entries are joined first.
    """
    # Isolate the @return ( ... ) body for the named function.
    fn_re = re.compile(
        r"@function\s+" + re.escape(func_name) + r"\b[^{]*\{\s*@return\s*\((?P<body>.*?)\)\s*;\s*\}",
        re.DOTALL,
    )
    m = fn_re.search(scss_text)
    if not m:
        raise ValueError(f"function {func_name!r} not found")
    body = m.group("body")

    # Join continuation lines: split on top-level commas is hard due to nested
    # parens, so collapse whitespace then split on "',' followed by a quote key".
    flat = re.sub(r"\s+", " ", body).strip()
    # Split into "'key': value" chunks. Keys are always quoted at depth 0.
    entries: dict[str, str] = {}
    # Use a paren-depth-aware splitter.
    parts: list[str] = []
    depth = 0
    cur = ""
    for ch in flat:
        if ch == "(":
            depth += 1
            cur += ch
        elif ch == ")":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        mm = re.match(r"'(?P<key>[^']+)'\s*:\s*(?P<val>.*)$", part, re.DOTALL)
        if not mm:
            continue
        entries[mm.group("key")] = _strip_if(mm.group("val"))
    return entries


def parse_map_get_map(scss_text: str, func_name: str) -> dict[str, str]:
    """Parse a map whose values are ``map.get($deps, 'md-ref-palette', 'toneKey')``.

    Returns role -> tone-key.
    """
    fn_re = re.compile(
        r"@function\s+" + re.escape(func_name) + r"\b[^{]*\{\s*@return\s*\((?P<body>.*?)\)\s*;\s*\}",
        re.DOTALL,
    )
    m = fn_re.search(scss_text)
    if not m:
        raise ValueError(f"function {func_name!r} not found")
    body = re.sub(r"\s+", " ", m.group("body"))
    out: dict[str, str] = {}
    for mm in re.finditer(
        r"'(?P<role>[^']+)'\s*:\s*map\.get\([^,]+,\s*'[^']+'\s*,\s*'(?P<tone>[^']+)'\)",
        body,
    ):
        out[mm.group("role")] = mm.group("tone")
    return out


# ---------------------------------------------------------------------------
# Value normalizers
# ---------------------------------------------------------------------------


def hex_norm(value: str) -> str:
    """Normalize a CSS hex color to lowercase 6-digit ``#rrggbb``."""
    v = value.strip().lower()
    if not v.startswith("#"):
        return v
    h = v[1:]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def px_to_float(value: str) -> float:
    return float(value.strip().removesuffix("px"))


def rem_to_float(value: str) -> float:
    return float(value.strip().removesuffix("rem"))


def ms_to_int(value: str) -> int:
    return int(float(value.strip().removesuffix("ms")))


def cubic_bezier(value: str) -> tuple[tuple[float, float], tuple[float, float]]:
    m = re.match(r"cubic-bezier\((.*)\)$", value.strip())
    if not m:
        raise ValueError(f"not a cubic-bezier: {value!r}")
    nums = [float(x) for x in m.group(1).split(",")]
    return ((nums[0], nums[1]), (nums[2], nums[3]))


# ---------------------------------------------------------------------------
# Hand-transcribed elevation shadows (from elevation/internal/_elevation.scss)
# Key shadow opacity 0.3, ambient shadow opacity 0.15.
# Tuples are (dx, dy, blur, spread) in px, taken from the documented per-level
# box-shadow comments in _elevation.scss.
# ---------------------------------------------------------------------------

# Key (umbra) box-shadow per level: 0px <y> <blur> 0px  (spread always 0)
_KEY_SHADOWS = {
    0: (0, 0, 0, 0),
    1: (0, 1, 2, 0),
    2: (0, 1, 2, 0),
    3: (0, 1, 3, 0),
    4: (0, 2, 3, 0),
    5: (0, 4, 4, 0),
}
# Ambient (penumbra) box-shadow per level: 0px <y> <blur> <spread>
_AMBIENT_SHADOWS = {
    0: (0, 0, 0, 0),
    1: (0, 1, 3, 1),
    2: (0, 2, 6, 2),
    3: (0, 4, 8, 3),
    4: (0, 6, 10, 4),
    5: (0, 8, 12, 6),
}
_KEY_OPACITY = 0.3
_AMBIENT_OPACITY = 0.15


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def _write(path: Path, body: str, check: bool, changes: list[str]) -> None:
    content = HEADER + body
    if check:
        existing = path.read_text() if path.exists() else ""
        if existing != content:
            changes.append(str(path))
        return
    path.write_text(content)


def gen_palette(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-ref-palette.scss").read_text()
    raw = parse_flat_map(text)
    palette = {k: hex_norm(v) for k, v in sorted(raw.items())}
    lines = ['"""Reference tonal palette: tone-key -> hex."""', "", "REF_PALETTE: dict[str, str] = {"]
    for k, v in palette.items():
        lines.append(f"    {k!r}: {v!r},")
    lines.append("}")
    _write(out / "palette.py", "\n".join(lines) + "\n", check, changes)


def gen_color_roles(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-sys-color.scss").read_text()
    light = parse_map_get_map(text, "values-light")
    dark = parse_map_get_map(text, "values-dark")
    lines = ['"""System color roles: role -> palette tone-key, per light/dark scheme."""', ""]
    lines.append("LIGHT_ROLES: dict[str, str] = {")
    for k in sorted(light):
        lines.append(f"    {k!r}: {light[k]!r},")
    lines.append("}")
    lines.append("")
    lines.append("DARK_ROLES: dict[str, str] = {")
    for k in sorted(dark):
        lines.append(f"    {k!r}: {dark[k]!r},")
    lines.append("}")
    _write(out / "color_roles.py", "\n".join(lines) + "\n", check, changes)


_TYPESCALE_ROLES = [
    "display-large", "display-medium", "display-small",
    "headline-large", "headline-medium", "headline-small",
    "title-large", "title-medium", "title-small",
    "body-large", "body-medium", "body-small",
    "label-large", "label-medium", "label-small",
]


def gen_typescale(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-sys-typescale.scss").read_text()
    raw = parse_flat_map(text)
    tf_text = (repo / "tokens" / "versions" / VERSION / "_md-ref-typeface.scss").read_text()
    tf = parse_flat_map(tf_text)
    weight_map = {
        "weight-regular": int(tf["weight-regular"]),
        "weight-medium": int(tf["weight-medium"]),
        "weight-bold": int(tf["weight-bold"]),
    }
    # font tokens reference 'brand'/'plain' typeface keys -> resolve to family name
    family_map = {"brand": tf["brand"], "plain": tf["plain"]}

    def weight_val(role: str) -> int:
        token = raw[f"{role}-weight"]  # e.g. "weight-regular" passed through map.get
        # weight values are map.get(...,'weight-regular'); _strip_if leaves the
        # map.get expr, so extract the trailing key.
        m = re.search(r"weight-\w+", token)
        return weight_map[m.group(0)] if m else int(token)

    def family_val(role: str) -> str:
        token = raw[f"{role}-font"]
        m = re.search(r"'(brand|plain)'", token)
        return family_map[m.group(1)] if m else token

    lines = [
        '"""Typescale specs: role -> family, size_rem, line_height_rem, weight, tracking_rem."""',
        "",
        "TYPESCALE: dict[str, dict] = {",
    ]
    for role in _TYPESCALE_ROLES:
        spec = {
            "family": family_val(role),
            "size_rem": rem_to_float(raw[f"{role}-size"]),
            "line_height_rem": rem_to_float(raw[f"{role}-line-height"]),
            "weight": weight_val(role),
            "tracking_rem": rem_to_float(raw[f"{role}-tracking"]),
        }
        lines.append(f"    {role!r}: {spec!r},")
    lines.append("}")
    _write(out / "typescale.py", "\n".join(lines) + "\n", check, changes)


def gen_shape(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-sys-shape.scss").read_text()
    raw = parse_flat_map(text)
    scalar = {
        "none": px_to_float(raw["corner-none"]),
        "extra-small": px_to_float(raw["corner-extra-small"]),
        "small": px_to_float(raw["corner-small"]),
        "medium": px_to_float(raw["corner-medium"]),
        "large": px_to_float(raw["corner-large"]),
        "extra-large": px_to_float(raw["corner-extra-large"]),
        "full": px_to_float(raw["corner-full"]),
    }

    def shorthand(key: str) -> tuple[float, float, float, float]:
        # e.g. "(28px 28px 0px 0px)" -> (28,28,0,0) clockwise tl,tr,br,bl
        vals = re.findall(r"([\d.]+)px", raw[key])
        return tuple(float(v) for v in vals)  # type: ignore[return-value]

    per_corner = {
        "extra-large-top": shorthand("corner-extra-large-top"),
        "extra-small-top": shorthand("corner-extra-small-top"),
        "large-top": shorthand("corner-large-top"),
        "large-start": shorthand("corner-large-start"),
        "large-end": shorthand("corner-large-end"),
    }
    lines = ['"""Shape corner radii (px). CORNER scalars + per-corner shorthands."""', ""]
    lines.append("CORNER: dict[str, float] = {")
    for k, v in scalar.items():
        lines.append(f"    {k!r}: {v!r},")
    lines.append("}")
    lines.append("")
    lines.append("# Per-corner shorthands as (tl, tr, br, bl) tuples in px.")
    lines.append("PER_CORNER: dict[str, tuple] = {")
    for k, v in per_corner.items():
        lines.append(f"    {k!r}: {v!r},")
    lines.append("}")
    _write(out / "shape.py", "\n".join(lines) + "\n", check, changes)


def gen_elevation(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-sys-elevation.scss").read_text()
    raw = parse_flat_map(text)
    level_dp = {int(k.removeprefix("level")): int(v) for k, v in raw.items()}
    lines = [
        '"""Elevation: level -> dp, plus dual key/ambient shadow tuples.',
        "",
        "Shadow tuples are (dx, dy, blur, spread) in px. Key (umbra) shadows use",
        "opacity 0.3; ambient (penumbra) shadows use opacity 0.15. These are",
        "hand-transcribed from elevation/internal/_elevation.scss (computed there",
        'via clamp() rather than a flat map).',
        '"""',
        "",
        "LEVEL_DP: dict[int, int] = {",
    ]
    for k in sorted(level_dp):
        lines.append(f"    {k}: {level_dp[k]},")
    lines.append("}")
    lines.append("")
    lines.append(f"KEY_SHADOW_OPACITY = {_KEY_OPACITY!r}")
    lines.append(f"AMBIENT_SHADOW_OPACITY = {_AMBIENT_OPACITY!r}")
    lines.append("")
    lines.append("# (dx, dy, blur, spread) px")
    lines.append("KEY_SHADOWS: dict[int, tuple] = {")
    for k in sorted(_KEY_SHADOWS):
        lines.append(f"    {k}: {_KEY_SHADOWS[k]!r},")
    lines.append("}")
    lines.append("")
    lines.append("AMBIENT_SHADOWS: dict[int, tuple] = {")
    for k in sorted(_AMBIENT_SHADOWS):
        lines.append(f"    {k}: {_AMBIENT_SHADOWS[k]!r},")
    lines.append("}")
    _write(out / "elevation.py", "\n".join(lines) + "\n", check, changes)


def gen_motion(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-sys-motion.scss").read_text()
    raw = parse_flat_map(text)
    durations = {}
    easings = {}
    for k, v in raw.items():
        if k.startswith("duration-"):
            durations[k.removeprefix("duration-")] = ms_to_int(v)
        elif k.startswith("easing-") and v.strip().startswith("cubic-bezier"):
            easings[k.removeprefix("easing-")] = cubic_bezier(v)
    lines = [
        '"""Motion durations (ms) and easing control points ((x1,y1),(x2,y2))."""',
        "",
        "DURATIONS_MS: dict[str, int] = {",
    ]
    for k in sorted(durations):
        lines.append(f"    {k!r}: {durations[k]},")
    lines.append("}")
    lines.append("")
    lines.append("EASINGS: dict[str, tuple] = {")
    for k in sorted(easings):
        lines.append(f"    {k!r}: {easings[k]!r},")
    lines.append("}")
    _write(out / "motion.py", "\n".join(lines) + "\n", check, changes)


def gen_state(repo: Path, out: Path, check: bool, changes: list[str]) -> None:
    text = (repo / "tokens" / "versions" / VERSION / "_md-sys-state.scss").read_text()
    raw = parse_flat_map(text)
    state = {
        k.removesuffix("-state-layer-opacity"): float(v)
        for k, v in raw.items()
        if k.endswith("-state-layer-opacity")
    }
    lines = ['"""State layer opacities: state -> opacity."""', "", "STATE_OPACITY: dict[str, float] = {"]
    for k in sorted(state):
        lines.append(f"    {k!r}: {state[k]!r},")
    lines.append("}")
    _write(out / "state.py", "\n".join(lines) + "\n", check, changes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("/data/projects/material-web"),
        help="Path to the material-web source repo (contains tokens/).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit non-zero if generated output is stale.",
    )
    args = parser.parse_args(argv)

    repo = args.repo_root
    out = Path(__file__).resolve().parent.parent / "src" / "material_qt" / "tokens" / "_generated"
    out.mkdir(parents=True, exist_ok=True)

    changes: list[str] = []
    gen_palette(repo, out, args.check, changes)
    gen_color_roles(repo, out, args.check, changes)
    gen_typescale(repo, out, args.check, changes)
    gen_shape(repo, out, args.check, changes)
    gen_elevation(repo, out, args.check, changes)
    gen_motion(repo, out, args.check, changes)
    gen_state(repo, out, args.check, changes)

    if args.check:
        if changes:
            print("Stale generated token files:", *changes, sep="\n  ")
            return 1
        print("Generated token files are up to date.")
        return 0
    print(f"Wrote generated token files to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
