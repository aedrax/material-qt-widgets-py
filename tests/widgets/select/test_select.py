"""Tests for MdFilledSelect / MdOutlinedSelect."""

from __future__ import annotations

from material_qt.widgets.field import FieldVariant
from material_qt.widgets.select import MdFilledSelect, MdOutlinedSelect


def test_add_options_and_set_value(qtbot):
    s = MdFilledSelect(label="Fruit")
    qtbot.addWidget(s)
    for f in ("Apple", "Banana"):
        s.add_option(f)
    s.set_value("Banana")
    assert s.value() == "Banana"
    assert s._display.text() == "Banana"
    assert s._field._should_float() is True


def test_custom_values(qtbot):
    s = MdFilledSelect()
    qtbot.addWidget(s)
    s.add_option("One", 1)
    s.add_option("Two", 2)
    s.set_value(2)
    assert s.value() == 2
    assert s._display.text() == "Two"


def test_on_selected_emits_changed(qtbot):
    s = MdFilledSelect()
    qtbot.addWidget(s)
    s.add_option("Apple")
    seen = []
    s.changed.connect(seen.append)
    s._on_selected("Apple")
    assert seen == ["Apple"]
    assert s.value() == "Apple"


def test_variants(qtbot):
    f = MdFilledSelect()
    o = MdOutlinedSelect()
    for s in (f, o):
        qtbot.addWidget(s)
    assert f._field.variant == FieldVariant.FILLED
    assert o._field.variant == FieldVariant.OUTLINED


def test_renders(qtbot):
    for cls in (MdFilledSelect, MdOutlinedSelect):
        s = cls(label="Pick")
        qtbot.addWidget(s)
        s.add_option("A")
        s.set_value("A")
        s.resize(280, s.sizeHint().height())
        s.grab()
