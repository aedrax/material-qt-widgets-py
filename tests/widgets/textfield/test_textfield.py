"""Tests for Material text fields."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFocusEvent, QIntValidator, QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit, QPlainTextEdit

from material_qt.widgets.field import FieldVariant
from material_qt.widgets.textfield import MdFilledTextField, MdOutlinedTextField


def test_text_roundtrip_and_signal(qtbot):
    tf = MdFilledTextField(label="Name")
    qtbot.addWidget(tf)
    seen = []
    tf.textChanged.connect(seen.append)
    tf.set_text("hello")
    assert tf.text() == "hello"
    assert seen[-1] == "hello"


def test_populated_floats_on_text(qtbot):
    tf = MdFilledTextField(label="Name")
    qtbot.addWidget(tf)
    assert tf._field._should_float() is False
    tf.set_text("x")
    assert tf._field._should_float() is True


def test_variants(qtbot):
    f = MdFilledTextField()
    o = MdOutlinedTextField()
    for t in (f, o):
        qtbot.addWidget(t)
    assert f._field.variant == FieldVariant.FILLED
    assert o._field.variant == FieldVariant.OUTLINED


def test_password_mode(qtbot):
    tf = MdFilledTextField(label="Password", password=True)
    qtbot.addWidget(tf)
    assert tf.line_edit.echoMode() == QLineEdit.EchoMode.Password


def test_submitted_signal(qtbot):
    tf = MdFilledTextField(label="Search")
    qtbot.addWidget(tf)
    seen = []
    tf.submitted.connect(seen.append)
    tf.set_text("query")
    tf.line_edit.returnPressed.emit()
    assert seen == ["query"]


def test_multiline_mode(qtbot):
    tf = MdFilledTextField(label="Notes", max_lines=4, min_lines=2)
    qtbot.addWidget(tf)
    assert isinstance(tf.line_edit, QPlainTextEdit)
    seen = []
    tf.textChanged.connect(seen.append)
    tf.set_text("line1\nline2")
    assert tf.text() == "line1\nline2"
    assert seen[-1] == "line1\nline2"
    assert tf._field._should_float() is True


def test_multiline_box_taller_than_single(qtbot):
    single = MdFilledTextField(label="x")
    multi = MdFilledTextField(label="x", max_lines=5, min_lines=3)
    for t in (single, multi):
        qtbot.addWidget(t)
    assert multi.sizeHint().height() > single.sizeHint().height()


def test_password_cannot_be_multiline(qtbot):
    with pytest.raises(ValueError):
        MdFilledTextField(password=True, max_lines=3)


def test_min_lines_cannot_exceed_max_lines(qtbot):
    with pytest.raises(ValueError):
        MdFilledTextField(min_lines=5, max_lines=2)


def test_password_with_trailing_icon_rejected(qtbot):
    with pytest.raises(ValueError):
        MdFilledTextField(password=True, trailing_icon="clear")


def test_max_length_and_counter(qtbot):
    tf = MdFilledTextField(label="Code", max_length=5)
    qtbot.addWidget(tf)
    assert tf.line_edit.maxLength() == 5
    tf.set_text("abc")
    assert tf._field._counter == "3/5"


def test_multiline_max_length_enforced(qtbot):
    tf = MdFilledTextField(label="Bio", max_lines=3, max_length=4)
    qtbot.addWidget(tf)
    tf.set_text("abcdefgh")
    assert tf.text() == "abcd"
    assert tf._field._counter == "4/4"


def _put_cursor(edit: QPlainTextEdit, pos: int) -> None:
    cursor = edit.textCursor()
    cursor.setPosition(pos)
    edit.setTextCursor(cursor)


def test_multiline_full_field_rejects_insertion_keeps_tail(qtbot):
    # Pasting into the middle of a FULL field must reject the paste — not
    # silently eat the end of the existing text.
    tf = MdFilledTextField(label="Bio", max_lines=3, max_length=4)
    qtbot.addWidget(tf)
    tf.set_text("abcd")
    _put_cursor(tf.line_edit, 2)
    tf.line_edit.insertPlainText("XY")
    assert tf.text() == "abcd"
    assert tf._field._counter == "4/4"


def test_multiline_overflow_trims_insertion_not_tail(qtbot):
    # A mid-document paste into a nearly-full field keeps the tail and trims
    # only the inserted text.
    tf = MdFilledTextField(label="Bio", max_lines=3, max_length=4)
    qtbot.addWidget(tf)
    tf.set_text("abc")
    _put_cursor(tf.line_edit, 1)
    tf.line_edit.insertPlainText("XY")
    assert tf.text() == "aXbc"


def test_multiline_undo_survives_max_length_trim(qtbot):
    tf = MdFilledTextField(label="Bio", max_lines=3, max_length=4)
    qtbot.addWidget(tf)
    edit = tf.line_edit
    edit.clear()  # start with an undo-enabled, empty document
    QTest.keyClicks(edit, "abcd")
    QTest.keyClicks(edit, "e")  # rejected by the limit
    assert tf.text() == "abcd"
    # The old setPlainText() rewrite wiped the undo stack entirely.
    assert edit.document().isUndoAvailable()
    edit.undo()
    assert "e" not in tf.text()  # never resurrects the rejected char


def test_counter_counts_utf16_units_singleline(qtbot):
    tf = MdFilledTextField(label="Emoji", max_length=4)
    qtbot.addWidget(tf)
    tf.set_text("\U0001f600\U0001f600")  # 2 code points, 4 UTF-16 units
    # QLineEdit.maxLength counts UTF-16 units — the counter must agree
    # (the old code-point count read "2/4" forever).
    assert tf._field._counter == "4/4"
    tf.line_edit.insert("x")  # at the cap: further input rejected
    assert tf.text() == "\U0001f600\U0001f600"


def test_multiline_max_length_counts_utf16_units(qtbot):
    tf = MdFilledTextField(label="Emoji", max_lines=3, max_length=4)
    qtbot.addWidget(tf)
    tf.set_text("\U0001f600\U0001f600")
    assert tf.text() == "\U0001f600\U0001f600"
    assert tf._field._counter == "4/4"
    tf.line_edit.moveCursor(QTextCursor.MoveOperation.End)
    tf.line_edit.insertPlainText("\U0001f600")  # would exceed: rejected whole
    assert tf.text() == "\U0001f600\U0001f600"
    assert tf._field._counter == "4/4"


def test_multiline_max_length_never_splits_surrogate_pair(qtbot):
    tf = MdFilledTextField(label="Emoji", max_lines=3, max_length=5)
    qtbot.addWidget(tf)
    tf.set_text("\U0001f600\U0001f600")  # 4 units; 1 unit of room left
    tf.line_edit.moveCursor(QTextCursor.MoveOperation.End)
    tf.line_edit.insertPlainText("\U0001f600")  # 2 units: can't fit half
    assert tf.text() == "\U0001f600\U0001f600"


def test_password_toggle_real_click(qtbot):
    tf = MdFilledTextField(label="Password", password=True)
    qtbot.addWidget(tf)
    tf.show()
    qtbot.waitExposed(tf)
    assert tf._toggle is not None
    assert tf.line_edit.echoMode() == QLineEdit.EchoMode.Password
    QTest.mouseClick(tf._toggle, Qt.MouseButton.LeftButton)
    assert tf.password_visible is True
    assert tf.line_edit.echoMode() == QLineEdit.EchoMode.Normal
    QTest.mouseClick(tf._toggle, Qt.MouseButton.LeftButton)
    assert tf.line_edit.echoMode() == QLineEdit.EchoMode.Password


def test_set_trailing_icon_retires_password_toggle(qtbot):
    tf = MdFilledTextField(label="Password", password=True)
    qtbot.addWidget(tf)
    tf._on_toggle_clicked(None)  # reveal
    assert tf.line_edit.echoMode() == QLineEdit.EchoMode.Normal
    tf.set_trailing_icon("clear")  # replace the toggle slot
    assert tf._toggle is None
    # Echo restored to obscured now that the toggle is gone.
    assert tf.line_edit.echoMode() == QLineEdit.EchoMode.Password


def test_leading_and_trailing_icons(qtbot):
    tf = MdOutlinedTextField(label="Email", leading_icon="mail", trailing_icon="clear")
    qtbot.addWidget(tf)
    assert tf._field._leading is not None
    assert tf._field._trailing is not None
    tf.resize(tf.sizeHint())
    tf.grab()


def test_validator(qtbot):
    tf = MdFilledTextField(label="Age", validator=QIntValidator(0, 120))
    qtbot.addWidget(tf)
    assert tf.line_edit.validator() is not None


def test_enabled_and_read_only(qtbot):
    tf = MdFilledTextField(label="x", enabled=False, read_only=True)
    qtbot.addWidget(tf)
    assert tf.isEnabled() is False
    assert tf.is_read_only() is True
    tf.set_enabled(True)
    assert tf.isEnabled() is True


def _send_focus(edit, event_type):
    QApplication.sendEvent(edit, QFocusEvent(event_type))


def test_placeholder_hidden_while_label_rests(qtbot):
    # M3: label + placeholder, unfocused + empty → only the resting label
    # shows; the inner edit must not paint the placeholder underneath it.
    tf = MdFilledTextField(label="Name", placeholder="Jane Doe")
    qtbot.addWidget(tf)
    assert tf.line_edit.placeholderText() == ""
    _send_focus(tf.line_edit, QEvent.Type.FocusIn)  # label floats
    assert tf.line_edit.placeholderText() == "Jane Doe"
    _send_focus(tf.line_edit, QEvent.Type.FocusOut)  # label rests again
    assert tf.line_edit.placeholderText() == ""


def test_placeholder_shown_without_label(qtbot):
    tf = MdFilledTextField(placeholder="Search")
    qtbot.addWidget(tf)
    assert tf.line_edit.placeholderText() == "Search"
    tf.set_placeholder("Find")
    assert tf.line_edit.placeholderText() == "Find"


def test_set_placeholder_respects_resting_label(qtbot):
    tf = MdFilledTextField(label="Name", max_lines=3)
    qtbot.addWidget(tf)
    tf.set_placeholder("Jane Doe")
    assert tf.line_edit.placeholderText() == ""
    _send_focus(tf.line_edit, QEvent.Type.FocusIn)
    assert tf.line_edit.placeholderText() == "Jane Doe"


def test_renders(qtbot):
    for cls in (MdFilledTextField, MdOutlinedTextField):
        tf = cls(label="Label", text="value", supporting_text="help")
        qtbot.addWidget(tf)
        tf.resize(tf.sizeHint())
        tf.grab()
    # Multiline + counter + icons render too.
    multi = MdOutlinedTextField(
        label="Bio", max_lines=4, min_lines=2, max_length=200,
        leading_icon="person", supporting_text="Tell us about yourself",
    )
    qtbot.addWidget(multi)
    multi.set_text("hello\nworld")
    multi.resize(multi.sizeHint())
    multi.grab()
