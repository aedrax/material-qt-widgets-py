"""Material 3 select for QtWidgets.

Ports Material Web's ``select/`` — filled and outlined selects. A select reuses
the :class:`MdField` chrome (label, indicator/outline, supporting text) showing
the chosen option, with a trailing dropdown arrow; clicking opens an
:class:`MdMenu` of options below it. Choosing an option updates the value and
emits ``changed(value)``.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Signal
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
        supporting_text: str = "",
    ) -> None:
        super().__init__(parent)
        self._options: list[tuple[str, object]] = []
        self._value: object = None

        self._field = MdField(
            variant=self.VARIANT, label=label, supporting_text=supporting_text
        )
        self._display = QLineEdit()
        self._display.setReadOnly(True)
        self._field.set_content(self._display)

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
        self._display.setCursor(Qt.CursorShape.PointingHandCursor)

    # -- options / value ---------------------------------------------------

    def add_option(self, text: str, value: object = None) -> None:
        self._options.append((text, text if value is None else value))

    def set_value(self, value: object) -> None:
        for text, val in self._options:
            if val == value:
                self._value = val
                self._display.setText(text)
                self._field.set_populated(True)
                return

    def value(self) -> object:
        return self._value

    # -- interaction -------------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._field and event.type() == QEvent.Type.Resize:
            self._reposition_arrow()
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._open_menu()
            return True
        return False

    def _reposition_arrow(self) -> None:
        x = self._field.width() - _ARROW - 12
        y = int((56 - _ARROW) / 2)  # vertically center in the 56px box area
        self._arrow.move(max(0, x), max(0, y))
        self._arrow.raise_()

    def _open_menu(self) -> None:
        if not self._options:
            return
        menu = MdMenu(self)
        for text, _val in self._options:
            menu.add_item(MdMenuItem(text))
        menu.selected.connect(self._on_selected)
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
