"""Material 3 FAB menu (Expressive) for QtWidgets.

Ports the Material 3 Expressive FAB menu: a primary FAB that toggles open a
vertical column of labeled menu items (each a small FAB with a leading label).
The toggle FAB's icon flips between ``add`` and ``close``. ``itemClicked(index)``
fires when a menu item is activated; ``toggled(bool)`` on open/close.

Deferred (scaffold): the background scrim (use the dialog/bottom-sheet pattern)
and the staggered open/close item animation — items simply show/hide.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..fab import FabColor, FabSize, MdFab


class _MenuItemRow(QWidget):
    """A label + small FAB row for one menu entry."""

    clicked = Signal()

    def __init__(self, label: str, icon: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addStretch(1)
        self._label = QLabel(label)
        self._label.setFont(font_for_role(TypescaleRole.LABEL_LARGE))
        lay.addWidget(self._label)
        self._fab = MdFab(icon, size=FabSize.SMALL, color=FabColor.SECONDARY)
        self._fab.clicked.connect(self.clicked.emit)
        lay.addWidget(self._fab)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def _restyle(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        self._label.setStyleSheet(f"color: {c};")


class MdFabMenu(QWidget):
    """A FAB that expands into a vertical menu of labeled items."""

    itemClicked = Signal(int)
    toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None, *, icon: str = "add") -> None:
        super().__init__(parent)
        self._open = False
        self._closed_icon = icon
        self._rows: list[_MenuItemRow] = []

        self._lay = QVBoxLayout(self)
        # The FABs carry a level-3 drop shadow (~16px blur, 4px down-offset);
        # inset the content so those shadows are not clipped at the widget edge.
        self._lay.setContentsMargins(18, 18, 18, 22)
        self._lay.setSpacing(12)
        self._lay.setAlignment(Qt.AlignmentFlag.AlignRight)

        self._items_box = QVBoxLayout()
        self._items_box.setSpacing(12)
        self._items_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._lay.addLayout(self._items_box)

        self._fab = MdFab(icon, size=FabSize.REGULAR, color=FabColor.PRIMARY)
        self._fab.clicked.connect(self.toggle)
        self._lay.addWidget(self._fab, 0, Qt.AlignmentFlag.AlignRight)

    def add_item(self, label: str, *, icon: str = "") -> _MenuItemRow:
        index = len(self._rows)
        row = _MenuItemRow(label, icon)
        row.clicked.connect(lambda i=index: self._on_item(i))
        row.setVisible(self._open)
        self._items_box.addWidget(row)
        self._rows.append(row)
        return row

    @property
    def is_open(self) -> bool:
        return self._open

    def toggle(self) -> None:
        self.set_open(not self._open)

    def set_open(self, open_: bool) -> None:
        if open_ == self._open:
            return
        self._open = open_
        for row in self._rows:
            row.setVisible(open_)
        self._fab.set_icon("close" if open_ else self._closed_icon)
        self.toggled.emit(open_)

    def _on_item(self, index: int) -> None:
        self.itemClicked.emit(index)
        self.set_open(False)


__all__ = ["MdFabMenu"]
