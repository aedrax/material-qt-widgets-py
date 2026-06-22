"""Material 3 top app bar for QtWidgets.

Ports the Material 3 top app bar (cf. Flutter's ``AppBar`` and the M3
scroll-under configs). Four variants are supported:

* ``CENTER`` — 64px, centered ``title-large`` title;
* ``SMALL``  — 64px, leading-aligned ``title-large`` title;
* ``MEDIUM`` — 112px, ``headline-small`` title on a second row;
* ``LARGE``  — 152px, ``headline-medium`` title on a second row.

The container uses the ``surface`` role; the title uses ``on-surface``. A leading
widget (typically a navigation :class:`MdIconButton`) sits at the start and
trailing action icon buttons are appended with :meth:`add_action`.

Scroll-under collapse
---------------------
The ``MEDIUM`` and ``LARGE`` variants collapse to 64px as content scrolls under
them (cf. Flutter's ``_MediumScrollUnderFlexibleConfig`` /
``_LargeScrollUnderFlexibleConfig``). Drive it directly with
:meth:`set_collapse_fraction` (``0.0`` expanded, ``1.0`` collapsed) or wire it to
a scroll view with :meth:`attach_scroll_area`. As the bar collapses the bottom
``headline`` title cross-fades out while a ``title-large`` title fades in at the
top-row (small-variant) position, the container tints from ``surface`` to
``surface-container``, and the bar rises from elevation 0 to
``scrolled_under_elevation`` (M3 level 3 by default) — matching M3 scroll-under
behavior (cf. Flutter ``AppBar.scrolledUnderElevation``).

Bottom slot
-----------
A persistent widget (typically a tab bar; cf. Flutter ``AppBar.bottom``) can be
hosted below the toolbar rows via the ``bottom`` constructor kwarg or
:meth:`set_bottom`; the bar's height grows to fit it. The bottom slot is not
affected by scroll-under collapse.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..iconbutton import MdIconButton

_ROW_HEIGHT = 64
_PAD = 16


class TopAppBarVariant(Enum):
    """Top app bar layout variants."""

    CENTER = "center"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


_HEIGHTS = {
    TopAppBarVariant.CENTER: 64,
    TopAppBarVariant.SMALL: 64,
    TopAppBarVariant.MEDIUM: 112,
    TopAppBarVariant.LARGE: 152,
}

_TITLE_TYPESCALE = {
    TopAppBarVariant.CENTER: TypescaleRole.TITLE_LARGE,
    TopAppBarVariant.SMALL: TypescaleRole.TITLE_LARGE,
    TopAppBarVariant.MEDIUM: TypescaleRole.HEADLINE_SMALL,
    TopAppBarVariant.LARGE: TypescaleRole.HEADLINE_MEDIUM,
}

_TWO_ROW = (TopAppBarVariant.MEDIUM, TopAppBarVariant.LARGE)


def _lerp_color(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(
        round(a.red() + (b.red() - a.red()) * t),
        round(a.green() + (b.green() - a.green()) * t),
        round(a.blue() + (b.blue() - a.blue()) * t),
    )


def _with_alpha(color: QColor, alpha: float) -> str:
    """Return ``color`` at ``alpha`` (0..1) as a ``#AARRGGBB`` string.

    Hand-built ``rgba()`` strings are unreliable across Qt versions (alpha units
    vary); ``HexArgb`` is unambiguous.
    """
    c = QColor(color)
    c.setAlphaF(max(0.0, min(1.0, alpha)))
    return c.name(QColor.NameFormat.HexArgb)


class MdTopAppBar(MaterialWidgetMixin, QWidget):
    """A Material 3 top app bar."""

    def __init__(
        self,
        title: str = "",
        parent: QWidget | None = None,
        *,
        variant: TopAppBarVariant = TopAppBarVariant.SMALL,
        leading: QWidget | None = None,
        toolbar_height: int | None = None,
        bottom: QWidget | None = None,
        scrolled_under_elevation: ElevationLevel | int = ElevationLevel.LEVEL3,
    ) -> None:
        super().__init__(parent)
        self._variant = variant
        self._leading = leading
        # Per-row toolbar height; Flutter's ``AppBar.toolbarHeight`` overrides the
        # 64px default and shifts every variant's expanded height by the delta.
        self._row_height = _ROW_HEIGHT if toolbar_height is None else int(toolbar_height)
        self._expanded_h = _HEIGHTS[variant] + (self._row_height - _ROW_HEIGHT)
        self._collapse_distance = self._expanded_h - self._row_height  # 0 single-row
        self._collapse_t = 0.0
        self._scrolled_under_elevation = ElevationLevel(int(scrolled_under_elevation))

        # Optional persistent bottom slot (cf. Flutter ``AppBar.bottom``), e.g. a
        # tab bar. It sits below the toolbar rows and is not collapsed.
        self._bottom = bottom
        self._bottom_h = max(0, bottom.sizeHint().height()) if bottom is not None else 0

        self._title = QLabel(title)
        self._title.setFont(font_for_role(_TITLE_TYPESCALE[variant]))

        # Two-row variants get a second, top-row title (title-large) that fades
        # in as the bar collapses, landing where a SMALL variant's title sits.
        self._collapsed_title: QLabel | None = None
        if variant in _TWO_ROW:
            self._collapsed_title = QLabel(title)
            self._collapsed_title.setFont(font_for_role(TypescaleRole.TITLE_LARGE))

        # The action buttons share a trailing layout regardless of variant.
        self._actions_lay = QHBoxLayout()
        self._actions_lay.setContentsMargins(0, 0, 0, 0)
        self._actions_lay.setSpacing(0)

        self._build_layout()

        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        self.setFixedHeight(self._expanded_h + self._bottom_h)

        self._restyle_titles()
        ThemeManager.instance().themeChanged.connect(self._restyle_titles)

    # -- layout ------------------------------------------------------------

    def _build_layout(self) -> None:
        # The toolbar rows live in a content holder whose height is what scroll
        # collapse animates; an optional persistent bottom slot is stacked under
        # it (and is *not* collapsed).
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._content = QWidget(self)
        self._content.setFixedHeight(self._expanded_h)
        self._build_content(self._content)
        outer.addWidget(self._content)

        if self._bottom is not None:
            outer.addWidget(self._bottom)
        else:
            outer.addStretch(0)

    def _build_content(self, holder: QWidget) -> None:
        if self._variant in _TWO_ROW:
            # Top row: leading + collapsed title at the start, actions at the end.
            inner = QVBoxLayout(holder)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.setSpacing(0)

            top = QHBoxLayout()
            top.setContentsMargins(_PAD, 0, _PAD, 0)
            top.setSpacing(0)
            top.addWidget(self._first_row_leading())
            if self._leading is not None:
                top.addSpacing(_PAD)
            assert self._collapsed_title is not None  # always set for two-row
            top.addWidget(self._collapsed_title)
            top.addStretch(1)
            top.addLayout(self._actions_lay)
            top_holder = QWidget()
            top_holder.setLayout(top)
            top_holder.setFixedHeight(self._row_height)

            title_row = QHBoxLayout()
            title_row.setContentsMargins(_PAD, 0, _PAD, _PAD)
            title_row.addWidget(self._title)
            title_row.addStretch(1)

            inner.addWidget(top_holder)
            inner.addLayout(title_row)
            return

        # Single-row (small / center): leading | title | actions.
        row = QHBoxLayout(holder)
        row.setContentsMargins(_PAD, 0, _PAD, 0)
        row.setSpacing(0)
        row.addWidget(self._first_row_leading())
        centered = self._variant is TopAppBarVariant.CENTER
        if centered:
            row.addStretch(1)
        elif self._leading is not None:
            row.addSpacing(_PAD)
        row.addWidget(self._title)
        row.addStretch(1)
        row.addLayout(self._actions_lay)

    def _first_row_leading(self) -> QWidget:
        if self._leading is not None:
            return self._leading
        spacer = QWidget()
        spacer.setFixedWidth(0)
        return spacer

    def _restyle_titles(self) -> None:
        on_surface = ThemeManager.instance().color(ColorRole.ON_SURFACE)
        if self._collapsed_title is not None:
            # Cross-fade: headline fades out, title-large fades in, as t -> 1.
            self._title.setStyleSheet(
                f"color: {_with_alpha(on_surface, 1.0 - self._collapse_t)};"
            )
            self._collapsed_title.setStyleSheet(
                f"color: {_with_alpha(on_surface, self._collapse_t)};"
            )
        else:
            self._title.setStyleSheet(f"color: {on_surface.name()};")

    # -- public API --------------------------------------------------------

    def set_title(self, title: str) -> None:
        self._title.setText(title)
        if self._collapsed_title is not None:
            self._collapsed_title.setText(title)

    def add_action(self, icon: str = "", *, toggle: bool = False) -> MdIconButton:
        """Append a trailing action icon button and return it."""
        button = MdIconButton(icon, toggle=toggle)
        self._actions_lay.addWidget(button)
        return button

    def set_bottom(self, widget: QWidget | None) -> None:
        """Set (or clear) the persistent bottom slot, e.g. a tab bar.

        Mirrors Flutter's ``AppBar.bottom``; the bar's height grows to fit it.
        """
        outer = self.layout()
        # Slot 0 is always the content holder; slot 1 is the bottom widget or a
        # placeholder stretch. Remove slot 1 and replace it.
        if outer.count() > 1:
            item = outer.takeAt(1)
            old = item.widget()
            if old is not None:
                old.setParent(None)
        self._bottom = widget
        self._bottom_h = max(0, widget.sizeHint().height()) if widget is not None else 0
        if widget is not None:
            outer.addWidget(widget)
        else:
            outer.addStretch(0)
        self.setFixedHeight(self._current_total())

    def _current_total(self) -> int:
        content_h = round(self._expanded_h - self._collapse_distance * self._collapse_t)
        return content_h + self._bottom_h

    def set_collapse_fraction(self, t: float) -> None:
        """Set the scroll-under collapse, ``0.0`` expanded .. ``1.0`` collapsed.

        No-op for the single-row CENTER/SMALL variants. Out-of-range values are
        clamped. As the bar collapses it rises from elevation 0 to
        ``scrolled_under_elevation`` (cf. Flutter ``AppBar.scrolledUnderElevation``).
        """
        t = max(0.0, min(1.0, t))
        self._collapse_t = t
        if self._collapse_distance:
            content_h = round(self._expanded_h - self._collapse_distance * t)
            self._content.setFixedHeight(content_h)
            self.setFixedHeight(content_h + self._bottom_h)
            # Scroll-under elevation: 0 when expanded, target when scrolled under.
            # Only re-apply on change — apply_elevation rebuilds the shadow effect.
            level = self._scrolled_under_elevation if t > 0.0 else ElevationLevel.LEVEL0
            if level != self._elevation:
                self.set_elevation(level)
        self._restyle_titles()
        self.update()

    @property
    def collapse_fraction(self) -> float:
        return self._collapse_t

    def attach_scroll_area(self, scroll_area: QScrollArea) -> None:
        """Drive collapse from a scroll area's vertical scroll position.

        No-op for single-row variants (their collapse distance is zero).
        """
        if not self._collapse_distance:
            return
        bar = scroll_area.verticalScrollBar()
        bar.valueChanged.connect(
            lambda v: self.set_collapse_fraction(v / self._collapse_distance)
        )
        self.set_collapse_fraction(bar.value() / self._collapse_distance)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        # M3 scroll-under: container tints surface -> surface-container.
        fill = _lerp_color(
            theme.color(ColorRole.SURFACE),
            theme.color(ColorRole.SURFACE_CONTAINER),
            self._collapse_t,
        )
        painter.fillPath(rounded_path(QRectF(self.rect()), self.radii), fill)


__all__ = ["MdTopAppBar", "TopAppBarVariant"]
