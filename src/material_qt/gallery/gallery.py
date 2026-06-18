"""A single browsable gallery of every Material Qt component.

The Qt analog of the Material Web catalog: a left-hand component list and a
scrollable showcase panel for the selected component, plus a global light/dark
toggle. Run with ``python -m material_qt.gallery``.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..theme.theme_manager import ThemeManager
from ..tokens.color import ColorRole
from ..tokens.typography import TypescaleRole, spec_for
from ..core.typography_util import font_for_role
from ..widgets.badge import MdBadge
from ..widgets.button import (
    MdElevatedButton,
    MdFilledButton,
    MdFilledTonalButton,
    MdOutlinedButton,
    MdTextButton,
)
from ..widgets.card import CardVariant, MdCard
from ..widgets.checkbox import MdCheckbox
from ..widgets.dialog import MdDialog
from ..widgets.chips import (
    MdAssistChip,
    MdChipSet,
    MdFilterChip,
    MdInputChip,
    MdSuggestionChip,
)
from ..widgets.divider import MdDivider
from ..widgets.field import FieldVariant, MdField
from ..widgets.fab import FabColor, FabSize, MdBrandedFab, MdFab
from ..widgets.icon import MdIcon
from ..widgets.iconbutton import (
    MdFilledIconButton,
    MdFilledTonalIconButton,
    MdIconButton,
    MdOutlinedIconButton,
)
from ..widgets.item import MdItem
from ..widgets.list import MdList, MdListItem
from ..widgets.menu import MdMenu, MdMenuItem
from ..widgets.navigationbar import MdNavigationBar
from ..widgets.navigationdrawer import MdNavigationDrawer
from ..widgets.navigationtab import MdNavigationTab
from ..widgets.progress import MdCircularProgress, MdLinearProgress
from ..widgets.radio import MdRadio
from ..widgets.segmentedbutton import MdSegmentedButton, MdSegmentedButtonSet
from ..widgets.select import MdFilledSelect, MdOutlinedSelect
from ..widgets.slider import MdSlider
from ..widgets.switch import MdSwitch
from ..widgets.tabs import MdTabs
from ..widgets.textfield import MdFilledTextField, MdOutlinedTextField


def _section(title: str) -> QLabel:
    label = QLabel(title)
    label.setFont(font_for_role(TypescaleRole.TITLE_SMALL))
    return label


def _row(*widgets: QWidget, spacing: int = 16) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(spacing)
    for widget in widgets:
        lay.addWidget(widget)
    lay.addStretch(1)
    return w


def _labeled(widget: QWidget, text: str) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)
    lay.addWidget(widget)
    lay.addWidget(QLabel(text))
    lay.addStretch(1)
    return w


# -- per-component showcase builders --------------------------------------


def _build_button() -> QWidget:
    page = _page()
    lay = page.layout()
    variants = [
        ("Elevated", MdElevatedButton),
        ("Filled", MdFilledButton),
        ("Tonal", MdFilledTonalButton),
        ("Outlined", MdOutlinedButton),
        ("Text", MdTextButton),
    ]
    lay.addWidget(_section("Variants"))
    lay.addWidget(_row(*[cls(label) for label, cls in variants]))
    lay.addWidget(_section("With icon"))
    lay.addWidget(_row(*[cls(label, icon="add") for label, cls in variants]))
    lay.addWidget(_section("Disabled"))
    disabled = []
    for label, cls in variants:
        b = cls(label)
        b.setEnabled(False)
        disabled.append(b)
    lay.addWidget(_row(*disabled))
    lay.addStretch(1)
    return page


def _build_icon_button() -> QWidget:
    page = _page()
    lay = page.layout()
    variants = [
        ("Standard", MdIconButton),
        ("Filled", MdFilledIconButton),
        ("Tonal", MdFilledTonalIconButton),
        ("Outlined", MdOutlinedIconButton),
    ]
    lay.addWidget(_section("Variants"))
    lay.addWidget(_row(*[cls("favorite") for _, cls in variants]))
    lay.addWidget(_section("Toggle (selected)"))
    lay.addWidget(
        _row(*[cls("favorite", toggle=True, checked=True) for _, cls in variants])
    )
    lay.addStretch(1)
    return page


def _build_fab() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Sizes"))
    lay.addWidget(
        _row(
            MdFab("edit", size=FabSize.SMALL),
            MdFab("edit", size=FabSize.REGULAR),
            MdFab("edit", size=FabSize.LARGE),
            MdBrandedFab(),
        )
    )
    lay.addWidget(_section("Colors"))
    lay.addWidget(
        _row(*[MdFab("add", color=c) for c in (
            FabColor.SURFACE, FabColor.PRIMARY, FabColor.SECONDARY, FabColor.TERTIARY
        )])
    )
    lay.addWidget(_section("Extended"))
    lay.addWidget(_row(MdFab("add", label="Compose", color=FabColor.PRIMARY)))
    lay.addStretch(1)
    return page


def _build_checkbox() -> QWidget:
    page = _page()
    lay = page.layout()
    unchecked = MdCheckbox()
    checked = MdCheckbox(checked=True)
    indet = MdCheckbox()
    indet.set_indeterminate(True)
    err = MdCheckbox(checked=True, error=True)
    disabled = MdCheckbox(checked=True)
    disabled.setEnabled(False)
    for w, t in (
        (unchecked, "Unchecked"), (checked, "Checked"), (indet, "Indeterminate"),
        (err, "Error"), (disabled, "Disabled"),
    ):
        lay.addWidget(_labeled(w, t))
    lay.addStretch(1)
    return page


def _build_radio() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Single-selection group"))
    group = QWidget()
    gl = QVBoxLayout(group)
    gl.setContentsMargins(0, 0, 0, 0)
    # Wrapping each radio in its own row widget puts them in different parents,
    # so autoExclusive can't link them — a QButtonGroup enforces exclusivity.
    btn_group = QButtonGroup(group)
    for i, name in enumerate(("Apple", "Banana", "Cherry")):
        r = MdRadio(checked=(i == 0))
        btn_group.addButton(r)
        gl.addWidget(_labeled(r, name))
    lay.addWidget(group)
    lay.addStretch(1)
    return page


def _build_switch() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_labeled(MdSwitch(), "Off"))
    lay.addWidget(_labeled(MdSwitch(checked=True), "On"))
    d = MdSwitch(checked=True)
    d.setEnabled(False)
    lay.addWidget(_labeled(d, "Disabled"))
    lay.addStretch(1)
    return page


def _build_segmented() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Single-select"))
    single = MdSegmentedButtonSet()
    for i, label in enumerate(("Day", "Week", "Month")):
        seg = MdSegmentedButton(label)
        if i == 0:
            seg.setChecked(True)
        single.add_segment(seg)
    lay.addWidget(single)
    lay.addWidget(_section("Multi-select"))
    multi = MdSegmentedButtonSet(multi=True)
    for label in ("Bold", "Italic", "Underline"):
        multi.add_segment(MdSegmentedButton(label))
    lay.addWidget(multi)
    lay.addStretch(1)
    return page


def _build_select() -> QWidget:
    page = _page()
    lay = page.layout()
    f = MdFilledSelect(label="Fruit", supporting_text="Pick one")
    for x in ("Apple", "Banana", "Cherry", "Date"):
        f.add_option(x)
    f.setMinimumWidth(280)
    o = MdOutlinedSelect(label="Country")
    for x in ("USA", "Canada", "Mexico"):
        o.add_option(x)
    o.set_value("Canada")
    o.setMinimumWidth(280)
    lay.addWidget(f)
    lay.addWidget(o)
    lay.addStretch(1)
    return page


def _build_slider() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Continuous"))
    lay.addWidget(MdSlider(value=40))
    lay.addWidget(_section("Discrete (step 10, ticks)"))
    lay.addWidget(MdSlider(value=60, step=10, ticks=True))
    lay.addStretch(1)
    return page


def _build_progress() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Linear"))
    lay.addWidget(MdLinearProgress(value=0.6))
    lay.addWidget(MdLinearProgress(indeterminate=True))
    lay.addWidget(_section("Circular"))
    lay.addWidget(
        _row(
            MdCircularProgress(value=0.25),
            MdCircularProgress(value=0.7),
            MdCircularProgress(indeterminate=True),
        )
    )
    lay.addStretch(1)
    return page


def _build_card() -> QWidget:
    page = _page()
    lay = page.layout()
    row = QHBoxLayout()
    row.setSpacing(16)
    for variant, label in (
        (CardVariant.ELEVATED, "Elevated"),
        (CardVariant.FILLED, "Filled"),
        (CardVariant.OUTLINED, "Outlined"),
    ):
        card = MdCard(variant=variant)
        card.add_widget(QLabel(label))
        card.add_widget(QLabel("Supporting content."))
        card.setFixedSize(180, 110)
        row.addWidget(card)
    row.addStretch(1)
    holder = QWidget()
    holder.setLayout(row)
    lay.addWidget(holder)
    lay.addStretch(1)
    return page


def _build_chips() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Assist / Suggestion"))
    s1 = MdChipSet()
    s1.add_chip(MdAssistChip("Add to calendar", icon="event"))
    s1.add_chip(MdSuggestionChip("Suggestion"))
    lay.addWidget(s1)
    lay.addWidget(_section("Filter"))
    s2 = MdChipSet()
    s2.add_chip(MdFilterChip("All", selected=True))
    s2.add_chip(MdFilterChip("Unread"))
    s2.add_chip(MdFilterChip("Starred"))
    lay.addWidget(s2)
    lay.addWidget(_section("Input"))
    s3 = MdChipSet()
    for name in ("Alice", "Bob", "Carol"):
        s3.add_chip(MdInputChip(name, icon="person"))
    lay.addWidget(s3)
    lay.addStretch(1)
    return page


def _build_tabs() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Primary"))
    primary = MdTabs()
    primary.add_tab("Flights", icon="flight")
    primary.add_tab("Trips", icon="luggage")
    primary.add_tab("Explore", icon="explore")
    lay.addWidget(primary)
    lay.addWidget(_section("Secondary"))
    secondary = MdTabs(secondary=True)
    for t in ("Overview", "Specifications", "Reviews"):
        secondary.add_tab(t)
    lay.addWidget(secondary)
    lay.addStretch(1)
    return page


def _build_typography() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.setSpacing(2)
    for role in TypescaleRole:
        spec = spec_for(role)
        lbl = QLabel(f"{role.value}  ·  {spec.size_rem * 16:.0f}px / {spec.weight}")
        lbl.setFont(font_for_role(role))
        lbl_role = ColorRole.ON_SURFACE
        lbl.setStyleSheet(
            f"color: {ThemeManager.instance().color(lbl_role).name()};"
        )
        lay.addWidget(lbl)
    lay.addStretch(1)
    return page


def _build_text_field() -> QWidget:
    page = _page()
    lay = page.layout()
    f = MdFilledTextField(label="Name", supporting_text="As it appears on your ID")
    f.setMinimumWidth(280)
    o = MdOutlinedTextField(label="Email", text="a@b.com")
    o.setMinimumWidth(280)
    p = MdOutlinedTextField(label="Password", password=True, error=True,
                            supporting_text="At least 8 characters")
    p.setMinimumWidth(280)
    for tf in (f, o, p):
        lay.addWidget(tf)
    lay.addStretch(1)
    return page


def _build_field() -> QWidget:
    from PySide6.QtWidgets import QLineEdit

    page = _page()
    lay = page.layout()

    def field(variant, label, **kw):
        f = MdField(variant=variant, label=label, **kw)
        edit = QLineEdit()
        edit.setStyleSheet("background: transparent; border: none;")
        edit.textChanged.connect(lambda t: f.set_populated(bool(t)))
        f.set_content(edit)
        f.setMinimumWidth(280)
        return f

    lay.addWidget(field(FieldVariant.FILLED, "Filled", supporting_text="Supporting text"))
    lay.addWidget(field(FieldVariant.OUTLINED, "Outlined"))
    lay.addWidget(field(FieldVariant.OUTLINED, "Error", supporting_text="Required",
                        error=True))
    lay.addStretch(1)
    return page


def _build_list() -> QWidget:
    page = _page()
    lay = page.layout()
    lst = MdList()
    lst.add_item(MdListItem("Inbox", supporting_text="3 new messages",
                            leading=MdIcon("inbox"), trailing_supporting_text="3"))
    lst.add_item(MdListItem("Starred", leading=MdIcon("star"),
                            trailing=MdIcon("chevron_right")), divider=True)
    lst.add_item(MdListItem("Sent", leading=MdIcon("send")), divider=True)
    lst.add_item(MdListItem("Drafts", supporting_text="2 drafts",
                            leading=MdIcon("drafts")), divider=True)
    lst.setMaximumWidth(420)
    lay.addWidget(lst)
    lay.addStretch(1)
    return page


def _build_dialog() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Dialog (click to open)"))
    open_btn = MdFilledButton("Open dialog")
    status = QLabel("(no result)")

    def open_dialog():
        # Parent the dialog to the top-level window so the scrim covers it.
        host = page.window()
        dlg = MdDialog(host, icon="delete", headline="Delete file?",
                       supporting_text="This will permanently remove the file. "
                       "This action cannot be undone.")
        dlg.add_action("Cancel", accept=False)
        dlg.add_action("Delete", accept=True)
        dlg.accepted.connect(lambda: status.setText("Deleted"))
        dlg.rejected.connect(lambda: status.setText("Cancelled"))
        dlg.open()

    open_btn.clicked.connect(open_dialog)
    lay.addWidget(_row(open_btn))
    lay.addWidget(status)
    lay.addStretch(1)
    return page


def _build_menu() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Menu (click to open)"))
    trigger = MdFilledButton("Open menu")
    status = QLabel("(no selection)")

    def open_menu():
        menu = MdMenu(trigger)
        for label, icon in [("Cut", "content_cut"), ("Copy", "content_copy"),
                            ("Paste", "content_paste"), ("Delete", "delete")]:
            menu.add_item(MdMenuItem(label, leading_icon=icon))
        menu.selected.connect(lambda t: status.setText(f"Selected: {t}"))
        menu.open_at(trigger)

    trigger.clicked.connect(open_menu)
    lay.addWidget(_row(trigger))
    lay.addWidget(status)
    lay.addStretch(1)
    return page


def _build_navigation_bar() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Navigation bar"))
    bar = MdNavigationBar()
    for label, icon in [("Home", "home"), ("Search", "search"),
                        ("Saved", "bookmark"), ("Profile", "person")]:
        bar.add_destination(label, icon=icon)
    lay.addWidget(bar)
    lay.addStretch(1)
    return page


def _build_navigation_drawer() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Navigation drawer"))
    drawer = MdNavigationDrawer(headline="Mail")
    for label, icon in [("Inbox", "inbox"), ("Starred", "star"),
                        ("Sent", "send"), ("Drafts", "drafts")]:
        drawer.add_destination(label, icon=icon)
    lay.addWidget(drawer)
    lay.addStretch(1)
    return page


def _build_navigation_tab() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Navigation tabs"))
    bar = QHBoxLayout()
    bar.setSpacing(0)
    grp = QButtonGroup(page)
    for i, (label, icon) in enumerate(
        [("Home", "home"), ("Search", "search"), ("Saved", "bookmark"),
         ("Profile", "person")]
    ):
        t = MdNavigationTab(label, icon=icon)
        if i == 0:
            t.setChecked(True)
        grp.addButton(t)
        bar.addWidget(t)
    holder = QWidget()
    holder.setLayout(bar)
    lay.addWidget(holder)
    lay.addStretch(1)
    return page


def _build_item() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(MdItem("One-line item"))
    lay.addWidget(MdDivider())
    lay.addWidget(
        MdItem("Two-line item", supporting_text="Supporting text",
               leading=MdIcon("folder"))
    )
    lay.addWidget(MdDivider())
    lay.addWidget(
        MdItem(
            "Three-line item",
            supporting_text="Longer supporting text that wraps across lines.",
            trailing_supporting_text="100+",
            leading=MdIcon("email"),
            trailing=MdIcon("chevron_right"),
        )
    )
    lay.addStretch(1)
    return page


def _build_badge() -> QWidget:
    page = _page()
    lay = page.layout()
    dot, eight, many = MdBadge(), MdBadge(), MdBadge()
    eight.set_value("8")
    many.set_value("99+")
    lay.addWidget(_labeled(dot, "Dot"))
    lay.addWidget(_labeled(eight, "Value 8"))
    lay.addWidget(_labeled(many, "Value 99+"))
    lay.addStretch(1)
    return page


def _build_divider() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(QLabel("Above"))
    lay.addWidget(MdDivider())
    lay.addWidget(QLabel("Below"))
    inset = MdDivider()
    inset.inset_start = True
    lay.addWidget(inset)
    lay.addWidget(QLabel("After inset-start divider"))
    lay.addStretch(1)
    return page


def _build_icon() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Icons (24px)"))
    names = ["home", "favorite", "settings", "search", "delete", "check_circle"]
    lay.addWidget(_row(*[MdIcon(n) for n in names]))
    lay.addWidget(_section("Sizes"))
    lay.addWidget(_row(*[MdIcon("star", size=s) for s in (18, 24, 36, 48)]))
    lay.addStretch(1)
    return page


def _page() -> QWidget:
    page = QWidget()
    lay = QVBoxLayout(page)
    lay.setContentsMargins(28, 24, 28, 24)
    lay.setSpacing(14)
    return page


_COMPONENTS = [
    ("Badge", _build_badge),
    ("Button", _build_button),
    ("Card", _build_card),
    ("Checkbox", _build_checkbox),
    ("Chips", _build_chips),
    ("Dialog", _build_dialog),
    ("Divider", _build_divider),
    ("FAB", _build_fab),
    ("Field", _build_field),
    ("Icon", _build_icon),
    ("Icon button", _build_icon_button),
    ("Item", _build_item),
    ("List", _build_list),
    ("Menu", _build_menu),
    ("Navigation bar", _build_navigation_bar),
    ("Navigation drawer", _build_navigation_drawer),
    ("Navigation tab", _build_navigation_tab),
    ("Progress", _build_progress),
    ("Radio", _build_radio),
    ("Segmented", _build_segmented),
    ("Select", _build_select),
    ("Slider", _build_slider),
    ("Switch", _build_switch),
    ("Tabs", _build_tabs),
    ("Text field", _build_text_field),
    ("Typography", _build_typography),
]


class GalleryWindow(QWidget):
    """Browsable gallery of all Material Qt components."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Gallery")
        ThemeManager.instance().themeChanged.connect(self._restyle)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header.
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 16, 24, 16)
        title = QLabel("Material Qt")
        title.setFont(font_for_role(TypescaleRole.TITLE_LARGE))
        hl.addWidget(title)
        hl.addStretch(1)
        self._theme_btn = MdFilledTonalButton("Dark mode", icon="dark_mode")
        self._theme_btn.clicked.connect(self._toggle_theme)
        hl.addWidget(self._theme_btn)
        root.addWidget(header)
        self._header = header

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._nav = QListWidget()
        self._nav.setFixedWidth(200)
        self._stack = QStackedWidget()
        for label, builder in _COMPONENTS:
            QListWidgetItem(label, self._nav)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(builder())
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            self._stack.addWidget(scroll)
        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav.setCurrentRow(0)

        body.addWidget(self._nav)
        body.addWidget(self._stack, 1)
        root.addLayout(body, 1)
        self._restyle()

    def _toggle_theme(self) -> None:
        # Flip relative to the *actual* current theme (which may start in SYSTEM
        # mode resolving to dark), so the first click always changes the theme.
        ThemeManager.instance().toggle_light_dark()

    def _restyle(self) -> None:
        # Paint the window and nav with theme surface colors.
        theme = ThemeManager.instance()
        # Keep the toggle button label/icon in sync with the real theme state.
        dark = theme.is_dark
        self._theme_btn.setText("Light mode" if dark else "Dark mode")
        self._theme_btn.set_icon("light_mode" if dark else "dark_mode")
        bg = theme.color(ColorRole.SURFACE).name()
        on = theme.color(ColorRole.ON_SURFACE).name()
        nav_bg = theme.color(ColorRole.SURFACE_CONTAINER_LOW).name()
        sel = theme.color(ColorRole.SECONDARY_CONTAINER).name()
        on_sel = theme.color(ColorRole.ON_SECONDARY_CONTAINER).name()
        self.setStyleSheet(f"GalleryWindow {{ background: {bg}; }}")
        self._header.setStyleSheet(f"background: {nav_bg};")
        self._nav.setStyleSheet(
            f"QListWidget {{ background: {nav_bg}; color: {on}; border: none;"
            f" outline: none; padding: 8px; }}"
            f" QListWidget::item {{ padding: 10px 12px; border-radius: 8px; }}"
            f" QListWidget::item:selected {{ background: {sel}; color: {on_sel}; }}"
        )


def main() -> int:
    app = QApplication(sys.argv)
    w = GalleryWindow()
    w.resize(900, 620)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
