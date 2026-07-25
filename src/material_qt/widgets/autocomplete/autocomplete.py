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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from ..field import FieldVariant, MdField
from ..menu import DropdownController

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
        # Options shown in the currently open menu, in row order. Rows are
        # committed by index so duplicate display labels stay distinct.
        self._row_options: list[object] = []

        self._field = MdField(
            variant=self.VARIANT, label=label, supporting_text=supporting_text
        )
        self._edit = QLineEdit()
        if placeholder:
            self._edit.setPlaceholderText(placeholder)
        self._field.set_content(self._edit)
        self._edit.textEdited.connect(self._on_text_edited)

        # The shared controller owns the non-grabbing options popup (anchored
        # under the field, keyboard-forwarded from the input, top-match
        # auto-highlighted). Rows are committed by index (see _on_text_edited).
        self._dropdown = DropdownController(
            self._field, key_source=self._edit,
            max_height=int(options_max_height), grabs_focus=False,
            auto_highlight=True,
        )

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

    @property
    def _menu(self):  # noqa: ANN202  (the controller's popup, for callers/tests)
        return self._dropdown.menu

    def _on_text_edited(self, text: str) -> None:
        self._field.set_populated(bool(text))
        self.textChanged.emit(text)
        matches = self.matching_options(text)
        # Keep the row-order options and (re)open the popup; show([]) closes.
        # Duplicate display labels each get their own row.
        self._row_options = list(matches)
        self._dropdown.show([self._display_for(o) for o in matches])
        menu = self._dropdown.menu
        if menu is not None and not menu.isHidden():
            # Rows were rebuilt by show(); bind each to its index.
            for index, item in enumerate(menu._items):
                item.triggered.connect(
                    lambda index=index: self._commit_index(index)
                )

    def _commit_index(self, index: int) -> None:
        if 0 <= index < len(self._row_options):
            option = self._row_options[index]
            self.set_text(self._display_for(option))
            self.selected.emit(option)

    def _on_selected(self, label: str) -> None:
        """Commit by display label (first match wins); prefer _commit_index."""
        option = next(
            (o for o in self._row_options if self._display_for(o) == label),
            None,
        )
        self.set_text(label)
        if option is not None:
            self.selected.emit(option)


class MdFilledAutocomplete(_MdAutocomplete):
    VARIANT = FieldVariant.FILLED


class MdOutlinedAutocomplete(_MdAutocomplete):
    VARIANT = FieldVariant.OUTLINED


# Default alias: the filled variant, matching Flutter's Material default.
MdAutocomplete = MdFilledAutocomplete


__all__ = ["MdAutocomplete", "MdFilledAutocomplete", "MdOutlinedAutocomplete"]
