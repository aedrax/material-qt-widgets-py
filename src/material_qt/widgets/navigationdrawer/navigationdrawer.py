"""Material 3 navigation drawer (labs) for QtWidgets.

Ports Material Web's ``labs/navigationdrawer`` — a side panel
(``surface-container-low``) listing destinations as full-corner pill rows. The
active destination fills ``secondary-container`` with ``on-secondary-container``
content; inactive rows are transparent with ``on-surface-variant``. Exclusive
selection; ``changed(index)`` fires on change.

Like Flutter's ``NavigationDrawer``, destinations can be interspersed with other
content — section headers (:meth:`add_section`), dividers (:meth:`add_divider`),
or arbitrary widgets (:meth:`add_widget`). ``changed`` reports the index among
*destinations only*, ignoring the non-destination children.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..divider import MdDivider
from ..icon.icon import material_symbols_font

_ITEM_H = 56
_ICON = 24
_PAD = 16
_GAP = 12
_DRAWER_W = 360  # M3 navigation-drawer container-width


class _DrawerItem(MaterialWidgetMixin, QAbstractButton):
    def __init__(self, label: str, parent: QWidget | None = None, *,
                 icon: str = "", active_icon: str = "") -> None:
        super().__init__(parent)
        self.setText(label)
        self._icon = icon
        self._active_icon = active_icon or icon
        self.setCheckable(True)
        self._init_material(
            shape=ShapeScale.FULL,
            typescale=TypescaleRole.LABEL_LARGE,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE_VARIANT,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggled.connect(lambda *_: self.update())

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_DRAWER_W - 2 * _PAD, _ITEM_H)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(120, _ITEM_H)

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        active = self.isChecked()
        if active:
            painter.fillPath(self.clip_path(),
                             theme.color(ColorRole.SECONDARY_CONTAINER))
        content_role = (
            ColorRole.ON_SECONDARY_CONTAINER if active else ColorRole.ON_SURFACE_VARIANT
        )
        color = theme.color(content_role)
        x = _PAD
        glyph = self._active_icon if active else self._icon
        if glyph:
            font = material_symbols_font(_ICON, filled=active)
            if font is not None:
                painter.setFont(font)
                painter.setPen(color)
                painter.drawText(QRectF(x, 0, _ICON, self.height()),
                                 Qt.AlignmentFlag.AlignCenter, glyph)
            x += _ICON + _GAP
        painter.setFont(self.font())
        painter.setPen(color)
        painter.drawText(QRectF(x, 0, self.width() - x - _PAD, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self.text())


class MdNavigationDrawer(MaterialWidgetMixin, QWidget):
    """A side navigation drawer of destination rows."""

    changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, headline: str = "") -> None:
        super().__init__(parent)
        self._items: list[_DrawerItem] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(_PAD, 12, _PAD, 12)
        self._lay.setSpacing(4)
        if headline:
            h = QLabel(headline)
            h.setFont(font_for_role(TypescaleRole.TITLE_SMALL))
            self._headline = h
            self._lay.addWidget(h)
            self._style_headline()
            ThemeManager.instance().themeChanged.connect(self._style_headline)
        self._lay.addStretch(1)
        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )
        self.setFixedWidth(_DRAWER_W)

    def _style_headline(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_SURFACE_VARIANT).name()
        self._headline.setStyleSheet(f"color: {c}; padding: 8px 16px;")

    def _insert(self, widget: QWidget) -> None:
        # Always before the trailing stretch (the last layout item).
        self._lay.insertWidget(self._lay.count() - 1, widget)

    def add_destination(self, label: str, *, icon: str = "",
                        active_icon: str = "") -> _DrawerItem:
        item = _DrawerItem(label, icon=icon, active_icon=active_icon)
        self._group.addButton(item, len(self._items))
        self._insert(item)
        self._items.append(item)
        item.toggled.connect(
            lambda on, it=item: on and self.changed.emit(self._items.index(it))
        )
        if len(self._items) == 1:
            item.setChecked(True)
        return item

    def add_section(self, text: str) -> QLabel:
        """Add a non-destination section header between destinations."""
        label = QLabel(text)
        label.setFont(font_for_role(TypescaleRole.TITLE_SMALL))

        def style() -> None:
            c = ThemeManager.instance().color(ColorRole.ON_SURFACE_VARIANT).name()
            label.setStyleSheet(f"color: {c}; padding: 16px 16px 8px 16px;")

        style()
        ThemeManager.instance().themeChanged.connect(style)
        self._insert(label)
        return label

    def add_divider(self) -> MdDivider:
        """Add a divider between destinations."""
        divider = MdDivider()
        self._insert(divider)
        return divider

    def add_widget(self, widget: QWidget) -> None:
        """Add an arbitrary widget (does not count as a destination)."""
        self._insert(widget)

    def changeEvent(self, event) -> None:  # noqa: N802
        super().changeEvent(event)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdNavigationDrawer"]
