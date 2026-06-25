"""Smoke test: the gallery builds every component page without crashing."""

from __future__ import annotations

from material_qt.gallery.gallery import COMPONENT_META, _COMPONENTS, GalleryWindow
from material_qt.theme.theme_manager import ThemeManager, ThemeMode


def test_gallery_builds_all_pages(qtbot):
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._stack.count() == len(_COMPONENTS)
    # Drawer has one destination per component.
    assert len(w._drawer._items) == len(_COMPONENTS)
    # Visit every page via the nav drawer (forces each builder + a paint).
    for i in range(w._stack.count()):
        w.select(i)
        assert w._stack.currentIndex() == i
    w.resize(900, 620)
    w.grab()


def test_every_component_has_metadata(qtbot):
    # Each page's hero relies on COMPONENT_META for its icon + description.
    for label, _builder in _COMPONENTS:
        assert label in COMPONENT_META


def test_search_bar_page_opens_view_and_filters(qtbot):
    # Builders run at construction, but interactive callbacks wired *inside* a
    # builder (e.g. the search bar's open_view) only fire on use — exercise that
    # path so a bad signal name / wiring raises here, not just in the live app.
    from PySide6.QtWidgets import QMainWindow

    from material_qt.gallery import gallery
    from material_qt.widgets.searchbar import MdSearchBar, MdSearchView

    win = QMainWindow()
    qtbot.addWidget(win)
    win.setCentralWidget(gallery._build_search_bar())
    win.resize(700, 500)
    win.show()
    qtbot.waitExposed(win)

    bar = win.findChild(MdSearchBar)
    assert bar is not None
    bar.clicked.emit()  # opens the full-screen search view (the wired callback)
    view = win.findChild(MdSearchView)
    assert view is not None and not view.isHidden()
    # The callbacks open_view wired must fire without error.
    view.textChanged.emit("man")
    view.suggestionSelected.emit("Mango")


def test_clicking_each_page_trigger_does_not_raise(qtbot):
    # Exercise every page's interactive triggers (buttons + search bars) so a
    # bad callback wiring inside any builder raises here, not in the live app.
    # Buttons fire even while their page is off-stack; any modal a click opens is
    # parented to the window, so dismiss overlays between pages to avoid stacking.
    from PySide6.QtWidgets import QAbstractButton, QApplication

    from material_qt.core.modal_overlay import ModalOverlay
    from material_qt.widgets.searchbar import MdSearchBar

    app = QApplication.instance()
    w = GalleryWindow()
    qtbot.addWidget(w)
    w.resize(1000, 700)
    w.show()
    qtbot.waitExposed(w)

    for i in range(w._stack.count()):
        page = w._stack.widget(i)
        for btn in page.findChildren(QAbstractButton):
            if btn.isEnabled():
                btn.click()
                app.processEvents()
        for sbar in page.findChildren(MdSearchBar):
            sbar.clicked.emit()
            app.processEvents()
        # Close any overlay this page's triggers opened so they don't stack.
        for overlay in w.findChildren(ModalOverlay):
            if not overlay.isHidden():
                overlay._close()
        app.processEvents()

    w.grab()  # still paints after all that interaction


def test_theme_toggle_flips_on_first_click(qtbot):
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert ThemeManager.instance().is_dark is False
    assert w._theme_btn.icon_name == "dark_mode"  # offers to go dark
    w._toggle_theme()
    assert ThemeManager.instance().is_dark is True
    assert w._theme_btn.icon_name == "light_mode"  # now offers to go light


def test_toggle_button_reflects_starting_theme(qtbot):
    # If the app starts dark, the toggle must already show the light-mode icon.
    ThemeManager.instance().set_mode(ThemeMode.DARK)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._theme_btn.icon_name == "light_mode"
    w._toggle_theme()
    assert ThemeManager.instance().is_dark is False


def test_gallery_defaults_to_catalog_theme(qtbot):
    from material_qt.tokens.color import ColorRole

    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    w = GalleryWindow()
    qtbot.addWidget(w)
    # Opens on the catalog (amber) theme: light primary #7f5700, surface #fff8f3.
    assert ThemeManager.instance().color(ColorRole.PRIMARY).name() == "#7f5700"
    assert ThemeManager.instance().color(ColorRole.SURFACE).name() == "#fff8f3"


def test_palette_button_cycles_theme_preset(qtbot):
    from material_qt.tokens.color import ColorRole

    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert ThemeManager.instance().color(ColorRole.PRIMARY).name() == "#7f5700"  # Catalog
    w._cycle_brand()  # -> Baseline (token primary)
    assert ThemeManager.instance().color(ColorRole.PRIMARY).name() == "#6750a4"
    w._cycle_brand()  # -> back to Catalog
    assert ThemeManager.instance().color(ColorRole.PRIMARY).name() == "#7f5700"


def test_collapse_clears_spurious_hamburger_focus_ring(qtbot):
    # Hiding the focused drawer item on collapse makes Qt move focus to the
    # hamburger with TabFocusReason, which would spuriously show its keyboard
    # focus ring until the next click. The collapse must clear that.
    from PySide6.QtCore import Qt

    w = GalleryWindow()
    qtbot.addWidget(w)
    w.resize(1200, 800)
    w.show()
    item = w._drawer._items[2]
    item.setFocus(Qt.FocusReason.MouseFocusReason)
    w.select(2)
    w.resize(700, 800)  # cross the breakpoint -> collapse
    assert not w._hamburger.hasFocus()
    assert not w._hamburger.focus_ring.visible


def test_modal_select_clears_spurious_hamburger_focus_ring(qtbot):
    # In compact mode, selecting a destination in the modal drawer closes it;
    # hiding the focused item must not leave a focus ring on the hamburger.
    from PySide6.QtCore import Qt

    w = GalleryWindow()
    qtbot.addWidget(w)
    w.resize(700, 800)  # compact -> hamburger + modal
    w.show()
    w._toggle_nav()  # open the modal drawer
    assert w._modal.is_open()
    item = w._drawer._items[5]
    item.setFocus(Qt.FocusReason.MouseFocusReason)
    item.setChecked(True)  # select -> closes the modal
    assert not w._modal.is_open()
    assert not w._hamburger.hasFocus()
    assert not w._hamburger.focus_ring.visible
