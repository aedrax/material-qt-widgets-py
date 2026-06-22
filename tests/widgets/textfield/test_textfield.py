"""Tests for Material text fields."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit

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
