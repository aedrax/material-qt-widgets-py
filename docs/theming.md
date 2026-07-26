# Theming

All color in material-qt flows through one object: the `ThemeManager`
singleton. Widgets never store colors — they look roles up at paint time and
repaint when the theme changes, so mode switches, brand palettes, and
per-role overrides all apply live to a running app.

```python
from material_qt import ThemeManager, ThemeMode

theme = ThemeManager.instance()
```

## Why not QPalette?

`QPalette` models a handful of color roles; Material 3 defines ~50 (48
`ColorRole`s in this port). The theme is therefore carried out-of-band by
the singleton plus its `themeChanged` signal. Every Material widget connects
`themeChanged → update()` when constructed (wired by
`MaterialWidgetMixin._init_material`, see [Architecture](./architecture.md)).
A sensible subset *is* still mapped onto the application `QPalette` — see
[`apply_app_palette`](#theming-native-qt-widgets) below — so native Qt
widgets follow along.

## Modes: light, dark, system

```python
theme.set_mode(ThemeMode.SYSTEM)   # default: follow the OS
theme.set_mode(ThemeMode.DARK)
theme.toggle_light_dark()          # convenience: flips LIGHT <-> DARK
theme.mode                         # ThemeMode
theme.is_dark                      # bool, the *resolved* darkness
```

In `SYSTEM` mode the manager tracks the OS via
`QStyleHints.colorScheme()` / `colorSchemeChanged` (Qt 6.5+), with a
window-lightness fallback on older Qt. The manager may be constructed before
the `QApplication` exists; every public entry point retries the hint hookup,
so no special ordering is required.

## Color roles and schemes

`ColorRole` (`material_qt.tokens`) is a `StrEnum` of the 48 Material roles,
kebab-case valued: `ColorRole.ON_SURFACE_VARIANT == "on-surface-variant"`.
`ColorScheme` (importable from the package root) is an immutable
`ColorRole → QColor` map built from the baseline Material tokens; there is
exactly one light and one dark instance (cached).

The universal read path — and the one that honors overrides — is:

```python
from material_qt.tokens import ColorRole

qcolor = theme.color(ColorRole.PRIMARY)   # also accepts the string "primary"
```

Custom-painted widgets should call `theme.color(...)` inside `paintEvent`
rather than caching colors, which is what makes live theme switching free.

## Runtime overrides (branding)

Overrides sit on top of the resolved scheme and are kept **per mode**, so a
brand color can differ between light and dark:

```python
# Both modes:
theme.set_overrides({"primary": "#006A6A", "on-primary": "#FFFFFF"})

# Dark only:
theme.set_overrides({"primary": "#4DDADA"}, mode=ThemeMode.DARK)

theme.overrides(dark=True)   # inspect (a copy)
theme.clear_overrides()      # both modes; or mode=ThemeMode.LIGHT / DARK
```

Values accept a `QColor` or any string `QColor` understands. Every call
repaints all widgets and rebuilds the app palette.

## Full palettes and presets

`set_palette(light, dark)` **replaces** all overrides with two role maps
(`None` = baseline tokens for that mode). Named presets live in
`material_qt.theme.presets`:

```python
from material_qt.theme.presets import PRESETS

theme.set_palette(*PRESETS["Catalog"])    # material-web.dev's amber scheme
theme.set_palette(*PRESETS["Baseline"])   # back to stock (None, None)
```

## Theming native Qt widgets

```python
theme.apply_app_palette()   # or apply_app_palette(app)
```

Maps surface → `Window`, on-surface → `WindowText`/`Text`/`ButtonText`,
surface-container-lowest → `Base`, surface-container → `Button`,
primary → `Highlight`, on-primary → `HighlightedText`. Called automatically
on every theme change once an application exists — invoke it once at
startup and forget it.

## Reacting to theme changes yourself

```python
theme.themeChanged.connect(self.update)
```

`themeChanged` fires on mode changes, OS scheme changes (in `SYSTEM` mode),
and every override/palette mutation. Material widgets already subscribe;
connect your own custom-painted widgets the same way.

## Testing note

The test suite's `tests/conftest.py` has an autouse fixture that resets
`ThemeManager._instance = None` after every test — theme state set in one
test never leaks into the next. If you write tests that mutate the theme
(modes, overrides), rely on that reset rather than undoing changes manually.
