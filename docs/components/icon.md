# Icon

Material Symbols icon rendering.

**Classes:** `MdIcon`, `IconStyle`, `DEFAULT_ICON_SIZE` · **Source:** `src/material_qt/widgets/icon/`
**Spec:** <https://m3.material.io/styles/icons>. Ports Material Web's `md-icon`: a Material Symbols glyph rendered by ligature name at a default size of 24px, weight 400, colored `on-surface` by default (the web `currentColor` default), with the `FILL` axis toggling outlined vs filled.

## Usage

```python
from material_qt import MdIcon, IconStyle

icon = MdIcon("favorite", parent=page)               # 24px outlined heart
big = MdIcon("settings", size=40, filled=True)        # 40px filled gear
```

Icons are Material Symbols ligature-name strings (e.g. `"favorite"`, `"check_box"`), never a `QIcon`.

Run the demo: `python -m material_qt.widgets.icon.demo`.

## API

### MdIcon

Extends `QWidget`. Fixed size policy in both directions; `sizeHint()` is `size x size`.

```python
MdIcon(
    name: str = "",
    parent: QWidget | None = None,
    *,
    size: int = DEFAULT_ICON_SIZE,
    filled: bool = False,
    style: IconStyle = IconStyle.OUTLINED,
    color_role: ColorRole = ColorRole.ON_SURFACE,
)
```

- `name` — property; the ligature name (or any text to render). `set_name(name)` updates it and the accessible name.
- `icon_size` — property; the icon box size in logical pixels. `set_size(size)` changes it (clamped to at least 1).
- `filled` — property; whether the FILL 1 variant is used. `set_filled(filled)` toggles it. Only visibly changes the glyph when the loaded font supports the `FILL` variation axis.
- `color_role` — property; theme color role for the glyph. `set_color_role(role)` changes it.
- `font_available` — property (bool); whether a Material Symbols/Icons font was found for rendering.
- `font_family` — property; the resolved family name, or `None` if unavailable.
- `register_font(path)` — classmethod; register a Material Symbols font file with Qt at runtime. Returns the registered family name, or `None` on failure. Useful for applications that ship their own copy of the font.

No signals.

### IconStyle

Material Symbols visual style; each value maps to a font family name preferred when available:

- `OUTLINED` = `"Material Symbols Outlined"`
- `ROUNDED` = `"Material Symbols Rounded"`
- `SHARP` = `"Material Symbols Sharp"`

### Module constants and functions

These live in `material_qt.widgets.icon.icon` (`DEFAULT_ICON_SIZE` and `IconStyle` are also re-exported from `material_qt`; the two functions are not).

- `DEFAULT_ICON_SIZE = 24` — default icon size in logical pixels (`md-icon`: `--md-icon-size: 24px`).
- `material_symbols_family(style: IconStyle = None) -> str | None` — resolve a usable Material Symbols family, loading the bundled font if needed. Shared by other components (buttons, FABs) that render glyphs inline. Returns the family name, or `None` if no Material Symbols font can be found.
- `material_symbols_font(size: int, *, filled: bool = False) -> QFont | None` — build a Material Symbols `QFont` at `size` px (weight 400, `FILL`/`opsz` axes set when supported), or `None` if no family resolves.

## Notes

- Font resolution happens once per `MdIcon` instance, in tiers:
  1. A Material family already registered with Qt wins (the constructor's `style` family is preferred; otherwise the first registered of `Material Symbols Outlined`, `Material Symbols Rounded`, `Material Symbols Sharp`, `Material Icons Outlined`, `Material Icons`).
  2. Otherwise a font file is loaded via `QFontDatabase.addApplicationFont`, trying in order: the `MATERIAL_SYMBOLS_FONT` environment variable (if set), the bundled `src/material_qt/assets/MaterialSymbolsOutlined.ttf`, then common system paths (`/usr/share/fonts/...`, `~/.fonts/`, `~/.local/share/fonts/`).
  3. If nothing loads, the widget falls back to drawing the icon *name* as small elided text inside a placeholder box outline — it never crashes or renders blank. `font_available` reports which case applies.
- Because the Material Symbols Outlined variable font is bundled, glyphs render out of the box without any system font installed.
- Variable-font axes are set via `QFont.setVariableAxis` (Qt 6.7+), guarded so older Qt still works: `FILL` (0 outlined / 1 filled), `wght` 400, and `opsz` tracking the pixel size. On older Qt, `filled=True` has no visible effect.
- The glyph color comes from `ThemeManager` for the given `color_role` and repaints on `themeChanged`.
- The icon is decorative by default (the web component sets `aria-hidden="true"`); the ligature name is exposed as the widget's accessible name for screen readers.
- This page is the definitive reference for font resolution; see [usage](../usage.md) for how other components accept icon names and [theming](../theming.md) for color roles.
