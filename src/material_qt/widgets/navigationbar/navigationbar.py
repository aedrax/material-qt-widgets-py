"""Material 3 navigation bar (labs) for QtWidgets.

Ports Material Web's ``labs/navigationbar`` — a bottom bar (``surface-container``,
80px tall) holding 3-5 :class:`MdNavigationTab` destinations with exclusive
selection. ``changed(index)`` fires when the active destination changes.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ..navigationtab import MdNavigationTab

_HEIGHT = 80


class MdNavigationBar(MaterialWidgetMixin, QWidget):
    """A bottom navigation bar of icon+label destinations."""

    changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *,
                 label_behavior: str = "always") -> None:
        super().__init__(parent)
        self._tabs: list[MdNavigationTab] = []
        self._label_behavior = label_behavior
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER,
        )
        self.setFixedHeight(_HEIGHT)

    def add_destination(self, label: str, *, icon: str = "",
                        active_icon: str = "", badge: str | None = None) -> MdNavigationTab:
        tab = MdNavigationTab(label, icon=icon, active_icon=active_icon)
        tab.set_label_behavior(self._label_behavior)
        if badge is not None:
            tab.set_badge(badge)
        self._group.addButton(tab, len(self._tabs))
        self._lay.addWidget(tab)
        self._tabs.append(tab)
        tab.toggled.connect(lambda on, t=tab: on and self.changed.emit(self._tabs.index(t)))
        if len(self._tabs) == 1:
            tab.setChecked(True)
        return tab

    def set_label_behavior(self, behavior: str) -> None:
        """``"always"`` / ``"selected"`` / ``"hide"`` — when to show labels."""
        self._label_behavior = behavior
        for tab in self._tabs:
            tab.set_label_behavior(behavior)

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(max(360, sum(t.sizeHint().width() for t in self._tabs)), _HEIGHT)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdNavigationBar"]
