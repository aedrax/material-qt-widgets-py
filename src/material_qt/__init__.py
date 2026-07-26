"""material-qt: a Qt6 / PySide6 (QtWidgets) port of Material Design 3.

The full component catalogue lives in :mod:`material_qt.widgets` and is
re-exported here alongside the theming API, so applications can write::

    from material_qt import MdFilledButton, ThemeManager, ThemeMode

Design tokens and shared widget machinery stay namespaced under
:mod:`material_qt.tokens` and :mod:`material_qt.core`.
"""

from __future__ import annotations

from .theme import ColorScheme, ThemeManager, ThemeMode
from .widgets import *  # noqa: F403
from .widgets import __all__ as _widgets_all

__version__ = "1.0.0"

__all__ = ["ColorScheme", "ThemeManager", "ThemeMode", "__version__", *_widgets_all]
