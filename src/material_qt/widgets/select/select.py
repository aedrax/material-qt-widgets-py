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

import time

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from ..field import FieldVariant, MdField
from ..icon import MdIcon
from ..menu import DropdownController

_ARROW = 24
# A press that dismisses the open popup is replayed to the field by Qt; its
# release must not immediately reopen the menu (QComboBox click-to-toggle).
_REOPEN_GRACE_S = 0.1


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
        self._visible_options: list[tuple[str, object]] = []
        self._hooked_menu = None
        self._menu_hidden_at = float("-inf")

        self._field = MdField(
            variant=self.VARIANT, label=label, supporting_text=supporting_text
        )
        self._display = QLineEdit()
        self._display.setReadOnly(not self._enable_filter)
        if hint_text:
            self._display.setPlaceholderText(hint_text)
        self._field.set_content(self._display)

        # Icons go into the field's slots so the inner edit and floating label
        # are inset to clear them (the field owns their placement).
        self._leading: MdIcon | None = None
        if self._leading_icon:
            self._leading = MdIcon(self._leading_icon)
            self._leading.set_size(_ARROW)
            self._field.set_leading(self._leading)

        # Trailing dropdown arrow in the field's trailing slot.
        self._arrow = MdIcon("arrow_drop_down")
        self._arrow.set_size(_ARROW)
        self._field.set_trailing(self._arrow)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._field)

        # Open the menu on a click anywhere in the field / display / arrow.
        for w in (self._field, self._display, self._arrow):
            w.installEventFilter(self)
        self._sync_cursor()

        # Shared options popup: grabbing for a plain select (it owns its own
        # keys), non-grabbing + keyboard-forwarded from the editable display
        # when filtering (with the top match auto-highlighted so Enter commits
        # it). Rows are committed by index (see _show_rows) so options with
        # duplicate display labels stay distinct.
        self._dropdown = DropdownController(
            self._field,
            key_source=self._display if self._enable_filter else None,
            max_height=self._menu_height,
            grabs_focus=not self._enable_filter,
            auto_highlight=self._enable_filter,
        )

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

    @property
    def _menu(self):  # noqa: ANN202  (the controller's popup, for callers/tests)
        return self._dropdown.menu

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        etype = event.type()
        if obj is self._hooked_menu and etype == QEvent.Type.Hide:
            # Remember when the popup closed: the press that dismissed it is
            # replayed to the field underneath and must not reopen the menu.
            self._menu_hidden_at = time.monotonic()
        elif etype == QEvent.Type.MouseButtonRelease and self._enabled:
            if time.monotonic() - self._menu_hidden_at < _REOPEN_GRACE_S:
                # This release belongs to the click that just dismissed the
                # popup — swallow the reopen (click-to-toggle, QComboBox-like).
                return not self._enable_filter
            # When filtering, a click in the editable field shouldn't swallow
            # the caret placement; just (re)open the menu. (Navigation keys and
            # outside-press dismissal are handled by the DropdownController.)
            self._open_menu()
            if not self._enable_filter:
                return True
        return False

    def _on_text_edited(self, text: str) -> None:
        self._filter_menu(text)

    def _filter_menu(self, query: str) -> None:
        q = query.casefold()
        self._show_rows(
            [(text, val) for text, val in self._options if q in text.casefold()]
        )

    def _open_menu(self) -> None:
        if not self._options:
            return
        self._show_rows(list(self._options))

    def _show_rows(self, rows: list[tuple[str, object]]) -> None:
        """(Re)open the popup with ``rows``, committing rows by index.

        Index-keyed commits keep options with duplicate display labels
        distinct (a label lookup would always resolve to the first).
        """
        self._visible_options = rows
        self._dropdown.show([text for text, _val in rows])
        menu = self._dropdown.menu
        if menu is None:
            return
        if menu is not self._hooked_menu:
            menu.installEventFilter(self)  # watch Hide for reopen suppression
            self._hooked_menu = menu
        if not menu.isHidden():
            # Rows were rebuilt by show(); bind each to its index.
            for index, item in enumerate(menu._items):
                item.triggered.connect(
                    lambda index=index: self._commit_index(index)
                )

    def _commit_index(self, index: int) -> None:
        if 0 <= index < len(self._visible_options):
            self._commit(*self._visible_options[index])

    def _commit(self, text: str, val: object) -> None:
        self._value = val
        self._display.setText(text)
        self._field.set_populated(True)
        self.changed.emit(val)

    def _on_selected(self, text: str) -> None:
        """Commit by display label (first match wins); prefer _commit_index."""
        for opt_text, val in self._options:
            if opt_text == text:
                self._commit(opt_text, val)
                return


class MdFilledSelect(_MdSelect):
    VARIANT = FieldVariant.FILLED


class MdOutlinedSelect(_MdSelect):
    VARIANT = FieldVariant.OUTLINED


__all__ = ["MdFilledSelect", "MdOutlinedSelect"]
