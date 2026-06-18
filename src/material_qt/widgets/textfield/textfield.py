"""Material 3 text fields for QtWidgets.

Ports Material Web's ``textfield/`` — filled and outlined single-line text
fields. Each composes an :class:`MdField` (the chrome: floating label, active
indicator / notched outline, supporting text, error) with a ``QLineEdit`` for
input. Exposes ``text``/``set_text``, ``placeholder``, ``error``, password mode,
and a ``textChanged`` signal.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from ..field import FieldVariant, MdField


class _MdTextField(QWidget):
    """Base single-line text field; use a variant subclass."""

    VARIANT = FieldVariant.FILLED

    textChanged = Signal(str)  # noqa: N815  (Qt-style signal name)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        label: str = "",
        text: str = "",
        placeholder: str = "",
        supporting_text: str = "",
        error: bool = False,
        password: bool = False,
    ) -> None:
        super().__init__(parent)
        self._field = MdField(
            variant=self.VARIANT,
            label=label,
            supporting_text=supporting_text,
            error=error,
        )
        self._edit = QLineEdit()
        if placeholder:
            self._edit.setPlaceholderText(placeholder)
        if password:
            self._edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._field.set_content(self._edit)
        self._edit.textChanged.connect(self._on_text_changed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._field)

        if text:
            self.set_text(text)

    # -- value -------------------------------------------------------------

    def _on_text_changed(self, value: str) -> None:
        self._field.set_populated(bool(value))
        self.textChanged.emit(value)

    def text(self) -> str:
        return self._edit.text()

    def set_text(self, value: str) -> None:
        self._edit.setText(value)

    @property
    def line_edit(self) -> QLineEdit:
        """The underlying input, for advanced configuration."""
        return self._edit

    # -- passthroughs ------------------------------------------------------

    def set_error(self, error: bool) -> None:
        self._field.set_error(error)

    def set_placeholder(self, text: str) -> None:
        self._edit.setPlaceholderText(text)


class MdFilledTextField(_MdTextField):
    VARIANT = FieldVariant.FILLED


class MdOutlinedTextField(_MdTextField):
    VARIANT = FieldVariant.OUTLINED


__all__ = ["MdFilledTextField", "MdOutlinedTextField"]
