"""Material 3 text fields for QtWidgets.

Ports Material Web's ``textfield/`` (and Flutter's ``TextField`` /
``InputDecoration``) — filled and outlined text fields. Each composes an
:class:`MdField` (the chrome: floating label, active indicator / notched
outline, supporting text, error, leading/trailing icon slots, counter) with a
``QLineEdit`` (single-line) or ``QPlainTextEdit`` (multiline) for input.

Idiomatic QObject surface:

* callbacks → Qt Signals: ``textChanged(str)``, ``submitted(str)``.
* getters/setters: ``text()``/``set_text()``, ``set_error()``, ``set_enabled()``,
  ``set_read_only()``, ``set_placeholder()``, ``set_supporting_text()``.
* ``maxLines``/``minLines`` → ``max_lines``/``min_lines`` (multiline mode).
* ``prefixIcon``/``suffixIcon`` → ``leading_icon``/``trailing_icon``.
* ``obscureText`` → ``password`` (with a built-in visibility toggle).
* ``maxLength`` → ``max_length`` (with a live character counter, enforced).
* ``inputFormatters`` → ``set_validator`` (a :class:`QValidator`).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QTextCursor, QValidator
from PySide6.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...tokens.color import ColorRole
from ..field import FieldVariant, MdField
from ..icon import MdIcon

# A single text row is ~24px; each extra line adds roughly a line height. These
# match the field's single-line box (48) and grow from there for multiline.
_LINE_PX = 22


def _utf16_len(text: str) -> int:
    """Length in UTF-16 code units — the units ``QLineEdit.maxLength`` counts."""
    return len(text.encode("utf-16-le")) // 2


class _MdTextField(QWidget):
    """Base text field; use a variant subclass (filled/outlined)."""

    VARIANT = FieldVariant.FILLED

    textChanged = Signal(str)  # noqa: N815  (Qt-style signal name)
    submitted = Signal(str)  # noqa: N815  (fires on Enter / editing complete)

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
        enabled: bool = True,
        read_only: bool = False,
        max_length: int = 0,
        max_lines: int = 1,
        min_lines: int = 1,
        leading_icon: str = "",
        trailing_icon: str = "",
        validator: QValidator | None = None,
    ) -> None:
        super().__init__(parent)
        if password and max_lines != 1:
            # Mirror Flutter's assert: obscured fields cannot be multiline.
            raise ValueError("password fields cannot be multiline (max_lines must be 1)")
        if password and trailing_icon:
            # The trailing slot is owned by the password visibility toggle.
            raise ValueError("password fields cannot also set a trailing_icon")
        if int(min_lines) > int(max_lines):
            raise ValueError("min_lines cannot be greater than max_lines")

        self._password = bool(password)
        self._password_visible = False
        self._label = label
        self._placeholder = placeholder
        # (position, chars added) of the last document insertion, in UTF-16
        # units — used to reject the overflowing part of a multiline edit.
        self._last_insert: tuple[int, int] | None = None
        self._max_length = max(0, int(max_length))
        self._max_lines = max(1, int(max_lines))
        self._min_lines = max(1, min(int(min_lines), self._max_lines))
        self._multiline = self._max_lines > 1
        self._toggle: MdIcon | None = None

        box_h = None
        if self._multiline:
            box_h = 48 + (self._min_lines - 1) * _LINE_PX
        self._field = MdField(
            variant=self.VARIANT,
            label=label,
            supporting_text=supporting_text,
            error=error,
            multiline_box_height=box_h,
        )

        # Pick the content-widget type once, from max_lines.
        if self._multiline:
            self._edit = self._build_multiline()
        else:
            self._edit = self._build_singleline()

        self._field.set_content(self._edit)
        # Track focus to toggle the placeholder with the floating label (M3:
        # the placeholder only shows once the label has floated out of the way).
        self._edit.installEventFilter(self)
        self._sync_placeholder(focused=False)

        if leading_icon:
            self.set_leading_icon(leading_icon)
        if trailing_icon:
            self.set_trailing_icon(trailing_icon)
        elif self._password:
            self._install_password_toggle()

        if validator is not None and not self._multiline:
            self._edit.setValidator(validator)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._field)

        self.set_enabled(enabled)
        self.set_read_only(read_only)

        if text:
            self.set_text(text)
        self._update_counter()

    # -- content builders --------------------------------------------------

    def _build_singleline(self) -> QLineEdit:
        edit = QLineEdit()
        if self._password:
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        if self._max_length:
            edit.setMaxLength(self._max_length)  # QLineEdit hard-enforces the cap.
        edit.textChanged.connect(self._on_text_changed)
        edit.returnPressed.connect(lambda: self.submitted.emit(self.text()))
        return edit

    def _build_multiline(self) -> QPlainTextEdit:
        edit = QPlainTextEdit()
        # Track where text is inserted so max_length can reject the overflow.
        edit.document().contentsChange.connect(self._on_contents_change)
        # QPlainTextEdit.textChanged emits no argument; adapt to read the value.
        edit.textChanged.connect(lambda: self._on_text_changed(self.text()))
        return edit

    # -- value -------------------------------------------------------------

    def _on_contents_change(self, position: int, removed: int, added: int) -> None:
        if added > 0:
            self._last_insert = (position, added)

    def _on_text_changed(self, value: str) -> None:
        # QPlainTextEdit has no maxLength; enforce the cap ourselves so the
        # counter never lies about the limit.
        if self._multiline and self._max_length and self._enforce_max_length():
            value = self.text()
        self._field.set_populated(bool(value))
        self._update_counter()
        self.textChanged.emit(value)

    def _enforce_max_length(self) -> bool:
        """Reject the overflowing part of the last insertion (QLineEdit-style).

        Only the newly inserted characters past the cap are removed — never the
        document tail — and the removal joins the insertion's undo block so
        undo keeps working. Returns True when text was trimmed.
        """
        doc = self._edit.document()
        # characterCount() counts UTF-16 units (QString), incl. a final null.
        over = (doc.characterCount() - 1) - self._max_length
        if over <= 0 or self._last_insert is None:
            return False
        pos, added = self._last_insert
        # Whole-document changes (setPlainText) report charsAdded including
        # the terminal block char; clamp to the last real position.
        end = min(pos + added, doc.characterCount() - 1)
        trim = min(over, end - pos)
        if trim <= 0:
            return False
        start = end - trim
        # Never cut a surrogate pair in half: back up over a low surrogate.
        ch = doc.characterAt(start)
        if ch and 0xDC00 <= ord(ch) <= 0xDFFF:
            start -= 1
        cursor = QTextCursor(doc)
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self._edit.blockSignals(True)  # re-emit once, with the trimmed value
        try:
            cursor.joinPreviousEditBlock()
            cursor.removeSelectedText()
            cursor.endEditBlock()
        finally:
            self._edit.blockSignals(False)
        return True

    def text(self) -> str:
        if self._multiline:
            return self._edit.toPlainText()
        return self._edit.text()

    def set_text(self, value: str) -> None:
        if self._multiline:
            self._edit.setPlainText(value)
        else:
            self._edit.setText(value)

    @property
    def line_edit(self) -> QWidget:
        """The underlying input widget, for advanced configuration."""
        return self._edit

    @property
    def field(self) -> MdField:
        """The underlying field chrome."""
        return self._field

    # -- character counter -------------------------------------------------

    def _update_counter(self) -> None:
        if not self._max_length:
            return
        # Count UTF-16 units so the counter matches what maxLength enforces
        # (an emoji outside the BMP counts as 2, exactly as QLineEdit sees it).
        self._field.set_counter(f"{_utf16_len(self.text())}/{self._max_length}")

    def max_length(self) -> int:
        return self._max_length

    # -- state -------------------------------------------------------------

    def set_error(self, error: bool) -> None:
        self._field.set_error(error)

    def set_supporting_text(self, text: str) -> None:
        self._field.set_supporting_text(text)

    def set_placeholder(self, text: str) -> None:
        self._placeholder = text
        self._sync_placeholder()

    def _sync_placeholder(self, focused: bool | None = None) -> None:
        # M3: with a label, the placeholder shows only while the label is
        # floated (focused); otherwise the resting label would overlap it.
        if focused is None:
            focused = self._edit.hasFocus()
        show = focused or not self._label
        self._edit.setPlaceholderText(self._placeholder if show else "")

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._edit:
            if event.type() == QEvent.Type.FocusIn:
                self._sync_placeholder(focused=True)
            elif event.type() == QEvent.Type.FocusOut:
                self._sync_placeholder(focused=False)
        return super().eventFilter(obj, event)

    def set_enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        self.setEnabled(enabled)
        self._edit.setEnabled(enabled)
        self._field.setEnabled(enabled)

    def set_read_only(self, read_only: bool) -> None:
        self._edit.setReadOnly(bool(read_only))

    def is_read_only(self) -> bool:
        return self._edit.isReadOnly()

    def set_validator(self, validator: QValidator | None) -> None:
        """Set a :class:`QValidator` (the idiomatic Qt input formatter)."""
        if self._multiline:
            return  # QPlainTextEdit has no validator hook.
        self._edit.setValidator(validator)

    # -- icon slots --------------------------------------------------------

    def set_leading_icon(self, name: str) -> None:
        if not name:
            self._field.set_leading(None)
            return
        icon = MdIcon(name, color_role=ColorRole.ON_SURFACE_VARIANT)
        icon.set_size(24)
        self._field.set_leading(icon)

    def set_trailing_icon(self, name: str) -> None:
        # Replacing the trailing slot retires any password toggle that lived
        # there: drop our (now-deleted) reference and restore the obscured echo.
        if self._toggle is not None:
            self._toggle = None
            self._password_visible = False
            if self._password and not self._multiline:
                self._edit.setEchoMode(QLineEdit.EchoMode.Password)
        if not name:
            self._field.set_trailing(None)
            return
        icon = MdIcon(name, color_role=ColorRole.ON_SURFACE_VARIANT)
        icon.set_size(24)
        self._field.set_trailing(icon)

    # -- password visibility toggle ---------------------------------------

    def _install_password_toggle(self) -> None:
        toggle = MdIcon("visibility", color_role=ColorRole.ON_SURFACE_VARIANT)
        toggle.set_size(24)
        toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle.mousePressEvent = self._on_toggle_clicked  # type: ignore[method-assign]
        self._toggle = toggle
        self._field.set_trailing(toggle)

    def _on_toggle_clicked(self, _event) -> None:
        self._password_visible = not self._password_visible
        mode = (
            QLineEdit.EchoMode.Normal
            if self._password_visible
            else QLineEdit.EchoMode.Password
        )
        self._edit.setEchoMode(mode)
        if self._toggle is not None:
            self._toggle.set_name(
                "visibility_off" if self._password_visible else "visibility"
            )

    @property
    def password_visible(self) -> bool:
        return self._password_visible


class MdFilledTextField(_MdTextField):
    VARIANT = FieldVariant.FILLED


class MdOutlinedTextField(_MdTextField):
    VARIANT = FieldVariant.OUTLINED


__all__ = ["MdFilledTextField", "MdOutlinedTextField"]
