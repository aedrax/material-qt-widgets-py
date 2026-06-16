# material-qt

A Qt6 / PySide6 (QtWidgets) port of Google's
[Material Design 3](https://m3.material.io/) tokens and shared component
foundation, derived from the
[Material Web Components](https://github.com/material-components/material-web).

This package is **Wave 1: the foundation layer only** — design tokens, theming,
and the shared interaction/painting machinery (motion, shape, typography,
elevation, ripple, focus ring, responsive helpers, and a `MaterialWidget` base).
No concrete components (button, checkbox, etc.) are included yet; those land in
`material_qt.widgets` in a later wave.

## Layout

- `material_qt.tokens` — pure-Python design tokens (zero Qt imports, headless
  testable). Values under `tokens/_generated/` are transcribed from
  `tokens/versions/v0_192/*.scss` by `scripts/gen_tokens.py` and committed.
- `material_qt.theme` — `ColorScheme` (immutable role→QColor maps) and the
  `ThemeManager` singleton (light/dark/system, `themeChanged` signal).
- `material_qt.core` — motion, shape, typography, interaction state, state
  layer, elevation, ripple, focus ring, responsive helpers, and the
  `MaterialWidget` base.
- `material_qt.demo` — a minimal demo window.

## Install (development)

From this `qt/` directory:

```bash
pip install -e ".[dev]"
```

## Run the demo

```bash
python -m material_qt.demo
```

## Run the tests

```bash
python -m pytest
```

For headless environments set `QT_QPA_PLATFORM=offscreen`.

## Regenerate tokens

```bash
python scripts/gen_tokens.py
```

This re-parses `tokens/versions/v0_192/*.scss` from the source repo and rewrites
`src/material_qt/tokens/_generated/*.py`. The generated files are committed.
