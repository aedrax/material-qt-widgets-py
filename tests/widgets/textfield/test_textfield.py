"""Tests for Material text fields."""

from __future__ import annotations

from PySide6.QtWidgets import QLineEdit

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


def test_renders(qtbot):
    for cls in (MdFilledTextField, MdOutlinedTextField):
        tf = cls(label="Label", text="value", supporting_text="help")
        qtbot.addWidget(tf)
        tf.resize(tf.sizeHint())
        tf.grab()
