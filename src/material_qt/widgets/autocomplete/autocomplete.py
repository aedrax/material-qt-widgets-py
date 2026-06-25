"""Material 3 autocomplete for QtWidgets.

Ports Flutter's ``Autocomplete`` (``autocomplete.dart``): a text field that
shows a filtered dropdown of options as the user types. It composes an
:class:`MdField` (the chrome) with a ``QLineEdit`` for input and reuses the
existing :class:`MdMenu` surface for the options popup.

Properties (idiomatic QObject form):

* ``options`` — ``list[str]`` or arbitrary objects. ``set_options`` replaces them.
* ``display_string_for_option`` — callable mapping an option to its display text
  (defaults to ``str``); used both to render rows and to match the typed query.
* ``options_max_height`` — caps the popup height; it scrolls past that.
* ``initial_value`` — initial field text.
* ``selected(value)`` Signal — emits the chosen *option object* (Flutter
  ``onSelected``).
* ``textChanged(str)`` Signal — emits the field text on every keystroke.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from ..field import FieldVariant, MdField
from ..menu import MdMenu, MdMenuItem

_DEFAULT_MAX_HEIGHT = 200


class _MdAutocomplete(QWidget):
    """Base autocomplete; use a variant subclass."""

    VARIANT = FieldVariant.FILLED

    selected = Signal(object)  # emits the chosen option object
    textChanged = Signal(str)  # noqa: N815  (Qt-style signal name)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        options: Sequence[object] | None = None,
        label: str = "",
        placeholder: str = "",
        supporting_text: str = "",
        display_string_for_option: Callable[[object], str] | None = None,
        options_max_height: int = _DEFAULT_MAX_HEIGHT,
        initial_value: str = "",
    ) -> None:
        super().__init__(parent)
        self._options: list[object] = list(options) if options else []
        self._display_for = display_string_for_option or str
        self._options_max_height = int(options_max_height)
        self._menu: MdMenu | None = None
        # Maps the row display text -> option object for the currently open menu.
        self._row_options: dict[str, object] = {}

        self._field = MdField(
            variant=self.VARIANT, label=label, supporting_text=supporting_text
        )
        self._edit = QLineEdit()
        if placeholder:
            self._edit.setPlaceholderText(placeholder)
        self._field.set_content(self._edit)
        self._edit.textEdited.connect(self._on_text_edited)
        # Watch the input for navigation keys / focus-out so the non-grabbing
        # options popup can be driven without taking the keyboard.
        self._edit.installEventFilter(self)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._field)

        if initial_value:
            self.set_text(initial_value)

    # -- options -----------------------------------------------------------

    def set_options(self, options: Sequence[object]) -> None:
        self._options = list(options)

    def options(self) -> list[object]:
        return list(self._options)

    def set_display_string_for_option(self, fn: Callable[[object], str]) -> None:
        self._display_for = fn

    # -- text --------------------------------------------------------------

    def text(self) -> str:
        return self._edit.text()

    def set_text(self, value: str) -> None:
        self._edit.setText(value)
        self._field.set_populated(bool(value))

    @property
    def line_edit(self) -> QLineEdit:
        """The underlying input, for advanced configuration."""
        return self._edit

    # -- filtering / popup -------------------------------------------------

    def matching_options(self, query: str) -> list[object]:
        """Options whose display string contains ``query`` (case-insensitive)."""
        if not query:
            return list(self._options)
        q = query.casefold()
        return [o for o in self._options if q in self._display_for(o).casefold()]

    def _on_text_edited(self, text: str) -> None:
        self._field.set_populated(bool(text))
        self.textChanged.emit(text)
        matches = self.matching_options(text)
        if matches:
            self._show_menu(matches)
        else:
            self._close_menu()

    def _ensure_menu(self) -> MdMenu:
        if self._menu is None:
            # A non-grabbing popup: the keyboard stays on the line edit so the
            # user can keep typing while the options surface is shown.
            self._menu = MdMenu(
                self, max_height=self._options_max_height, grabs_focus=False
            )
            self._menu.selected.connect(self._on_selected)
        return self._menu

    def _close_menu(self) -> None:
        if self._menu is not None:
            self._menu.close()

    def _show_menu(self, options: list[object]) -> None:
        # Reuse one persistent popup; rebuild its rows in place each keystroke
        # so it resizes to the current matches without leaking windows.
        menu = self._ensure_menu()
        menu.clear()
        self._row_options = {}
        for opt in options:
            label = self._display_for(opt)
            self._row_options[label] = opt
            menu.add_item(MdMenuItem(label))
        menu.setFixedWidth(self._field.width())
        menu.open_at(self._field)
        # Auto-highlight the top match so Enter commits it without arrowing.
        menu.highlight_first()

    def _on_selected(self, label: str) -> None:
        option = self._row_options.get(label)
        self.set_text(label)
        self._close_menu()
        if option is not None:
            self.selected.emit(option)

    # -- keyboard ----------------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is not self._edit:
            return False
        etype = event.type()
        if (
            etype == QEvent.Type.KeyPress
            and self._menu is not None
            and not self._menu.isHidden()
        ):
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
        # The popup self-dismisses on an outside press (see MdMenu); we do NOT
        # close on the field's focus-out, which would race a row click's
        # mouse-release and swallow click-to-select.
        return False


class MdFilledAutocomplete(_MdAutocomplete):
    VARIANT = FieldVariant.FILLED


class MdOutlinedAutocomplete(_MdAutocomplete):
    VARIANT = FieldVariant.OUTLINED


# Default alias: the filled variant, matching Flutter's Material default.
MdAutocomplete = MdFilledAutocomplete


__all__ = ["MdAutocomplete", "MdFilledAutocomplete", "MdOutlinedAutocomplete"]
