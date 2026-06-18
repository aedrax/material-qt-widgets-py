"""Built-in color theme presets (full role maps), applied via ThemeManager.

A preset is a name plus light/dark dicts of color-role -> hex. ``Baseline`` is
the default token scheme (no overrides). ``Catalog`` reproduces the
material-web.dev catalog's default theme — an M3 dynamic-color scheme generated
from the amber seed ``#ecaa2e`` — captured from the live site's
``--md-sys-color-*`` values for light and dark.
"""

from __future__ import annotations

# material-web.dev catalog — light scheme (seed #ecaa2e).
CATALOG_LIGHT: dict[str, str] = {
    "primary": "#7f5700", "on-primary": "#ffffff",
    "primary-container": "#f7b337", "on-primary-container": "#442d00",
    "secondary": "#765a2b", "on-secondary": "#ffffff",
    "secondary-container": "#ffdca9", "on-secondary-container": "#5c4316",
    "tertiary": "#566500", "on-tertiary": "#ffffff",
    "tertiary-container": "#b6ca54", "on-tertiary-container": "#2d3600",
    "error": "#ba1a1a", "on-error": "#ffffff",
    "error-container": "#ffdad6", "on-error-container": "#410002",
    "background": "#fff8f3", "on-background": "#201b12",
    "surface": "#fff8f3", "on-surface": "#201b12",
    "surface-variant": "#f2e0c9", "on-surface-variant": "#504534",
    "outline": "#837562", "outline-variant": "#d5c4ae",
    "surface-container-lowest": "#ffffff", "surface-container-low": "#fef2e4",
    "surface-container": "#f8ecde", "surface-container-high": "#f3e6d8",
    "surface-container-highest": "#ede1d3",
    "surface-dim": "#e4d8cb", "surface-bright": "#fff8f3",
    "inverse-surface": "#362f26", "inverse-on-surface": "#fbefe1",
    "inverse-primary": "#ffba3e", "shadow": "#000000", "scrim": "#000000",
    "surface-tint": "#7f5700",
}

# material-web.dev catalog — dark scheme (seed #ecaa2e).
CATALOG_DARK: dict[str, str] = {
    "primary": "#ffd28d", "on-primary": "#432c00",
    "primary-container": "#e5a427", "on-primary-container": "#342100",
    "secondary": "#e6c188", "on-secondary": "#432c02",
    "secondary-container": "#543b0f", "on-secondary-container": "#f5cf95",
    "tertiary": "#cee36a", "on-tertiary": "#2c3400",
    "tertiary-container": "#a5b945", "on-tertiary-container": "#212800",
    "error": "#ffb4ab", "on-error": "#690005",
    "error-container": "#93000a", "on-error-container": "#ffdad6",
    "background": "#18130b", "on-background": "#ede1d3",
    "surface": "#18130b", "on-surface": "#ede1d3",
    "surface-variant": "#504534", "on-surface-variant": "#d5c4ae",
    "outline": "#9d8f7b", "outline-variant": "#504534",
    "surface-container-lowest": "#120d06", "surface-container-low": "#201b12",
    "surface-container": "#251f16", "surface-container-high": "#2f2920",
    "surface-container-highest": "#3b342a",
    "surface-dim": "#18130b", "surface-bright": "#3f382f",
    "inverse-surface": "#ede1d3", "inverse-on-surface": "#362f26",
    "inverse-primary": "#7f5700", "shadow": "#000000", "scrim": "#000000",
    "surface-tint": "#ffba3e",
}

# name -> (light map | None, dark map | None). None means "use the baseline
# token scheme" (i.e. clear overrides).
PRESETS: dict[str, tuple[dict[str, str] | None, dict[str, str] | None]] = {
    "Baseline": (None, None),
    "Catalog": (CATALOG_LIGHT, CATALOG_DARK),
}

__all__ = ["CATALOG_DARK", "CATALOG_LIGHT", "PRESETS"]
