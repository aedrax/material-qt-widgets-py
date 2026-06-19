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
top-row (small-variant) position, and the container tints from ``surface`` to
``surface-container`` — matching M3 scroll-under behavior.
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
    ) -> None:
        super().__init__(parent)
        self._variant = variant
        self._leading = leading
        self._expanded_h = _HEIGHTS[variant]
        self._collapse_distance = self._expanded_h - _ROW_HEIGHT  # 0 for single-row
        self._collapse_t = 0.0

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
        self.setFixedHeight(self._expanded_h)

        self._restyle_titles()
        ThemeManager.instance().themeChanged.connect(self._restyle_titles)

    # -- layout ------------------------------------------------------------

    def _build_layout(self) -> None:
        if self._variant in _TWO_ROW:
            # Top row: leading + collapsed title at the start, actions at the end.
            outer = QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

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
            top_holder.setFixedHeight(_ROW_HEIGHT)

            title_row = QHBoxLayout()
            title_row.setContentsMargins(_PAD, 0, _PAD, _PAD)
            title_row.addWidget(self._title)
            title_row.addStretch(1)

            outer.addWidget(top_holder)
            outer.addLayout(title_row)
            return

        # Single-row (small / center): leading | title | actions.
        row = QHBoxLayout(self)
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

    def set_collapse_fraction(self, t: float) -> None:
        """Set the scroll-under collapse, ``0.0`` expanded .. ``1.0`` collapsed.

        No-op for the single-row CENTER/SMALL variants. Out-of-range values are
        clamped.
        """
        t = max(0.0, min(1.0, t))
        self._collapse_t = t
        if self._collapse_distance:
            self.setFixedHeight(round(self._expanded_h - self._collapse_distance * t))
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
