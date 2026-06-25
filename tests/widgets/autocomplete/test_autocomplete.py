"""Tests for MdAutocomplete."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from material_qt.widgets.autocomplete import (
    MdAutocomplete,
    MdFilledAutocomplete,
    MdOutlinedAutocomplete,
)
from material_qt.widgets.field import FieldVariant


def test_options_and_filter(qtbot):
    a = MdAutocomplete(options=["Apple", "Banana", "Cherry"])
    qtbot.addWidget(a)
    assert a.options() == ["Apple", "Banana", "Cherry"]
    assert a.matching_options("an") == ["Banana"]
    assert a.matching_options("") == ["Apple", "Banana", "Cherry"]
    assert a.matching_options("z") == []


def test_initial_value_populates(qtbot):
    a = MdAutocomplete(options=["Apple"], initial_value="Apple")
    qtbot.addWidget(a)
    assert a.text() == "Apple"
    assert a._field._should_float() is True


def test_text_changed_signal(qtbot):
    a = MdAutocomplete(options=["Apple", "Apricot"])
    qtbot.addWidget(a)
    seen = []
    a.textChanged.connect(seen.append)
    a._on_text_edited("Ap")
    assert seen == ["Ap"]


def test_selected_emits_option_object(qtbot):
    opts = [{"id": 1, "name": "Apple"}, {"id": 2, "name": "Banana"}]
    a = MdAutocomplete(
        options=opts, display_string_for_option=lambda o: o["name"]
    )
    qtbot.addWidget(a)
    picked = []
    a.selected.connect(picked.append)
    # Open the popup, then choose a row by its display label.
    a._on_text_edited("Ban")
    a._on_selected("Banana")
    assert picked == [{"id": 2, "name": "Banana"}]
    assert a.text() == "Banana"


def test_display_string_for_option_used_in_filter(qtbot):
    opts = [{"name": "Apple"}, {"name": "Banana"}]
    a = MdAutocomplete(
        options=opts, display_string_for_option=lambda o: o["name"]
    )
    qtbot.addWidget(a)
    assert a.matching_options("app") == [{"name": "Apple"}]


def test_no_match_no_menu(qtbot):
    a = MdAutocomplete(options=["Apple"])
    qtbot.addWidget(a)
    a._on_text_edited("zzz")
    # No popup opened for an empty match set.
    assert a._menu is None or a._menu.isHidden()


def test_variants(qtbot):
    f = MdFilledAutocomplete()
    o = MdOutlinedAutocomplete()
    for a in (f, o):
        qtbot.addWidget(a)
    assert f._field.variant == FieldVariant.FILLED
    assert o._field.variant == FieldVariant.OUTLINED


def test_renders(qtbot):
    a = MdAutocomplete(options=["Apple", "Banana"], label="Fruit")
    qtbot.addWidget(a)
    a.resize(280, a._field.sizeHint().height())
    assert a.grab() is not None


def test_popup_is_non_grabbing(qtbot):
    # The options popup must not grab the keyboard, or the field is untypeable.
    a = MdAutocomplete(options=["Apple", "Apricot"])
    qtbot.addWidget(a)
    a._on_text_edited("Ap")
    assert a._menu is not None
    assert a._menu._grabs_focus is False


def test_single_menu_reused_across_keystrokes(qtbot):
    # No new MdMenu (popup window) per keystroke — one is reused.
    a = MdAutocomplete(options=["Apple", "Apricot", "Banana"])
    qtbot.addWidget(a)
    a._on_text_edited("A")
    m1 = a._menu
    a._on_text_edited("Ap")
    m2 = a._menu
    assert m1 is m2
    # And it rebuilt rows in place to the current matches.
    assert [it.text for it in a._menu._items] == ["Apple", "Apricot"]


def test_top_match_auto_highlighted(qtbot):
    # Enter should commit the top match without the user arrowing first.
    a = MdAutocomplete(options=["Apple", "Apricot"])
    qtbot.addWidget(a)
    picked = []
    a.selected.connect(picked.append)
    a._on_text_edited("Ap")
    assert a._menu._highlight == 0
    assert a._menu.activate_highlighted() is True
    assert picked == ["Apple"]


def test_popup_shrinks_as_matches_reduce(qtbot):
    # Regression: as filtering narrows the matches, the popup must shrink — the
    # inner QScrollArea's default sizeHint ignores content, so the height is set
    # explicitly from the item count each open.
    a = MdAutocomplete(
        options=["Apple", "Apricot", "Avocado", "Banana", "Mango", "Orange"])
    qtbot.addWidget(a)
    a._on_text_edited("a")          # many matches
    tall = a._menu.height()
    a._on_text_edited("man")        # one match (Mango)
    short = a._menu.height()
    assert len(a._menu._items) == 1
    assert short < tall


def test_mouse_click_on_row_selects(qtbot):
    # Regression: clicking a row used to lose to a focus-out close that fired
    # before the row's mouse-release. A click must set the text and emit.
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    a = MdAutocomplete(options=["Apple", "Apricot"])
    qtbot.addWidget(a)
    picked = []
    a.selected.connect(picked.append)
    a._on_text_edited("Ap")
    row = a._menu._items[0]
    center = QPointF(row.rect().center())
    for et in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
        QApplication.sendEvent(row, QMouseEvent(
            et, center, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier))
    assert picked == ["Apple"]
    assert a.text() == "Apple"
    assert a._menu.isHidden()


def test_outside_press_dismisses_popup(qtbot):
    # The non-grabbing popup self-dismisses on a press outside its frame.
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    a = MdAutocomplete(options=["Apple", "Apricot"])
    qtbot.addWidget(a)
    a._on_text_edited("Ap")
    menu = a._menu
    assert not menu.isHidden()
    # A press far outside the popup frame closes it (app-wide event filter).
    far = QPointF(menu.frameGeometry().right() + 500,
                  menu.frameGeometry().bottom() + 500)
    QApplication.sendEvent(menu, QMouseEvent(
        QEvent.Type.MouseButtonPress, far, far, Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
    assert menu.isHidden()


def test_keyboard_navigation_and_activate(qtbot):
    a = MdAutocomplete(options=["Apple", "Apricot"])
    qtbot.addWidget(a)
    picked = []
    a.selected.connect(picked.append)
    a._on_text_edited("Ap")  # auto-highlights index 0 (Apple)
    a._menu.highlight_next()  # -> Apricot (index 1)
    assert a._menu._highlight == 1
    assert a._menu.activate_highlighted() is True
    assert picked == ["Apricot"]
    assert a.text() == "Apricot"
