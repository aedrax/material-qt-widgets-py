"""Material 3 select for QtWidgets.

Ports Material Web's ``select/`` (and Flutter's ``DropdownMenu`` /
``DropdownButton``) — filled and outlined selects. A select reuses the
:class:`MdField` chrome (label, indicator/outline, supporting text) showing the
chosen option, with a trailing dropdown arrow; clicking opens an
:class:`MdMenu` of options below it. Choosing an option updates the value and
emits ``changed(value)``.

Exposes ``items``/``value``/``changed``, ``label``/``hint_text``, ``enabled``,
``leading_icon`` and ``menu_height``. When ``enable_filter`` is set the field is
editable and typing narrows the open menu (Flutter ``enableFilter``).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from ..field import FieldVariant, MdField
from ..icon import MdIcon
from ..menu import MdMenu, MdMenuItem

_ARROW = 24


class _MdSelect(QWidget):
    """Base select; use a variant subclass."""

    VARIANT = FieldVariant.FILLED

    changed = Signal(object)  # emits the selected value

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        label: str = "",
        hint_text: str = "",
        supporting_text: str = "",
        items: list | None = None,
        value: object = None,
        enabled: bool = True,
        leading_icon: str = "",
        menu_height: int = 0,
        enable_filter: bool = False,
    ) -> None:
        super().__init__(parent)
        self._options: list[tuple[str, object]] = []
        self._value: object = None
        self._enabled = bool(enabled)
        self._leading_icon = leading_icon
        self._menu_height = int(menu_height)
        self._enable_filter = bool(enable_filter)
        self._menu: MdMenu | None = None

        self._field = MdField(
            variant=self.VARIANT, label=label, supporting_text=supporting_text
        )
        self._display = QLineEdit()
        self._display.setReadOnly(not self._enable_filter)
        if hint_text:
            self._display.setPlaceholderText(hint_text)
        self._field.set_content(self._display)

        # Optional leading icon at the field's left edge.
        self._leading: MdIcon | None = None
        if self._leading_icon:
            self._leading = MdIcon(self._leading_icon, parent=self._field)
            self._leading.set_size(_ARROW)

        # Trailing dropdown arrow overlaid at the field's right edge.
        self._arrow = MdIcon("arrow_drop_down", parent=self._field)
        self._arrow.set_size(_ARROW)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._field)

        # Open the menu on a click anywhere in the field / display / arrow.
        for w in (self._field, self._display, self._arrow):
            w.installEventFilter(self)
        self._field.installEventFilter(self)  # also for Resize repositioning
        self._sync_cursor()

        if self._enable_filter:
            self._display.textEdited.connect(self._on_text_edited)

        if items:
            self.set_options(items)
        if value is not None:
            self.set_value(value)

    # -- options / value ---------------------------------------------------

    def add_option(self, text: str, value: object = None) -> None:
        self._options.append((text, text if value is None else value))

    def set_options(self, items: list) -> None:
        """Replace all options. Each item is a ``str`` or a ``(text, value)`` pair."""
        self._options = []
        for it in items:
            if isinstance(it, (tuple, list)) and len(it) == 2:
                self.add_option(it[0], it[1])
            else:
                self.add_option(str(it))

    def set_value(self, value: object) -> None:
        for text, val in self._options:
            if val == value:
                self._value = val
                self._display.setText(text)
                self._field.set_populated(True)
                return

    def value(self) -> object:
        return self._value

    # -- enabled / icons ---------------------------------------------------

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self._display.setEnabled(self._enabled)
        self._sync_cursor()

    def set_menu_height(self, height: int) -> None:
        self._menu_height = int(height)

    def _sync_cursor(self) -> None:
        cursor = (
            Qt.CursorShape.IBeamCursor
            if self._enable_filter and self._enabled
            else Qt.CursorShape.PointingHandCursor
            if self._enabled
            else Qt.CursorShape.ArrowCursor
        )
        self._display.setCursor(cursor)

    # -- interaction -------------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        etype = event.type()
        if obj is self._field and etype == QEvent.Type.Resize:
            self._reposition_icons()
        elif etype == QEvent.Type.MouseButtonRelease and self._enabled:
            # When filtering, a click in the editable field shouldn't swallow
            # the caret placement; just (re)open the menu.
            self._open_menu()
            if not self._enable_filter:
                return True
        elif (
            self._enable_filter
            and obj is self._display
            and etype == QEvent.Type.KeyPress
            and self._menu is not None
            and not self._menu.isHidden()
        ):
            # Forward navigation keys to the (non-grabbing) options popup so the
            # field keeps the keyboard for typing. Returns True to consume.
            return self._forward_key(event)
        elif (
            self._enable_filter
            and obj is self._display
            and etype == QEvent.Type.FocusOut
        ):
            # Deferred: a click landing on a menu row first deactivates the
            # field window; a synchronous close would swallow its mouse-release.
            QTimer.singleShot(0, self._close_menu)
        return False

    def _forward_key(self, event: QEvent) -> bool:
        key = event.key()
        if key == Qt.Key.Key_Down:
            self._menu.highlight_next()
            return True
        if key == Qt.Key.Key_Up:
            self._menu.highlight_prev()
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return self._menu.activate_highlighted()
        if key == Qt.Key.Key_Escape:
            self._close_menu()
            return True
        return False

    def _reposition_icons(self) -> None:
        x = self._field.width() - _ARROW - 12
        y = int((56 - _ARROW) / 2)  # vertically center in the 56px box area
        self._arrow.move(max(0, x), max(0, y))
        self._arrow.raise_()
        if self._leading is not None:
            self._leading.move(12, max(0, y))
            self._leading.raise_()

    def _on_text_edited(self, text: str) -> None:
        # Reuse one persistent popup (rebuild rows in place) — never create a
        # new MdMenu per keystroke.
        self._filter_menu(text)

    def _ensure_menu(self) -> MdMenu:
        if self._menu is None:
            grabs = not self._enable_filter
            self._menu = MdMenu(
                self, max_height=self._menu_height, grabs_focus=grabs
            )
            self._menu.selected.connect(self._on_selected)
        return self._menu

    def _close_menu(self) -> None:
        if self._menu is not None:
            self._menu.close()

    def _filter_menu(self, query: str) -> None:
        menu = self._ensure_menu()
        q = query.casefold()
        menu.clear()
        any_match = False
        for text, _val in self._options:
            if q in text.casefold():
                menu.add_item(MdMenuItem(text))
                any_match = True
        if not any_match:
            menu.close()
            return
        menu.setFixedWidth(self._field.width())
        menu.open_at(self._field)

    def _open_menu(self) -> None:
        if not self._options:
            return
        menu = self._ensure_menu()
        menu.clear()
        for text, _val in self._options:
            menu.add_item(MdMenuItem(text))
        menu.setFixedWidth(self._field.width())
        menu.open_at(self._field)

    def _on_selected(self, text: str) -> None:
        for opt_text, val in self._options:
            if opt_text == text:
                self._value = val
                self._display.setText(opt_text)
                self._field.set_populated(True)
                self.changed.emit(val)
                return


class MdFilledSelect(_MdSelect):
    VARIANT = FieldVariant.FILLED


class MdOutlinedSelect(_MdSelect):
    VARIANT = FieldVariant.OUTLINED


__all__ = ["MdFilledSelect", "MdOutlinedSelect"]
