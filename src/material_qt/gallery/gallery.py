"""A single browsable gallery of every Material Qt component.

The Qt analog of the Material Web catalog: a left-hand component list and a
scrollable showcase panel for the selected component, plus a global light/dark
toggle. Run with ``python -m material_qt.gallery``.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..theme.theme_manager import ThemeManager
from ..theme.presets import PRESETS
from ..core.responsive import ResponsiveHelper, WindowSizeClass, size_class_for
from ..core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ..tokens.motion import Duration, Easing
from ..tokens.color import ColorRole
from ..tokens.typography import TypescaleRole, spec_for
from ..core.typography_util import font_for_role
from ..widgets.badge import MdBadge
from ..widgets.banner import MdBanner
from ..widgets.bottomsheet import MdBottomSheet
from ..widgets.buttongroup import MdButtonGroup
from ..widgets.carousel import MdCarousel, MdWeightedCarousel
from ..widgets.expansionpanel import MdExpansionPanel
from ..widgets.fabmenu import MdFabMenu
from ..widgets.loadingindicator import MdLoadingIndicator
from ..widgets.toolbar import MdToolbar
from ..widgets.searchbar import MdSearchBar
from ..widgets.sidesheet import MdSideSheet
from ..widgets.button import (
    MdElevatedButton,
    MdFilledButton,
    MdFilledTonalButton,
    MdOutlinedButton,
    MdTextButton,
)
from ..widgets.card import CardVariant, MdCard
from ..widgets.checkbox import MdCheckbox
from ..widgets.datatable import MdDataTable
from ..widgets.datepicker import MdDatePicker
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
from ..widgets.navigationrail import MdNavigationRail
from ..widgets.navigationtab import MdNavigationTab
from ..widgets.progress import MdCircularProgress, MdLinearProgress
from ..widgets.radio import MdRadio
from ..widgets.rangeslider import MdRangeSlider
from ..widgets.segmentedbutton import MdSegmentedButton, MdSegmentedButtonSet
from ..widgets.select import MdFilledSelect, MdOutlinedSelect
from ..widgets.splitbutton import MdSplitButton, SplitButtonColor
from ..widgets.slider import MdSlider
from ..widgets.snackbar import MdSnackbar
from ..widgets.switch import MdSwitch
from ..widgets.tabs import MdTabs
from ..widgets.textfield import MdFilledTextField, MdOutlinedTextField
from ..widgets.timepicker import MdTimePicker
from ..widgets.tooltip import MdTooltip
from ..widgets.topappbar import MdTopAppBar, TopAppBarVariant


def _themed_text_label(
    text: str,
    *,
    role: ColorRole = ColorRole.ON_SURFACE,
    typescale: TypescaleRole | None = None,
) -> QLabel:
    """A QLabel whose color follows the theme (re-applied on every change)."""
    label = QLabel(text)
    if typescale is not None:
        label.setFont(font_for_role(typescale))

    def apply() -> None:
        label.setStyleSheet(f"color: {ThemeManager.instance().color(role).name()};")

    apply()
    ThemeManager.instance().themeChanged.connect(apply)
    return label


def _section(title: str) -> QLabel:
    return _themed_text_label(
        title, role=ColorRole.ON_SURFACE_VARIANT, typescale=TypescaleRole.TITLE_SMALL
    )


class _FlowLayout(QLayout):
    """A layout that lays children left-to-right and wraps to new lines — so
    showcase rows reflow responsively instead of clipping at narrow widths."""

    def __init__(self, parent: QWidget | None = None, *, hspacing: int = 16,
                 vspacing: int = 16) -> None:
        super().__init__(parent)
        self._items: list = []
        self._hs = hspacing
        self._vs = vspacing

    def addItem(self, item) -> None:  # noqa: N802
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, i):  # noqa: N802
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i):  # noqa: N802
        return self._items.pop(i) if 0 <= i < len(self._items) else None

    def expandingDirections(self):  # noqa: N802
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        return self._do_layout(QRect(0, 0, width, 0), test=True)

    def setGeometry(self, rect: QRect) -> None:  # noqa: N802
        super().setGeometry(rect)
        self._do_layout(rect, test=False)

    def sizeHint(self) -> QSize:  # noqa: N802
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # noqa: N802
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect: QRect, *, test: bool) -> int:
        m = self.contentsMargins()
        x = rect.x() + m.left()
        y = rect.y() + m.top()
        right = rect.right() - m.right()
        line_h = 0
        for item in self._items:
            hint = item.sizeHint()
            w, h = hint.width(), hint.height()
            if line_h and x + w > right:
                x = rect.x() + m.left()
                y += line_h + self._vs
                line_h = 0
            if not test:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x += w + self._hs
            line_h = max(line_h, h)
        return y + line_h + m.bottom() - rect.y()


def _row(*widgets: QWidget, spacing: int = 16) -> QWidget:
    w = QWidget()
    # Flow layout so rows wrap when narrow; generous margins so elevation
    # drop-shadows aren't clipped by the row's bounds — sized for a hovered FAB
    # (level-4: ~20px blur, 6px down-offset), the largest shadow shown in a row.
    lay = _FlowLayout(w, hspacing=spacing, vspacing=spacing)
    lay.setContentsMargins(20, 14, 20, 24)
    for widget in widgets:
        lay.addWidget(widget)
    sp = w.sizePolicy()
    sp.setHeightForWidth(True)
    w.setSizePolicy(sp)
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


def _build_split_button() -> QWidget:
    from ..widgets.menu import MdMenu, MdMenuItem

    page = _page()
    lay = page.layout()
    for color in SplitButtonColor:
        lay.addWidget(_section(color.value))
        sb = MdSplitButton("Save", color=color, icon="save")
        menu = MdMenu(sb)
        for label in ("Save as draft", "Save and close", "Save a copy"):
            menu.add_item(MdMenuItem(label))
        sb.set_menu(menu)
        lay.addWidget(_row(sb))
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


def _build_range_slider() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Range slider"))
    lay.addWidget(MdRangeSlider(low=25, high=75))
    lay.addWidget(_section("Discrete (step 10)"))
    lay.addWidget(MdRangeSlider(low=20, high=60, step=10))
    lay.addWidget(_section("Labeled (value bubble while dragging)"))
    lay.addWidget(MdRangeSlider(low=30, high=70, labeled=True))
    lay.addStretch(1)
    return page


def _build_slider() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Continuous"))
    lay.addWidget(MdSlider(value=40))
    lay.addWidget(_section("Discrete (step 10, ticks)"))
    lay.addWidget(MdSlider(value=60, step=10, ticks=True))
    lay.addWidget(_section("Labeled (value bubble while dragging)"))
    lay.addWidget(MdSlider(value=30, labeled=True))
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
    # Margins so the elevated card's drop-shadow isn't clipped by the holder.
    row.setContentsMargins(10, 8, 10, 16)
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
        text = f"{role.value}  ·  {spec.size_rem * 16:.0f}px / {spec.weight}"
        lay.addWidget(_themed_text_label(text, typescale=role))
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


def _build_data_table() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Data table (click a header to sort)"))
    table = MdDataTable(selectable=True)
    table.set_columns(["Dessert", "Calories", "Fat (g)"],
                      numeric=[False, True, True])
    for row in [["Frozen yogurt", 159, 6], ["Ice cream sandwich", 237, 9],
                ["Eclair", 262, 16], ["Cupcake", 305, 4]]:
        table.add_row(row)
    lay.addWidget(table)
    lay.addStretch(1)
    return page


def _build_date_picker() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Date picker (click to open)"))
    open_btn = MdFilledButton("Pick a date")
    status = QLabel("(no date selected)")

    def open_picker():
        dp = MdDatePicker(page.window())
        dp.closed.connect(dp.deleteLater)
        dp.accepted.connect(lambda d: status.setText(d.toString("dddd, MMMM d, yyyy")))
        dp.open()

    open_btn.clicked.connect(open_picker)
    lay.addWidget(_row(open_btn))
    lay.addWidget(status)
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
    lay.addWidget(_section("Navigation bar (with badges)"))
    bar = MdNavigationBar()
    bar.add_destination("Home", icon="home")
    bar.add_destination("Mail", icon="mail", badge="8")
    bar.add_destination("Alerts", icon="notifications", badge="")
    bar.add_destination("Profile", icon="person")
    lay.addWidget(bar)

    lay.addWidget(_section("Label behavior: only selected"))
    sel = MdNavigationBar(label_behavior="selected")
    for label, icon in [("Home", "home"), ("Search", "search"),
                        ("Saved", "bookmark"), ("Profile", "person")]:
        sel.add_destination(label, icon=icon)
    lay.addWidget(sel)
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
    drawer.add_divider()
    drawer.add_section("Labels")
    for label, icon in [("Work", "work"), ("Personal", "person")]:
        drawer.add_destination(label, icon=icon)
    lay.addWidget(drawer)
    lay.addStretch(1)
    return page


def _build_navigation_rail() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Navigation rail (toggle to extend)"))
    dests = [("Home", "home"), ("Search", "search"),
             ("Saved", "bookmark"), ("Profile", "person")]
    rail = MdNavigationRail()
    for label, icon in dests:
        rail.add_destination(label, icon=icon)
    rail.set_leading(MdFab("edit", size=FabSize.SMALL, color=FabColor.PRIMARY))
    rail.setFixedHeight(360)

    toggle = MdFilledTonalButton("Toggle extended")
    toggle.clicked.connect(lambda: rail.set_extended(not rail.extended))

    row = QHBoxLayout()
    row.addWidget(rail)
    row.addStretch(1)
    holder = QWidget()
    holder.setLayout(row)
    lay.addWidget(_row(toggle))
    lay.addWidget(holder)
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


def _build_time_picker() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Time picker (dial + keyboard input)"))
    status = QLabel("(no time selected)")

    def open_picker(*, hour24: bool):
        tp = MdTimePicker(page.window(), hour24=hour24)
        tp.closed.connect(tp.deleteLater)
        fmt = "HH:mm" if hour24 else "h:mm AP"
        tp.accepted.connect(lambda t: status.setText(t.toString(fmt)))
        tp.open()

    twelve = MdFilledButton("Pick a time (12h)")
    twentyfour = MdFilledButton("Pick a time (24h)")
    twelve.clicked.connect(lambda: open_picker(hour24=False))
    twentyfour.clicked.connect(lambda: open_picker(hour24=True))
    lay.addWidget(_row(twelve, twentyfour))
    lay.addWidget(status)
    lay.addStretch(1)
    return page


def _build_tooltip() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Tooltip (hover the buttons)"))
    row = QHBoxLayout()
    for label, tip in [("Favorite", "Add to favorites"),
                       ("Share", "Share this item"),
                       ("Delete", "Move to trash")]:
        btn = MdOutlinedButton(label)
        MdTooltip.attach(btn, tip)
        row.addWidget(btn)
    row.addStretch(1)
    holder = QWidget()
    holder.setLayout(row)
    lay.addWidget(holder)
    lay.addStretch(1)
    return page


def _build_top_app_bar() -> QWidget:
    page = _page()
    lay = page.layout()
    for variant, name in [
        (TopAppBarVariant.CENTER, "Center-aligned"),
        (TopAppBarVariant.SMALL, "Small"),
        (TopAppBarVariant.MEDIUM, "Medium"),
        (TopAppBarVariant.LARGE, "Large"),
    ]:
        lay.addWidget(_section(name))
        nav = MdIconButton("menu")
        bar = MdTopAppBar("Title", variant=variant, leading=nav)
        bar.add_action("search")
        bar.add_action("more_vert")
        lay.addWidget(bar)

    # Interactive scroll-under collapse: a medium bar pinned above its own
    # scroll area. Scrolling the list collapses the bar 112 -> 64px.
    lay.addWidget(_section("Scroll to collapse (medium)"))
    demo = QWidget()
    demo.setFixedHeight(280)
    dv = QVBoxLayout(demo)
    dv.setContentsMargins(0, 0, 0, 0)
    dv.setSpacing(0)
    cbar = MdTopAppBar("Settings", variant=TopAppBarVariant.MEDIUM,
                       leading=MdIconButton("menu"))
    cbar.add_action("search")
    cbar.add_action("more_vert")
    content = QWidget()
    cl = QVBoxLayout(content)
    cl.setContentsMargins(16, 12, 16, 12)
    cl.setSpacing(10)
    for i in range(20):
        cl.addWidget(QLabel(f"List item {i + 1}"))
    cl.addStretch(1)
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setWidget(content)
    sa.setFrameShape(QScrollArea.Shape.NoFrame)
    cbar.attach_scroll_area(sa)
    dv.addWidget(cbar)
    dv.addWidget(sa, 1)
    lay.addWidget(demo)
    lay.addStretch(1)
    return page


def _build_snackbar() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Snackbar (click to show)"))
    show_btn = MdFilledButton("Show snackbar")

    def show_snackbar():
        host = page.window()
        sb = MdSnackbar(host, "Photo deleted from album", action_label="Undo")
        sb.dismissed.connect(sb.deleteLater)  # transient: don't accumulate
        sb.open()

    show_btn.clicked.connect(show_snackbar)
    lay.addWidget(_row(show_btn))
    lay.addStretch(1)
    return page


def _build_banner() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Banner"))
    banner = MdBanner("Your photos are being backed up to the cloud.",
                      icon="cloud_upload")
    banner.add_action("Turn off")
    banner.add_action("Open")
    lay.addWidget(banner)
    lay.addStretch(1)
    return page


def _build_bottom_sheet() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Bottom sheet (click to open)"))
    open_btn = MdFilledButton("Show bottom sheet")

    def open_sheet():
        sheet = MdBottomSheet(page.window())
        sheet.closed.connect(sheet.deleteLater)
        title = QLabel("Share")
        title.setFont(font_for_role(TypescaleRole.TITLE_LARGE))
        sheet.add_content(title)
        for label in ["Messages", "Email", "Copy link", "Nearby"]:
            sheet.add_content(MdItem(label, leading=MdIcon("share")))
        sheet.open()

    open_btn.clicked.connect(open_sheet)
    lay.addWidget(_row(open_btn))
    lay.addStretch(1)
    return page


def _build_side_sheet() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Side sheet (click to open)"))
    open_btn = MdFilledButton("Show side sheet")

    def open_sheet():
        sheet = MdSideSheet(page.window(), title="Filters")
        sheet.closed.connect(sheet.deleteLater)
        for text in ["Category", "Price range", "Rating", "Availability"]:
            sheet.add_content(MdItem(text, leading=MdIcon("tune")))
        sheet.add_action("Reset")
        sheet.add_action("Apply")
        sheet.open()

    open_btn.clicked.connect(open_sheet)
    lay.addWidget(_row(open_btn))
    lay.addStretch(1)
    return page


def _build_carousel() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Carousel (drag, swipe, or scroll to browse)"))
    names = ["Beach", "Mountain", "Forest", "City", "Desert", "Lake"]
    carousel = MdCarousel()
    for name in names:
        carousel.add_tile(name)
    status = QLabel(f"Showing: {names[0]}")
    carousel.indexChanged.connect(
        lambda i: status.setText(f"Showing: {names[i]}" if 0 <= i < len(names) else "")
    )
    lay.addWidget(carousel)
    lay.addWidget(status)

    lay.addWidget(_section("Multi-browse — weights [3, 2, 1] (items resize as you scroll)"))
    multi = MdWeightedCarousel(weights=[3, 2, 1])
    for name in names:
        multi.add_tile(name)
    lay.addWidget(multi)

    lay.addWidget(_section("Hero — weights [1, 7, 1]"))
    hero = MdWeightedCarousel(weights=[1, 7, 1])
    for name in names:
        hero.add_tile(name)
    lay.addWidget(hero)
    lay.addStretch(1)
    return page


def _build_expansion_panel() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Expansion panels"))
    for i, (title, body) in enumerate([
        ("Trip details", "Flight, hotel, and rental car reservations."),
        ("Travelers", "2 adults, 1 child."),
        ("Payment", "Visa ending in 4242."),
    ]):
        panel = MdExpansionPanel(title, expanded=(i == 0))
        text = QLabel(body)
        text.setWordWrap(True)
        text.setFont(font_for_role(TypescaleRole.BODY_MEDIUM))
        panel.add_content(text)
        lay.addWidget(panel)
        lay.addWidget(MdDivider())
    lay.addStretch(1)
    return page


def _build_search_bar() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Search bar"))
    bar = MdSearchBar(placeholder="Search your library", trailing_icon="mic")
    status = QLabel("(type and press Enter)")
    bar.submitted.connect(lambda q: status.setText(f"Searched: {q}"))
    lay.addWidget(bar)
    lay.addWidget(status)
    lay.addStretch(1)
    return page


def _build_button_group() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Button group (multi-select)"))
    multi = MdButtonGroup(multi=True)
    for label, icon in [("Bold", "format_bold"), ("Italic", "format_italic"),
                        ("Underline", "format_underlined")]:
        multi.add_button(label, icon=icon)
    lay.addWidget(multi)
    lay.addWidget(_section("Single-select"))
    single = MdButtonGroup(multi=False)
    for label in ["Day", "Week", "Month"]:
        single.add_button(label)
    single._buttons[0].setChecked(True)
    lay.addWidget(single)
    lay.addStretch(1)
    return page


def _build_fab_menu() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("FAB menu (click the FAB)"))
    menu = MdFabMenu(icon="add")
    for label, icon in [("Share", "share"), ("Edit", "edit"), ("Delete", "delete")]:
        menu.add_item(label, icon=icon)
    lay.addWidget(menu, 0, Qt.AlignmentFlag.AlignRight)
    lay.addStretch(1)
    return page


def _build_loading_indicator() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Loading indicator"))
    lay.addWidget(_row(MdLoadingIndicator(), MdLoadingIndicator(size=64)))
    lay.addStretch(1)
    return page


def _build_toolbar() -> QWidget:
    page = _page()
    lay = page.layout()
    lay.addWidget(_section("Floating toolbar"))
    floating = MdToolbar()
    for icon in ["format_bold", "format_italic", "format_underlined", "more_vert"]:
        floating.add_action(icon)
    lay.addWidget(floating, 0, Qt.AlignmentFlag.AlignLeft)
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
    ("Banner", _build_banner),
    ("Bottom sheet", _build_bottom_sheet),
    ("Button", _build_button),
    ("Button group", _build_button_group),
    ("Card", _build_card),
    ("Carousel", _build_carousel),
    ("Checkbox", _build_checkbox),
    ("Chips", _build_chips),
    ("Data table", _build_data_table),
    ("Date picker", _build_date_picker),
    ("Dialog", _build_dialog),
    ("Divider", _build_divider),
    ("Expansion panel", _build_expansion_panel),
    ("FAB", _build_fab),
    ("FAB menu", _build_fab_menu),
    ("Field", _build_field),
    ("Icon", _build_icon),
    ("Icon button", _build_icon_button),
    ("Item", _build_item),
    ("List", _build_list),
    ("Loading indicator", _build_loading_indicator),
    ("Menu", _build_menu),
    ("Navigation bar", _build_navigation_bar),
    ("Navigation drawer", _build_navigation_drawer),
    ("Navigation rail", _build_navigation_rail),
    ("Navigation tab", _build_navigation_tab),
    ("Progress", _build_progress),
    ("Radio", _build_radio),
    ("Range slider", _build_range_slider),
    ("Search bar", _build_search_bar),
    ("Segmented", _build_segmented),
    ("Select", _build_select),
    ("Side sheet", _build_side_sheet),
    ("Slider", _build_slider),
    ("Snackbar", _build_snackbar),
    ("Split button", _build_split_button),
    ("Switch", _build_switch),
    ("Tabs", _build_tabs),
    ("Text field", _build_text_field),
    ("Time picker", _build_time_picker),
    ("Toolbar", _build_toolbar),
    ("Tooltip", _build_tooltip),
    ("Top app bar", _build_top_app_bar),
    ("Typography", _build_typography),
]


# Per-component icon (Material Symbols ligature) + one-line description, used for
# the nav drawer destinations and each page's hero header — mirroring the
# material-web.dev catalog.
COMPONENT_META: dict[str, tuple[str, str]] = {
    "Badge": ("notifications", "Small status indicator overlaid on an anchor."),
    "Banner": ("campaign", "Prominent inline message with actions."),
    "Bottom sheet": ("vertical_align_bottom", "Sheet anchored to the bottom edge."),
    "Button": ("smart_button", "Five common button variants for actions."),
    "Button group": ("page_control", "Connected pills, single- or multi-select."),
    "Card": ("space_dashboard", "Container for related content and actions."),
    "Carousel": ("view_carousel", "Scrollable row of contained items."),
    "Checkbox": ("check_box", "Select one or more items from a set."),
    "Chips": ("label", "Compact elements for input, filters, and actions."),
    "Data table": ("table_rows", "Rows and columns of sortable data."),
    "Date picker": ("calendar_month", "Select a date from a calendar."),
    "Dialog": ("web_asset", "Modal surface for focused tasks and decisions."),
    "Divider": ("horizontal_rule", "Thin line that groups content."),
    "Expansion panel": ("expand_more", "Header that expands to reveal content."),
    "FAB": ("add_circle", "Floating action button for the primary action."),
    "FAB menu": ("menu_open", "A FAB that expands into labeled actions."),
    "Field": ("text_fields", "Chrome shared by text fields and selects."),
    "Icon": ("star", "Material Symbols icon rendering."),
    "Icon button": ("touch_app", "Icon-only buttons, optionally toggleable."),
    "Item": ("list_alt", "Content layout primitive with slots."),
    "List": ("list", "Vertical index of text and images."),
    "Loading indicator": ("progress_activity", "Morphing shape for short waits."),
    "Menu": ("menu", "Popup list of choices anchored to a control."),
    "Navigation bar": ("bottom_navigation", "Bottom bar switching destinations."),
    "Navigation drawer": ("menu_open", "Side panel of navigation destinations."),
    "Navigation rail": ("view_sidebar", "Vertical side rail switching destinations."),
    "Navigation tab": ("tab", "A single navigation destination."),
    "Progress": ("progress_activity", "Linear and circular progress."),
    "Radio": ("radio_button_checked", "Select one option from a set."),
    "Range slider": ("tune", "Select a range between two values."),
    "Search bar": ("search", "Field for searching app content."),
    "Segmented": ("splitscreen", "Connected toggle buttons for choices."),
    "Select": ("arrow_drop_down_circle", "Dropdown to pick from options."),
    "Side sheet": ("dock_to_left", "Side panel for supporting content."),
    "Slider": ("tune", "Select a value from a range."),
    "Snackbar": ("info", "Brief message with an optional action."),
    "Split button": ("more_horiz", "Primary action plus a dropdown."),
    "Switch": ("toggle_on", "Toggle the state of a single item."),
    "Tabs": ("tab", "Organize content across primary/secondary tabs."),
    "Text field": ("text_fields", "Let users enter and edit text."),
    "Time picker": ("schedule", "Select a time on a clock dial."),
    "Toolbar": ("toolbar", "Floating or docked row of actions."),
    "Tooltip": ("chat_bubble", "Brief label shown on hover or focus."),
    "Top app bar": ("view_day", "Title and actions at the top of a screen."),
    "Typography": ("format_size", "The Material 3 type scale."),
}

# Theme presets cycled by the app-bar palette button. "Catalog" (the
# material-web.dev default amber/olive theme) is first, so the gallery opens
# matching the catalog; clicking the palette button cycles to "Baseline" and back.
_PRESET_NAMES = ["Catalog", "Baseline"]


def _hero(label: str) -> MdCard:
    """A catalog-style hero header: component name + description in a surface."""
    _icon, desc = COMPONENT_META.get(label, ("widgets", ""))
    card = MdCard(variant=CardVariant.FILLED)
    title = _themed_text_label(label, role=ColorRole.ON_SURFACE,
                               typescale=TypescaleRole.HEADLINE_MEDIUM)
    card.add_widget(title)
    if desc:
        d = _themed_text_label(desc, role=ColorRole.ON_SURFACE_VARIANT,
                               typescale=TypescaleRole.BODY_MEDIUM)
        d.setWordWrap(True)
        card.add_widget(d)
    return card


_DRAWER_W = 360  # matches MdNavigationDrawer width
_SCRIM_OPACITY = 0.32


class _NavModal(QWidget):
    """An animated modal navigation drawer overlay (compact/medium widths): the
    drawer slides in from the left while the scrim fades in (M3 emphasized
    motion). Dismisses on a scrim click or destination selection."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setFixedWidth(_DRAWER_W)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._t = 0.0  # 0 = closed (off-screen left), 1 = fully open
        self._opened = False
        self._anim = QVariantAnimation(self)
        self._anim.valueChanged.connect(self._set_t)
        self._anim.finished.connect(self._on_anim_finished)
        self.hide()

    def host(self, drawer: QWidget) -> None:
        self._scroll.setWidget(drawer)

    def release(self) -> QWidget | None:
        return self._scroll.takeWidget()

    def is_open(self) -> bool:
        return self._opened

    # -- open / close (animated) ------------------------------------------

    def open(self) -> None:
        if self._opened:
            return
        self._opened = True
        self.setGeometry(self.parentWidget().rect())
        self._reposition()
        self.raise_()
        self.show()
        self._animate_to(1.0, Duration.LONG1, Easing.EMPHASIZED_DECELERATE)

    def close(self) -> None:
        if not self._opened:
            return
        self._opened = False
        self._animate_to(0.0, Duration.SHORT4, Easing.EMPHASIZED_ACCELERATE)

    def _animate_to(self, target: float, duration: Duration, easing: Easing) -> None:
        self._anim.stop()
        if not MOTION_ENABLED:
            self._set_t(target)
            self._on_anim_finished()
            return
        self._anim.setStartValue(self._t)
        self._anim.setEndValue(target)
        self._anim.setDuration(duration_ms(duration))
        self._anim.setEasingCurve(easing_curve(easing))
        self._anim.start()

    def _set_t(self, value) -> None:
        self._t = float(value)
        self._reposition()
        self.update()  # repaint scrim at new opacity

    def _on_anim_finished(self) -> None:
        if not self._opened and self._t <= 0.0:
            self.hide()  # fully closed — remove the overlay

    def reset(self) -> None:
        """Snap closed without animation (used when leaving compact mode)."""
        self._anim.stop()
        self._opened = False
        self._t = 0.0
        self.hide()

    def _reposition(self) -> None:
        # Slide the panel in from the left: x in [-_DRAWER_W, 0] as t goes 0->1.
        x = round(_DRAWER_W * (self._t - 1.0))
        self._scroll.setGeometry(x, 0, _DRAWER_W, self.height())

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._reposition()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.position().x() > _DRAWER_W:  # clicked the scrim
            self.close()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        scrim = QColor(ThemeManager.instance().color(ColorRole.SCRIM))
        scrim.setAlphaF(_SCRIM_OPACITY * self._t)  # fade with the slide
        painter.fillRect(self.rect(), scrim)


class GalleryWindow(QWidget):
    """Browsable gallery of all Material Qt components (catalog-style)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Gallery")
        self._labels = [label for label, _ in _COMPONENTS]
        ThemeManager.instance().themeChanged.connect(self._restyle)
        self._preset_idx = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # -- App bar: title + theme toggle + brand-color (palette) action ----
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 8, 16, 8)
        hl.setSpacing(4)
        # Hamburger appears only at compact/medium widths (modal drawer).
        self._hamburger = MdIconButton("menu")
        self._hamburger.clicked.connect(self._toggle_nav)
        self._hamburger.hide()
        hl.addWidget(self._hamburger)
        title = QLabel("Material Qt")
        title.setFont(font_for_role(TypescaleRole.TITLE_LARGE))
        hl.addWidget(title)
        hl.addStretch(1)
        self._theme_btn = MdIconButton("dark_mode")
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._palette_btn = MdIconButton("palette")
        self._palette_btn.clicked.connect(self._cycle_brand)
        hl.addWidget(self._theme_btn)
        hl.addWidget(self._palette_btn)
        root.addWidget(header)
        self._header = header

        # -- Body: nav drawer (scrollable) + content stack -------------------
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._drawer = MdNavigationDrawer(headline="Components")
        self._stack = QStackedWidget()
        for label, builder in _COMPONENTS:
            icon, _desc = COMPONENT_META.get(label, ("widgets", ""))
            self._drawer.add_destination(label, icon=icon)
            # Each page = hero header + the component showcase, scrollable.
            page = QWidget()
            pl = QVBoxLayout(page)
            pl.setContentsMargins(28, 24, 28, 24)
            pl.setSpacing(16)
            pl.addWidget(_hero(label))
            pl.addWidget(builder(), 1)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            self._stack.addWidget(scroll)
        self._drawer.changed.connect(self._stack.setCurrentIndex)
        self._drawer.changed.connect(self._on_nav_changed)

        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setWidget(self._drawer)
        nav_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        # Width is animated on breakpoint changes, so cap (not fix) it.
        nav_scroll.setMinimumWidth(0)
        nav_scroll.setMaximumWidth(_DRAWER_W)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._nav_scroll = nav_scroll
        self._nav_anim = QPropertyAnimation(nav_scroll, b"maximumWidth", self)
        self._nav_anim.finished.connect(self._on_nav_anim_finished)

        body.addWidget(nav_scroll)
        body.addWidget(self._stack, 1)
        root.addLayout(body, 1)

        # Responsive nav: persistent drawer at expanded+ (>=840dp), modal drawer
        # behind a hamburger at compact/medium (per the M3 breakpoints).
        self._modal = _NavModal(self)
        self._compact: bool | None = None
        self._responsive = ResponsiveHelper(self)
        self._responsive.sizeClassChanged.connect(lambda *_: self._apply_responsive())

        # Open matching the material-web.dev catalog theme by default.
        self._apply_preset(_PRESET_NAMES[0])
        self._restyle()
        self._apply_responsive(animate=False)

    # -- selection (also used by tests) ------------------------------------

    def select(self, index: int) -> None:
        self._drawer._items[index].setChecked(True)

    # -- responsive nav ----------------------------------------------------

    def _apply_responsive(self, animate: bool = True) -> None:
        """Persistent drawer at expanded+ widths; modal + hamburger below.

        Crossing the breakpoint animates the persistent drawer's width (slide
        in/out) rather than popping.
        """
        compact = size_class_for(self.width()) in (
            WindowSizeClass.COMPACT, WindowSizeClass.MEDIUM
        )
        if compact == self._compact:
            return
        self._compact = compact
        self._nav_anim.stop()
        if compact:
            # Collapse the side drawer to 0 width, then move it into the modal.
            self._hamburger.show()
            self._animate_nav_to(0, animate)
        else:
            # Bring the drawer back into the side scroll and expand it in.
            drawer = self._modal.release()
            if drawer is not None:
                self._nav_scroll.setWidget(drawer)
            self._modal.reset()
            self._hamburger.hide()
            self._nav_scroll.setMaximumWidth(0)  # start collapsed, then slide in
            self._nav_scroll.show()
            self._animate_nav_to(_DRAWER_W, animate)

    def _animate_nav_to(self, target: int, animate: bool) -> None:
        if not (animate and MOTION_ENABLED):
            self._nav_scroll.setMaximumWidth(target)
            self._on_nav_anim_finished()
            return
        collapsing = target == 0
        self._nav_anim.setStartValue(self._nav_scroll.maximumWidth())
        self._nav_anim.setEndValue(target)
        self._nav_anim.setDuration(
            duration_ms(Duration.SHORT4 if collapsing else Duration.LONG1)
        )
        self._nav_anim.setEasingCurve(easing_curve(
            Easing.EMPHASIZED_ACCELERATE if collapsing else Easing.EMPHASIZED_DECELERATE
        ))
        self._nav_anim.start()

    def _on_nav_anim_finished(self) -> None:
        # When the side drawer has finished collapsing, hide it and hand the
        # drawer widget to the modal for compact-width use.
        if self._compact and self._nav_scroll.maximumWidth() == 0:
            self._nav_scroll.hide()
            drawer = self._nav_scroll.takeWidget()
            if drawer is not None:
                self._modal.host(drawer)
            self._nav_scroll.setMaximumWidth(_DRAWER_W)  # reset for next expand

    def _toggle_nav(self) -> None:
        if self._modal.is_open():
            self._modal.close()
        else:
            self._modal.open()

    def _on_nav_changed(self, _index: int) -> None:
        # Selecting a destination dismisses the modal drawer (compact mode).
        if self._modal.is_open():
            self._modal.close()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        modal = getattr(self, "_modal", None)
        if modal is not None and modal.isVisible():
            modal.setGeometry(self.rect())

    def _toggle_theme(self) -> None:
        # Flip relative to the *actual* current theme (which may start in SYSTEM
        # mode resolving to dark), so the first click always changes the theme.
        ThemeManager.instance().toggle_light_dark()

    def _apply_preset(self, name: str) -> None:
        light, dark = PRESETS[name]
        ThemeManager.instance().set_palette(light, dark)

    def _cycle_brand(self) -> None:
        # Cycle the full theme preset (Catalog <-> Baseline), reskinning every
        # component at once — like the catalog's theme control.
        self._preset_idx = (self._preset_idx + 1) % len(_PRESET_NAMES)
        self._apply_preset(_PRESET_NAMES[self._preset_idx])

    def _restyle(self) -> None:
        theme = ThemeManager.instance()
        dark = theme.is_dark
        self._theme_btn.set_icon("light_mode" if dark else "dark_mode")
        bg = theme.color(ColorRole.SURFACE).name()
        bar_bg = theme.color(ColorRole.SURFACE_CONTAINER).name()
        self.setStyleSheet(f"GalleryWindow {{ background: {bg}; }}")
        self._header.setStyleSheet(f"background: {bar_bg};")
        self._nav_scroll.setStyleSheet("QScrollArea { border: none; }")


def main() -> int:
    app = QApplication(sys.argv)
    w = GalleryWindow()
    w.resize(900, 620)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
