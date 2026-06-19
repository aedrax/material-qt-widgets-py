"""Material 3 expansion panel for QtWidgets.

An expandable panel (cf. Flutter's ``ExpansionTile``): a clickable header
(``title-medium`` title + a trailing chevron that flips) over collapsible content
that animates its height open/closed. ``toggled(bool)`` fires on expand/collapse.

The content's expanded height is measured at expand time (after layout has given
the panel a real width), so wrapped-text content is not clipped. Panels are
independent — exclusive-accordion grouping is deferred.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import animate
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import MdIcon

_PAD = 16
_HEADER_H = 56
_MAX = 16777215  # QWIDGETSIZE_MAX


class _Header(MaterialWidgetMixin, QWidget):
    clicked = Signal()

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.NONE, ripple=True, focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        self.setFixedHeight(_HEADER_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(_PAD, 0, _PAD, 0)
        self._title = QLabel(title)
        self._title.setFont(font_for_role(TypescaleRole.TITLE_MEDIUM))
        self._chevron = MdIcon("expand_more", color_role=ColorRole.ON_SURFACE_VARIANT)
        self._chevron.set_size(24)
        lay.addWidget(self._title, 1)
        lay.addWidget(self._chevron, 0)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def _restyle(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        self._title.setStyleSheet(f"color: {c};")

    def set_expanded(self, expanded: bool) -> None:
        self._chevron.set_name("expand_less" if expanded else "expand_more")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class MdExpansionPanel(QWidget):
    """An expandable header + collapsible content panel."""

    toggled = Signal(bool)

    def __init__(self, title: str = "", parent: QWidget | None = None,
                 *, expanded: bool = False) -> None:
        super().__init__(parent)
        self._expanded = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._header = _Header(title)
        self._header.clicked.connect(self.toggle)
        lay.addWidget(self._header)

        self._content = QWidget()
        self._content_lay = QVBoxLayout(self._content)
        self._content_lay.setContentsMargins(_PAD, 0, _PAD, _PAD)
        self._content_lay.setSpacing(8)
        self._content.setMaximumHeight(0)
        lay.addWidget(self._content)

        if expanded:
            self.set_expanded(True, animated=False)

    def add_content(self, widget: QWidget) -> None:
        self._content_lay.addWidget(widget)

    @property
    def expanded(self) -> bool:
        return self._expanded

    def toggle(self) -> None:
        self.set_expanded(not self._expanded)

    def set_expanded(self, expanded: bool, *, animated: bool = True) -> None:
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self._header.set_expanded(expanded)
        if expanded:
            # Measure now — after layout has given the panel its width.
            target = self._content.sizeHint().height()
            if animated:
                animate(self._content, b"maximumHeight", target,
                        duration=Duration.MEDIUM2, easing=Easing.EMPHASIZED,
                        start=0, on_finished=lambda: self._content.setMaximumHeight(_MAX))
            else:
                self._content.setMaximumHeight(_MAX)
        else:
            start = self._content.height()
            self._content.setMaximumHeight(start)
            if animated:
                animate(self._content, b"maximumHeight", 0,
                        duration=Duration.MEDIUM2, easing=Easing.EMPHASIZED, start=start)
            else:
                self._content.setMaximumHeight(0)
        self.toggled.emit(expanded)


__all__ = ["MdExpansionPanel"]
