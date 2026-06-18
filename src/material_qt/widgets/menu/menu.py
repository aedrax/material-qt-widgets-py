"""Material 3 menu for QtWidgets.

Ports Material Web's ``menu/`` — :class:`MdMenu`, a popup surface
(``surface-container`` + level-2 elevation, corner-extra-small) of
:class:`MdMenuItem` rows, anchored below a trigger widget. Uses the ``Qt.Popup``
window flag so it dismisses on an outside click; Escape also closes it and the
arrow keys move between items. Selecting an item emits ``selected(text)``.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_ITEM_H = 48
_PAD = 12
_ICON = 24
_GAP = 12
_SHADOW_MARGIN = 14


class MdMenuItem(MaterialWidgetMixin, QWidget):
    """A single row in a menu."""

    triggered = Signal()

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        leading_icon: str = "",
        trailing_text: str = "",
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._leading_icon = leading_icon
        self._trailing_text = trailing_text
        self._init_material(
            shape=ShapeScale.NONE,
            typescale=TypescaleRole.BODY_LARGE,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE,
            surface_role=ColorRole.SURFACE_CONTAINER,
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @property
    def text(self) -> str:
        return self._text

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = _PAD * 2 + metrics.horizontalAdvance(self._text)
        if self._leading_icon:
            w += _ICON + _GAP
        if self._trailing_text:
            w += _GAP + metrics.horizontalAdvance(self._trailing_text)
        return QSize(w, _ITEM_H)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(112, _ITEM_H)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self.triggered.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)
        theme = ThemeManager.instance()
        color = theme.color(ColorRole.ON_SURFACE)
        x = _PAD
        if self._leading_icon:
            font = material_symbols_font(_ICON, filled=False)
            if font is not None:
                painter.setFont(font)
                painter.setPen(theme.color(ColorRole.ON_SURFACE_VARIANT))
                painter.drawText(QRectF(x, 0, _ICON, self.height()),
                                 Qt.AlignmentFlag.AlignCenter, self._leading_icon)
            x += _ICON + _GAP
        painter.setFont(self.font())
        painter.setPen(color)
        painter.drawText(QRectF(x, 0, self.width() - x - _PAD, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self._text)
        if self._trailing_text:
            painter.setPen(theme.color(ColorRole.ON_SURFACE_VARIANT))
            painter.drawText(QRectF(0, 0, self.width() - _PAD, self.height()),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             self._trailing_text)


class MdMenu(QWidget):
    """A popup menu surface anchored below a trigger widget."""

    selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._items: list[MdMenuItem] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN
        )
        self._panel = _MenuPanel()
        self._panel_lay = QVBoxLayout(self._panel)
        self._panel_lay.setContentsMargins(0, 8, 0, 8)
        self._panel_lay.setSpacing(0)
        outer.addWidget(self._panel)

    def add_item(self, item: MdMenuItem) -> None:
        item.triggered.connect(lambda i=item: self._on_triggered(i))
        self._panel_lay.addWidget(item)
        self._items.append(item)

    def _on_triggered(self, item: MdMenuItem) -> None:
        self.selected.emit(item.text)
        self.close()

    def open_at(self, anchor: QWidget) -> None:
        """Show the menu just below ``anchor`` (left-aligned)."""
        self.adjustSize()
        bottom_left = anchor.mapToGlobal(anchor.rect().bottomLeft())
        self.move(bottom_left.x() - _SHADOW_MARGIN, bottom_left.y() - _SHADOW_MARGIN + 4)
        self.show()
        self.setFocus()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
            return
        if key in (Qt.Key.Key_Down, Qt.Key.Key_Up) and self._items:
            cur = next((i for i, it in enumerate(self._items) if it.hasFocus()), -1)
            step = 1 if key == Qt.Key.Key_Down else -1
            nxt = (cur + step) % len(self._items)
            self._items[nxt].setFocus()
            return
        super().keyPressEvent(event)


class _MenuPanel(MaterialWidgetMixin, QWidget):
    """The rounded, elevated surface holding the menu items."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.EXTRA_SMALL,
            elevation=ElevationLevel.LEVEL2,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdMenu", "MdMenuItem"]
