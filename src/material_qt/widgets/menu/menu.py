"""Material 3 menu for QtWidgets.

Ports Material Web's ``menu/`` — :class:`MdMenu`, a popup surface
(``surface-container`` + level-2 elevation, corner-extra-small) of
:class:`MdMenuItem` rows, anchored below a trigger widget. Uses the ``Qt.Popup``
window flag so it dismisses on an outside click; Escape also closes it and the
arrow keys move between items. Selecting an item emits ``selected(text)``.

A :class:`MdMenuItem` may carry a ``leading_icon`` / ``trailing_icon`` and
``trailing_text`` (e.g. a keyboard shortcut), and can be disabled. A
:class:`MdSubmenuItem` opens a nested :class:`MdMenu` anchored to its right edge
(Flutter ``SubmenuButton``). When a menu would grow taller than ``max_height``
its items scroll inside a :class:`QScrollArea`.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

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
    """A single row in a menu.

    Mirrors Flutter ``MenuItemButton`` / ``PopupMenuItem``: optional
    ``leading_icon`` and ``trailing_icon`` (Material Symbols glyph names), a
    ``trailing_text`` (typically a keyboard ``shortcut``), and an ``enabled``
    flag. Activating it emits ``triggered``.
    """

    triggered = Signal()

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        leading_icon: str = "",
        trailing_icon: str = "",
        trailing_text: str = "",
        enabled: bool = True,
        value: object = None,
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._leading_icon = leading_icon
        self._trailing_icon = trailing_icon
        self._trailing_text = trailing_text
        self._enabled = bool(enabled)
        self._value = value
        self._highlighted = False
        self._init_material(
            shape=ShapeScale.NONE,
            typescale=TypescaleRole.BODY_LARGE,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE,
            surface_role=ColorRole.SURFACE_CONTAINER,
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._sync_cursor()

    # -- properties --------------------------------------------------------

    @property
    def text(self) -> str:
        return self._text

    @property
    def value(self) -> object:
        """The item's value (defaults to its ``text`` when unset)."""
        return self._text if self._value is None else self._value

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self._sync_cursor()
        self.update()

    def set_highlighted(self, on: bool) -> None:
        """Keyboard highlight (used when the menu does not hold widget focus)."""
        on = bool(on)
        if on == self._highlighted:
            return
        self._highlighted = on
        self.update()

    def set_leading_icon(self, name: str) -> None:
        self._leading_icon = name
        self.updateGeometry()
        self.update()

    def set_trailing_icon(self, name: str) -> None:
        self._trailing_icon = name
        self.updateGeometry()
        self.update()

    def _sync_cursor(self) -> None:
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if self._enabled
            else Qt.CursorShape.ArrowCursor
        )

    # -- geometry ----------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = _PAD * 2 + metrics.horizontalAdvance(self._text)
        if self._leading_icon:
            w += _ICON + _GAP
        if self._trailing_icon:
            w += _ICON + _GAP
        if self._trailing_text:
            w += _GAP + metrics.horizontalAdvance(self._trailing_text)
        return QSize(w, _ITEM_H)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(112, _ITEM_H)

    # -- interaction -------------------------------------------------------

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if (
            self._enabled
            and event.button() == Qt.MouseButton.LeftButton
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
        if self._enabled:
            self.paint_material_surface(painter)
        else:
            painter.setOpacity(0.38)
        theme = ThemeManager.instance()
        if self._highlighted and self._enabled:
            # An ON_SURFACE state-layer overlay (hover opacity) so the
            # keyboard-highlighted row reads as focused without widget focus.
            overlay = QColor(theme.color(ColorRole.ON_SURFACE))
            overlay.setAlphaF(0.08)
            painter.fillRect(self.rect(), overlay)
        color = theme.color(ColorRole.ON_SURFACE)
        x = _PAD
        if self._leading_icon:
            self._draw_glyph(painter, self._leading_icon, QRectF(x, 0, _ICON, self.height()))
            x += _ICON + _GAP
        painter.setFont(self.font())
        painter.setPen(color)
        right_reserve = _PAD
        if self._trailing_icon:
            right_reserve += _ICON + _GAP
        painter.drawText(
            QRectF(x, 0, self.width() - x - right_reserve, self.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self._text,
        )
        if self._trailing_icon:
            self._draw_glyph(
                painter,
                self._trailing_icon,
                QRectF(self.width() - _PAD - _ICON, 0, _ICON, self.height()),
            )
        elif self._trailing_text:
            painter.setPen(theme.color(ColorRole.ON_SURFACE_VARIANT))
            painter.drawText(
                QRectF(0, 0, self.width() - _PAD, self.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                self._trailing_text,
            )

    def _draw_glyph(self, painter: QPainter, glyph: str, rect: QRectF) -> None:
        font = material_symbols_font(_ICON, filled=False)
        if font is None:
            return
        painter.setFont(font)
        painter.setPen(ThemeManager.instance().color(ColorRole.ON_SURFACE_VARIANT))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, glyph)


class MdSubmenuItem(MdMenuItem):
    """A menu item that opens a nested :class:`MdMenu` (Flutter ``SubmenuButton``).

    Hovering or clicking the item opens ``submenu`` anchored to its right edge.
    Items added to the submenu emit the parent menu's ``selected`` as usual.
    """

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        leading_icon: str = "",
        submenu_icon: str = "arrow_right",
        enabled: bool = True,
    ) -> None:
        super().__init__(
            text,
            parent,
            leading_icon=leading_icon,
            trailing_icon=submenu_icon,
            enabled=enabled,
        )
        self._submenu = MdMenu(self)
        # Clicking the row opens the submenu rather than selecting it.
        self.triggered.connect(self.open_submenu)

    @property
    def submenu(self) -> MdMenu:
        return self._submenu

    def add_item(self, item: MdMenuItem) -> None:
        """Convenience passthrough to the nested menu."""
        self._submenu.add_item(item)

    def open_submenu(self) -> None:
        if not self._enabled:
            return
        self._submenu.open_at(self, side="right")

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        if self._enabled:
            self.open_submenu()


class MdMenu(QWidget):
    """A popup menu surface anchored to a trigger widget."""

    selected = Signal(str)  # emits the chosen item's text
    activated = Signal(object)  # emits the chosen item's value

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        max_height: int = 0,
        grabs_focus: bool = True,
    ) -> None:
        super().__init__(parent)
        self._grabs_focus = bool(grabs_focus)
        if self._grabs_focus:
            # A standard menu: ``Qt.Popup`` takes an implicit keyboard+mouse grab
            # and dismisses on an outside click. Used for read-only selects and
            # plain menus where the menu itself owns keyboard navigation.
            self.setWindowFlags(
                Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
            )
        else:
            # A non-grabbing options surface (autocomplete / filterable select):
            # the keyboard stays on the typing field, so it must NOT grab focus.
            # Mirrors the QCompleter popup pattern. Dismissal is driven by the
            # owning field (focus-out / Escape), not by Qt.Popup.
            self.setWindowFlags(
                Qt.WindowType.Tool
                | Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.NoDropShadowWindowHint
            )
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._items: list[MdMenuItem] = []
        self._max_height = int(max_height)
        self._highlight = -1  # index of the keyboard-highlighted item

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN
        )
        self._panel = _MenuPanel()
        self._panel_lay = QVBoxLayout(self._panel)
        self._panel_lay.setContentsMargins(0, 8, 0, 8)
        self._panel_lay.setSpacing(0)

        # The panel scrolls when its content exceeds ``max_height``.
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._scroll.viewport().setAutoFillBackground(False)
        self._scroll.setWidget(self._panel)
        outer.addWidget(self._scroll)

    # -- properties --------------------------------------------------------

    def set_max_height(self, height: int) -> None:
        self._max_height = int(height)

    def add_item(self, item: MdMenuItem) -> None:
        item.triggered.connect(lambda i=item: self._on_triggered(i))
        self._panel_lay.addWidget(item)
        self._items.append(item)

    def clear(self) -> None:
        for item in self._items:
            self._panel_lay.removeWidget(item)
            item.setParent(None)
            item.deleteLater()
        self._items.clear()
        self._highlight = -1

    def _on_triggered(self, item: MdMenuItem) -> None:
        # A submenu item opens its child menu instead of dismissing.
        if isinstance(item, MdSubmenuItem):
            return
        self.selected.emit(item.text)
        self.activated.emit(item.value)
        self.close()

    # -- placement ---------------------------------------------------------

    def open_at(self, anchor: QWidget, *, side: str = "bottom") -> None:
        """Show the menu next to ``anchor``.

        ``side="bottom"`` (default) anchors below the trigger, left-aligned;
        ``side="right"`` anchors to the trigger's right edge (used by submenus).
        """
        # Cap the popup height (and let the panel scroll past ``max_height``).
        # ``setMaximumHeight`` — not ``setFixedHeight`` — so a later re-filter
        # with fewer items can shrink the menu again.
        if self._max_height > 0:
            self.setMaximumHeight(self._max_height + 2 * _SHADOW_MARGIN)
        else:
            self.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX (uncapped)
        self.adjustSize()

        if side == "right":
            corner = anchor.mapToGlobal(anchor.rect().topRight())
            self.move(corner.x() - _SHADOW_MARGIN, corner.y() - _SHADOW_MARGIN)
        else:
            corner = anchor.mapToGlobal(anchor.rect().bottomLeft())
            self.move(corner.x() - _SHADOW_MARGIN, corner.y() - _SHADOW_MARGIN + 4)
        self.show()
        if self._grabs_focus:
            self.setFocus()

    # -- keyboard navigation ----------------------------------------------
    #
    # ``_highlight`` tracks the active row so navigation works whether the menu
    # holds widget focus (grabbing popup) or is driven by an external field
    # forwarding keys (non-grabbing autocomplete/filter popup).

    def _set_highlight(self, index: int) -> None:
        if not self._items:
            self._highlight = -1
            return
        index %= len(self._items)
        if self._highlight == index:
            return
        if 0 <= self._highlight < len(self._items):
            self._items[self._highlight].set_highlighted(False)
        self._highlight = index
        self._items[index].set_highlighted(True)
        if self._grabs_focus:
            self._items[index].setFocus()

    def highlight_first(self) -> None:
        """Highlight the first item (used so Enter commits the top match)."""
        if self._items:
            self._set_highlight(0)

    def highlight_next(self) -> None:
        self._set_highlight(self._highlight + 1)

    def highlight_prev(self) -> None:
        self._set_highlight(self._highlight - 1)

    def activate_highlighted(self) -> bool:
        """Trigger the highlighted item. Returns True if one was activated."""
        if 0 <= self._highlight < len(self._items):
            self._items[self._highlight].triggered.emit()
            return True
        return False

    def keyPressEvent(self, event) -> None:  # noqa: N802
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
            return
        if key == Qt.Key.Key_Down:
            self.highlight_next()
            return
        if key == Qt.Key.Key_Up:
            self.highlight_prev()
            return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.activate_highlighted():
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


__all__ = ["MdMenu", "MdMenuItem", "MdSubmenuItem"]
