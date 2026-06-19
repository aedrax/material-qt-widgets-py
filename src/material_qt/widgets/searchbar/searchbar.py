"""Material 3 search bar for QtWidgets.

Ports the Material 3 search bar (the resting state of ``SearchAnchor`` / the
docked search field): a fully-rounded ``surface-container-high`` bar with a
leading search icon, a borderless text input (``body-large``), and an optional
trailing icon. ``textChanged(str)`` fires on edits; ``submitted(str)`` fires on
Enter. The full-screen search *view* (results overlay) is deferred.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import MdIcon

_HEIGHT = 56
_PAD = 16


class MdSearchBar(MaterialWidgetMixin, QWidget):
    """A Material 3 docked search bar."""

    textChanged = Signal(str)  # noqa: N815  (Qt-style signal name)
    submitted = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "Search",
        trailing_icon: str = "",
    ) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.FULL,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_HIGH,
        )
        self.setFixedHeight(_HEIGHT)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(_PAD, 0, _PAD, 0)
        lay.setSpacing(_PAD)

        self._leading = MdIcon("search", color_role=ColorRole.ON_SURFACE_VARIANT)
        self._leading.set_size(24)
        lay.addWidget(self._leading, 0)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setFont(font_for_role(TypescaleRole.BODY_LARGE))
        self._edit.setFrame(False)
        self._edit.setStyleSheet("background: transparent; border: none;")
        self._edit.textChanged.connect(self.textChanged.emit)
        self._edit.returnPressed.connect(lambda: self.submitted.emit(self._edit.text()))
        lay.addWidget(self._edit, 1)

        if trailing_icon:
            trail = MdIcon(trailing_icon, color_role=ColorRole.ON_SURFACE_VARIANT)
            trail.set_size(24)
            lay.addWidget(trail, 0)

        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def text(self) -> str:
        return self._edit.text()

    def set_text(self, text: str) -> None:
        self._edit.setText(text)

    def _restyle(self) -> None:
        theme = ThemeManager.instance()
        on_surface = theme.color(ColorRole.ON_SURFACE).name()
        hint = theme.color(ColorRole.ON_SURFACE_VARIANT).name()
        self._edit.setStyleSheet(
            "background: transparent; border: none;"
            f"color: {on_surface}; selection-background-color: {hint};"
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdSearchBar"]
