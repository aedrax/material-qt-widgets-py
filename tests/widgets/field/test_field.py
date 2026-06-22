"""Tests for MdField."""

from __future__ import annotations

from PySide6.QtWidgets import QLineEdit

from material_qt.widgets.field import FieldVariant, MdField


def test_populated_floats_label(qtbot):
    f = MdField(label="Name")
    qtbot.addWidget(f)
    assert f._should_float() is False
    f.set_populated(True)
    assert f._should_float() is True


def test_focus_floats_label(qtbot):
    f = MdField(label="Name")
    qtbot.addWidget(f)
    edit = QLineEdit()
    f.set_content(edit)
    f.show()
    f._focused = True  # simulate the FocusIn the event filter would set
    f._sync_float()
    assert f._should_float() is True


def test_variant_and_supporting_height(qtbot):
    plain = MdField(label="x")
    with_support = MdField(label="x", supporting_text="help")
    for f in (plain, with_support):
        qtbot.addWidget(f)
    assert with_support.sizeHint().height() > plain.sizeHint().height()
    assert MdField(variant=FieldVariant.OUTLINED).variant == FieldVariant.OUTLINED


def test_leading_trailing_slots(qtbot):
    f = MdField(label="x")
    qtbot.addWidget(f)
    f.set_content(QLineEdit())
    assert f._leading is None and f._trailing is None
    lead = QLineEdit()
    f.set_leading(lead)
    assert f._leading is lead
    f.set_leading(None)
    assert f._leading is None


def test_counter_adds_support_row(qtbot):
    plain = MdField(label="x")
    counted = MdField(label="x")
    counted.set_counter("3/10")
    for f in (plain, counted):
        qtbot.addWidget(f)
    assert counted.sizeHint().height() > plain.sizeHint().height()


def test_multiline_box_height(qtbot):
    single = MdField(label="x")
    tall = MdField(label="x", multiline_box_height=100)
    for f in (single, tall):
        qtbot.addWidget(f)
    assert tall.sizeHint().height() > single.sizeHint().height()


def test_renders(qtbot):
    for variant in FieldVariant:
        for err in (False, True):
            f = MdField(variant=variant, label="Label",
                        supporting_text="Help", error=err)
            qtbot.addWidget(f)
            f.set_content(QLineEdit())
            f.set_counter("5/10")
            f.resize(f.sizeHint())
            f.grab()
