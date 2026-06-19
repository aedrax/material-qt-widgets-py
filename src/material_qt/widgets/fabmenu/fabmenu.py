"""Material 3 FAB menu (Expressive) for QtWidgets.

Ports the Material 3 Expressive FAB menu: a primary FAB that toggles open a
vertical column of labeled menu items (each a small FAB with a leading label).
The toggle FAB's icon flips between ``add`` and ``close``. ``itemClicked(index)``
fires when a menu item is activated; ``toggled(bool)`` on open/close.

Items are laid out as nested layouts (not wrapper widgets) directly in the
menu's column, so each small FAB's level-3 drop shadow is clipped only by the
menu's (inset) bounds rather than by a tight per-row widget.

Deferred (scaffold): the background scrim (use the dialog/bottom-sheet pattern)
and the staggered open/close item animation — items simply show/hide.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..fab import FabColor, FabSize, MdFab

# Inset so the FABs' level-3 drop shadow (~16px blur, 4px down-offset) is not
# clipped at the widget edge.
_M = 18


class MdFabMenu(QWidget):
    """A FAB that expands into a vertical menu of labeled items."""

    itemClicked = Signal(int)
    toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None, *, icon: str = "add") -> None:
        super().__init__(parent)
        self._open = False
        self._closed_icon = icon
        self._items: list[tuple[QLabel, MdFab]] = []

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(_M, _M, _M, _M + 4)
        self._lay.setSpacing(12)
        # A leading stretch absorbs any extra height so items stay packed just
        # above the FAB instead of being stretched apart.
        self._lay.addStretch(1)

        self._fab = MdFab(icon, size=FabSize.REGULAR, color=FabColor.PRIMARY)
        self._fab.clicked.connect(self.toggle)
        self._lay.addWidget(self._fab, 0, Qt.AlignmentFlag.AlignRight)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

    def add_item(self, label: str, *, icon: str = "") -> MdFab:
        """Add a labeled menu item; returns its (small) FAB."""
        index = len(self._items)
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addStretch(1)
        lbl = QLabel(label)
        lbl.setFont(font_for_role(TypescaleRole.LABEL_LARGE))
        self._style_label(lbl)
        ThemeManager.instance().themeChanged.connect(lambda lb=lbl: self._style_label(lb))
        row.addWidget(lbl)
        fab = MdFab(icon, size=FabSize.SMALL, color=FabColor.SECONDARY)
        fab.clicked.connect(lambda: self._on_item(index))
        row.addWidget(fab)
        # Insert above the FAB (the FAB is the last item in the column).
        self._lay.insertLayout(self._lay.count() - 1, row)
        lbl.setVisible(self._open)
        fab.setVisible(self._open)
        self._items.append((lbl, fab))
        return fab

    def _style_label(self, lbl: QLabel) -> None:
        lbl.setStyleSheet(
            f"color: {ThemeManager.instance().color(ColorRole.ON_SURFACE).name()};"
        )

    @property
    def is_open(self) -> bool:
        return self._open

    def toggle(self) -> None:
        self.set_open(not self._open)

    def set_open(self, open_: bool) -> None:
        if open_ == self._open:
            return
        self._open = open_
        for lbl, fab in self._items:
            lbl.setVisible(open_)
            fab.setVisible(open_)
        self._fab.set_icon("close" if open_ else self._closed_icon)
        self.toggled.emit(open_)

    def _on_item(self, index: int) -> None:
        self.itemClicked.emit(index)
        self.set_open(False)


__all__ = ["MdFabMenu"]
