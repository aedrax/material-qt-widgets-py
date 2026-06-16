"""MdIcon: a Material Symbols icon widget for QtWidgets.

Ports Material Web's ``md-icon``. The web component renders a Material Symbols
glyph using a ligature name (its text content), at a default size of 24px, with
``color`` inheriting from the surrounding text color (``currentColor``), which in
Material defaults to ``on-surface``. ``font-weight`` is 400 and the ``FILL`` axis
toggles between the outlined (0) and filled (1) styles.

Font availability
-----------------
The "Material Symbols Outlined" font is a variable icon font that is often not
installed on a given system. :class:`MdIcon` resolves a usable font family at
construction time:

1. If a Material Symbols font family is already registered with Qt (either
   installed system-wide or loaded earlier via this class), it is used.
2. Otherwise this class tries to load a ``.ttf``/``.otf`` from a list of
   candidate paths (and the ``MATERIAL_SYMBOLS_FONT`` environment variable) via
   :meth:`QFontDatabase.addApplicationFont`.
3. If no Material Symbols font can be found, :class:`MdIcon` falls back to
   rendering the icon *name* as plain text inside a placeholder box (so the
   widget never crashes and the meaning is still legible).
   :attr:`MdIcon.font_available` reports which case applies, and
   :meth:`MdIcon.register_font` lets callers register a font at runtime.
"""

from __future__ import annotations

import os
from enum import Enum

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...theme.theme_manager import ThemeManager
from ...tokens.color import ColorRole

# Default icon size in logical pixels (md-icon: --md-icon-size: 24px).
DEFAULT_ICON_SIZE = 24

# Material Symbols / Material Icons family names, in preference order. The first
# one that is registered with Qt wins.
_MATERIAL_FAMILIES = (
    "Material Symbols Outlined",
    "Material Symbols Rounded",
    "Material Symbols Sharp",
    "Material Icons Outlined",
    "Material Icons",
)

# The Material Symbols Outlined variable font is bundled with the package so
# glyphs render out of the box without any system font installed.
_BUNDLED_FONT = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, "assets",
        "MaterialSymbolsOutlined.ttf",
    )
)

# Candidate filesystem locations for a Material Symbols/Icons font file. Checked
# only if no family is already registered. The MATERIAL_SYMBOLS_FONT env var, if
# set, is checked first, then the bundled font, then common system locations.
_FONT_FILE_CANDIDATES = (
    _BUNDLED_FONT,
    "/usr/share/fonts/truetype/material-symbols/MaterialSymbolsOutlined.ttf",
    "/usr/share/fonts/MaterialSymbolsOutlined.ttf",
    "/usr/share/fonts/truetype/material-design-icons/MaterialIcons-Regular.ttf",
    "/usr/share/fonts/truetype/MaterialIcons-Regular.ttf",
    "/usr/share/fonts/MaterialIcons-Regular.ttf",
    os.path.expanduser("~/.fonts/MaterialSymbolsOutlined.ttf"),
    os.path.expanduser("~/.local/share/fonts/MaterialSymbolsOutlined.ttf"),
)


class IconStyle(Enum):
    """Material Symbols visual style (maps to a family when one is available)."""

    OUTLINED = "Material Symbols Outlined"
    ROUNDED = "Material Symbols Rounded"
    SHARP = "Material Symbols Sharp"


def _registered_material_family(preferred: str | None = None) -> str | None:
    """Return a Material Symbols/Icons family registered with Qt, if any.

    If ``preferred`` is given and registered, it takes priority.
    """
    families = set(QFontDatabase.families())
    if preferred and preferred in families:
        return preferred
    for family in _MATERIAL_FAMILIES:
        if family in families:
            return family
    return None


def _try_load_font_file() -> str | None:
    """Attempt to load a candidate Material font file into Qt.

    Returns the first family name added, or ``None`` if nothing loaded.
    """
    candidates: list[str] = []
    env_path = os.environ.get("MATERIAL_SYMBOLS_FONT")
    if env_path:
        candidates.append(env_path)
    candidates += list(_FONT_FILE_CANDIDATES)
    for path in candidates:
        if not path or not os.path.isfile(path):
            continue
        font_id = QFontDatabase.addApplicationFont(path)
        if font_id == -1:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            return families[0]
    return None


class MdIcon(QWidget):
    """A Material Symbols icon, rendered by ligature name.

    Parameters
    ----------
    name:
        The icon ligature name (e.g. ``"favorite"``) or any text to render.
    parent:
        Optional parent widget.
    size:
        Icon box size in logical pixels (default 24).
    filled:
        Whether to use the filled (FILL 1) variant. Only has a visible effect
        when the loaded Material Symbols font supports the FILL variation axis.
    style:
        Which Material Symbols style family to prefer.
    color_role:
        Theme color role for the glyph (default ``ON_SURFACE``, matching the
        web ``currentColor`` default).
    """

    def __init__(
        self,
        name: str = "",
        parent: QWidget | None = None,
        *,
        size: int = DEFAULT_ICON_SIZE,
        filled: bool = False,
        style: IconStyle = IconStyle.OUTLINED,
        color_role: ColorRole = ColorRole.ON_SURFACE,
    ) -> None:
        super().__init__(parent)
        self._name = name
        self._size = max(1, int(size))
        self._filled = bool(filled)
        self._style = style
        self._color_role = color_role

        # Resolve a Material Symbols family once per instance. Loading is cheap
        # and idempotent for already-registered fonts.
        self._family = self._resolve_family()

        # The icon is decorative by default (web sets aria-hidden="true"); expose
        # the name as an accessible name for screen readers.
        self.setAccessibleName(name)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        ThemeManager.instance().themeChanged.connect(self.update)

    # -- font resolution ---------------------------------------------------

    @classmethod
    def register_font(cls, path: str) -> str | None:
        """Register a Material Symbols font file with Qt at runtime.

        Returns the registered family name, or ``None`` on failure. Useful for
        applications that ship their own copy of the font.
        """
        if not os.path.isfile(path):
            return None
        font_id = QFontDatabase.addApplicationFont(path)
        if font_id == -1:
            return None
        families = QFontDatabase.applicationFontFamilies(font_id)
        return families[0] if families else None

    def _resolve_family(self) -> str | None:
        preferred = self._style.value
        family = _registered_material_family(preferred)
        if family is not None:
            return family
        # Nothing registered yet: try to load a font file from disk.
        loaded = _try_load_font_file()
        if loaded is not None:
            return _registered_material_family(preferred) or loaded
        return None

    @property
    def font_available(self) -> bool:
        """Whether a Material Symbols/Icons font was found for rendering."""
        return self._family is not None

    @property
    def font_family(self) -> str | None:
        """The resolved Material Symbols family name, or ``None`` if unavailable."""
        return self._family

    # -- properties --------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        if name == self._name:
            return
        self._name = name
        self.setAccessibleName(name)
        self.updateGeometry()
        self.update()

    @property
    def icon_size(self) -> int:
        return self._size

    def set_size(self, size: int) -> None:
        size = max(1, int(size))
        if size == self._size:
            return
        self._size = size
        self.updateGeometry()
        self.update()

    @property
    def filled(self) -> bool:
        return self._filled

    def set_filled(self, filled: bool) -> None:
        filled = bool(filled)
        if filled == self._filled:
            return
        self._filled = filled
        self.update()

    @property
    def color_role(self) -> ColorRole:
        return self._color_role

    def set_color_role(self, role: ColorRole) -> None:
        """Set the glyph color role (default ``ON_SURFACE``)."""
        if role == self._color_role:
            return
        self._color_role = role
        self.update()

    # -- font --------------------------------------------------------------

    def _build_font(self) -> QFont:
        font = QFont()
        if self._family is not None:
            font.setFamily(self._family)
            font.setFamilies([self._family])
            font.setPixelSize(self._size)
            font.setWeight(QFont.Weight(400))
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            # FILL axis: filled = 1, outlined = 0. Variable-font axes are set via
            # QFont.setVariableAxis on Qt 6.7+. Guarded so older Qt still works.
            set_axis = getattr(font, "setVariableAxis", None)
            if set_axis is not None:
                try:
                    set_axis("FILL", 1.0 if self._filled else 0.0)
                    set_axis("wght", 400.0)
                    set_axis("opsz", float(self._size))
                except (TypeError, ValueError):
                    pass
        else:
            # Fallback: render the name as small plain text inside the box.
            font.setPixelSize(max(7, min(self._size // 3, 12)))
        return font

    # -- geometry ----------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._size, self._size)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._size, self._size)

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        color = ThemeManager.instance().color(self._color_role)
        painter.setPen(color)
        painter.setFont(self._build_font())

        rect = self.rect()
        if self._family is not None:
            # Ligature rendering: the name resolves to a single glyph.
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._name)
        elif self._name:
            # No icon font: draw a placeholder square outline + truncated label
            # so the widget is still meaningful and never blank/crashing.
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = max(1, self._size // 8)
            painter.drawRect(rect.adjusted(inset, inset, -inset, -inset))
            metrics = QFontMetrics(painter.font())
            label = metrics.elidedText(
                self._name, Qt.TextElideMode.ElideRight, rect.width() - 2 * inset
            )
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
        painter.end()


__all__ = ["DEFAULT_ICON_SIZE", "IconStyle", "MdIcon"]
