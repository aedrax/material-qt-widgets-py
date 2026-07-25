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


def test_items_and_value_kwargs(qtbot):
    s = MdFilledSelect(items=["A", ("Two", 2), "C"], value=2)
    qtbot.addWidget(s)
    assert s.value() == 2
    assert s._display.text() == "Two"


def test_set_options_replaces(qtbot):
    s = MdFilledSelect()
    qtbot.addWidget(s)
    s.set_options(["A", "B"])
    s.set_options(["C"])
    assert len(s._options) == 1
    assert s._options[0][0] == "C"


def test_hint_text_sets_placeholder(qtbot):
    s = MdFilledSelect(hint_text="Choose one")
    qtbot.addWidget(s)
    assert s._display.placeholderText() == "Choose one"


def test_enabled_toggle(qtbot):
    s = MdFilledSelect(enabled=False)
    qtbot.addWidget(s)
    assert s.is_enabled() is False
    s.set_enabled(True)
    assert s.is_enabled() is True


def test_leading_icon_created(qtbot):
    s = MdFilledSelect(leading_icon="search")
    qtbot.addWidget(s)
    assert s._leading is not None


def test_enable_filter_makes_editable(qtbot):
    s = MdFilledSelect(items=["Apple", "Banana", "Cherry"], enable_filter=True)
    qtbot.addWidget(s)
    assert s._display.isReadOnly() is False
    s._on_text_edited("an")
    assert s._menu is not None
    texts = [it.text for it in s._menu._items]
    assert texts == ["Banana"]
    s._menu.close()


def test_filter_menu_is_non_grabbing(qtbot):
    # The filter popup must not grab the keyboard away from the editable field.
    s = MdFilledSelect(items=["Apple", "Banana"], enable_filter=True)
    qtbot.addWidget(s)
    s._on_text_edited("a")
    assert s._menu is not None
    assert s._menu._grabs_focus is False


def test_filter_reuses_single_menu(qtbot):
    s = MdFilledSelect(items=["Apple", "Apricot", "Banana"], enable_filter=True)
    qtbot.addWidget(s)
    s._on_text_edited("A")
    m1 = s._menu
    s._on_text_edited("Ap")
    assert s._menu is m1
    assert [it.text for it in s._menu._items] == ["Apple", "Apricot"]
    s._menu.close()


def test_readonly_select_menu_grabs(qtbot):
    # A non-filtering select uses the standard grabbing Qt.Popup menu.
    s = MdFilledSelect(items=["Apple", "Banana"])
    qtbot.addWidget(s)
    s._open_menu()
    assert s._menu is not None
    assert s._menu._grabs_focus is True
    s._menu.close()


def _click(widget):
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QApplication

    center = QPointF(widget.rect().center())
    for et in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
        QApplication.sendEvent(widget, QMouseEvent(
            et, center, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier))


def test_replayed_click_after_popup_close_does_not_reopen(qtbot):
    # Regression: pressing the select while its menu is open closes the popup
    # (outside press) and Qt replays the press to the field; the release must
    # NOT immediately reopen the menu (QComboBox click-to-toggle behaviour).
    s = MdFilledSelect(items=["Apple", "Banana"])
    qtbot.addWidget(s)
    s._open_menu()
    menu = s._menu
    assert not menu.isHidden()
    # The outside press dismisses the grabbing popup...
    menu.close()
    # ...and Qt replays press+release to the field underneath.
    _click(s._display)
    assert menu.isHidden()


def test_click_after_grace_period_reopens(qtbot):
    s = MdFilledSelect(items=["Apple", "Banana"])
    qtbot.addWidget(s)
    s._open_menu()
    menu = s._menu
    menu.close()
    qtbot.wait(150)  # past the replay-suppression window
    _click(s._display)
    assert not menu.isHidden()
    menu.close()


def test_leading_icon_insets_edit(qtbot):
    # Regression: the leading icon used to be a raw overlay painted over the
    # text. It must live in the field's leading slot, with the edit inset past
    # it (and past the trailing arrow on the right).
    s = MdFilledSelect(label="Pick", leading_icon="search")
    qtbot.addWidget(s)
    s.resize(280, s.sizeHint().height())
    s.grab()  # force a layout pass
    assert s._leading.parent() is s._field
    assert s._arrow.parent() is s._field
    assert s._display.geometry().left() >= s._leading.geometry().right()
    assert s._display.geometry().right() <= s._arrow.geometry().left()


def test_filter_enter_commits_top_match(qtbot):
    # Regression: the filterable select must auto-highlight the top match so
    # Enter commits it without pressing Down first.
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    s = MdFilledSelect(items=["Apple", "Banana", "Cherry"], enable_filter=True)
    qtbot.addWidget(s)
    seen = []
    s.changed.connect(seen.append)
    s._on_text_edited("an")
    assert s._menu._highlight == 0
    QApplication.sendEvent(s._display, QKeyEvent(
        QEvent.Type.KeyPress, Qt.Key.Key_Return,
        Qt.KeyboardModifier.NoModifier))
    assert seen == ["Banana"]
    assert s.value() == "Banana"
    assert s._display.text() == "Banana"


def test_duplicate_labels_select_distinct_values(qtbot):
    # Regression: options were committed by display label, so two options with
    # the same label always resolved to the first one's value.
    s = MdFilledSelect(items=[("Dup", 1), ("Dup", 2)])
    qtbot.addWidget(s)
    seen = []
    s.changed.connect(seen.append)
    s._open_menu()
    assert len(s._menu._items) == 2
    s._menu._items[1].triggered.emit()
    assert s.value() == 2
    assert seen == [2]
    assert s._menu.isHidden()
