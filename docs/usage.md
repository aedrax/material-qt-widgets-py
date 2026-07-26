# Getting started

material-qt is a Qt6 / PySide6 (QtWidgets) port of Material Design 3. This
page covers installing it, putting a first widget on screen, and the handful
of app-level conveniences worth knowing about before you reach for the
[component docs](./README.md#components).

## Install

Requirements: Python **≥ 3.11** and **PySide6 ≥ 6.7** (the only runtime
dependency). PyQt6 is not supported.

```bash
pip install -e .            # library only
pip install -e ".[dev]"     # + pytest, pytest-qt, ruff, black, mypy
```

Without an install, run against the source tree by prefixing
`PYTHONPATH=src`.

## A minimal app

```python
from PySide6.QtWidgets import QApplication

from material_qt import MdFilledButton, ThemeManager, ThemeMode

app = QApplication([])

theme = ThemeManager.instance()
theme.set_mode(ThemeMode.SYSTEM)   # follow the OS; or ThemeMode.LIGHT / DARK
theme.apply_app_palette()          # also theme native Qt widgets (optional)

button = MdFilledButton("Hello Material", icon="celebration")
button.clicked.connect(lambda: print("clicked"))
button.show()

app.exec()
```

Notes:

- `ThemeManager.instance()` can be created before the `QApplication`; any
  public call after the app exists (like `set_mode` above) hooks up OS
  dark-mode tracking automatically.
- `apply_app_palette()` maps a subset of Material color roles onto the
  application `QPalette`, so plain Qt widgets in the same window don't look
  alien. See [Theming](./theming.md).

## Imports

Every public component class is importable from the package root:

```python
from material_qt import MdCard, MdOutlinedTextField, MdSnackbar
```

Leaf imports remain equally supported (and are what the source tree itself
uses):

```python
from material_qt.widgets.textfield import MdOutlinedTextField
```

Design tokens and shared machinery stay namespaced — `material_qt.tokens`
(pure Python, no Qt) and `material_qt.core` (ripple, focus ring, elevation,
motion, modal overlay). See [Architecture](./architecture.md).

## Icons

Icons are plain **Material Symbols ligature names** passed as strings —
never `QIcon`:

```python
MdFilledButton("Save", icon="save")
MdIconButton("menu")
MdIcon("star")
field.set_leading_icon("search")
```

The glyph font resolves in three tiers: a Material Symbols family already
registered with Qt → a font file (the `MATERIAL_SYMBOLS_FONT` environment
variable first, then the bundled `MaterialSymbolsOutlined.ttf`, then common
system paths) → a text placeholder showing the icon name (never crashes).
Browse names at [fonts.google.com/icons](https://fonts.google.com/icons).
Details in the [Icon component doc](./components/icon.md).

## Material scrollbars

Qt's native scrollbars don't restyle themselves. After building a window,
one sweep converts every `QScrollArea`-like descendant to the Material
scrollbar (rounded thumb, hover thicken):

```python
from material_qt import install_material_scrollbars

install_material_scrollbars(window)   # idempotent, safe on hidden bars
```

For a single scroll area, `use_material_scrollbars(area)`. See
[Scrollbar](./components/scrollbar.md).

## Explore the catalogue

```bash
python -m material_qt.gallery              # all 56 pages, light/dark toggle,
                                           # palette presets, responsive nav
python -m material_qt.demo                 # foundation-only showcase
python -m material_qt.widgets.button.demo  # ~half the packages ship a
                                           # standalone demo module
```

The gallery source (`src/material_qt/gallery/gallery.py`) doubles as a
usage example for every component: each page is built by a small
`_build_<name>()` function.

## Running tests

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m pytest
```

`offscreen` lets the full widget suite run headless. Conventions for writing
new tests (visibility gotchas, disabling motion) are noted throughout the
component docs where relevant.
