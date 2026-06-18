"""Material 3 list for QtWidgets.

Ports Material Web's ``list/`` — :class:`MdList` (a surface container) holding
:class:`MdListItem` rows. A list item reuses the :class:`MdItem` layout
primitive (leading / headline / supporting / trailing slots) and adds
interaction: ripple + focus ring + a ``clicked`` signal, with a 56px minimum
height. Non-interactive items are supported via ``interactive=False``.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager
from ..divider import MdDivider
from ..item import MdItem

_MIN_HEIGHT = 56


class MdListItem(MaterialWidgetMixin, QWidget):
    """An interactive list row composing the MdItem layout."""

    clicked = Signal()

    def __init__(
        self,
        headline: str = "",
        parent: QWidget | None = None,
        *,
        supporting_text: str = "",
        trailing_supporting_text: str = "",
        leading: QWidget | None = None,
        trailing: QWidget | None = None,
        interactive: bool = True,
    ) -> None:
        super().__init__(parent)
        self._interactive = interactive
        self._item = MdItem(
            headline,
            supporting_text=supporting_text,
            trailing_supporting_text=trailing_supporting_text,
            leading=leading,
            trailing=trailing,
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._item)

        self._init_material(
            shape=ShapeScale.NONE,
            ripple=interactive,
            focus_ring=interactive,
            ripple_role=ColorRole.ON_SURFACE,
            surface_role=ColorRole.SURFACE,
        )
        if interactive:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    @property
    def item(self) -> MdItem:
        return self._item

    def sizeHint(self) -> QSize:  # noqa: N802
        hint = self._item.sizeHint()
        return QSize(hint.width(), max(_MIN_HEIGHT, hint.height()))

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._item.minimumSizeHint().width(), _MIN_HEIGHT)

    # -- interaction -------------------------------------------------------

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if (
            self._interactive
            and event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if self._interactive and event.key() in (
            Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space
        ):
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class MdList(MaterialWidgetMixin, QWidget):
    """A surface container holding list items, with optional dividers."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 8, 0, 8)
        self._lay.setSpacing(0)
        self._lay.addStretch(1)
        self._items: list[MdListItem] = []
        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )

    def add_item(self, item: MdListItem, *, divider: bool = False) -> None:
        if divider and self._items:
            self._lay.insertWidget(self._lay.count() - 1, MdDivider())
        self._lay.insertWidget(self._lay.count() - 1, item)
        self._items.append(item)

    @property
    def items(self) -> list[MdListItem]:
        return list(self._items)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdList", "MdListItem"]
