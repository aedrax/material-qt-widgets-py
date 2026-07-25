"""Material 3 tabs for QtWidgets.

Ports Material Web's ``tabs/`` — :class:`MdTabs` holding :class:`MdTab` buttons
with an animated ``primary`` active indicator that slides to the selected tab.
Primary tabs stack an optional icon above the label with a short rounded
indicator under the label; secondary tabs are label-only with a full-width
indicator. Active label/icon uses ``primary`` (primary) / ``on-surface``
(secondary); inactive uses ``on-surface-variant``.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii, ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

from PySide6.QtCore import QVariantAnimation

_HEIGHT = 48
_DIVIDER_ROLE = ColorRole.SURFACE_CONTAINER_HIGHEST
_ICON = 24
_PAD = 16
_INDICATOR_H = 3


class MdTab(MaterialWidgetMixin, QAbstractButton):
    """A single tab."""

    def __init__(self, label: str = "", parent: QWidget | None = None, *,
                 icon: str = "", secondary: bool = False) -> None:
        super().__init__(parent)
        self.setText(label)
        self._icon = icon
        self._secondary = secondary
        self._label_color: QColor | None = None
        self._unselected_label_color: QColor | None = None
        self.setCheckable(True)
        self._init_material(
            shape=ShapeScale.NONE,
            typescale=TypescaleRole.TITLE_SMALL,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.PRIMARY,
            surface_role=ColorRole.SURFACE,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggled.connect(lambda *_: self.update())

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = _PAD * 2 + metrics.horizontalAdvance(self.text())
        return QSize(max(w, 90), _HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(72, _HEIGHT)

    def label_width(self) -> int:
        return QFontMetrics(self.font()).horizontalAdvance(self.text())

    def set_label_colors(self, selected: QColor | None,
                         unselected: QColor | None) -> None:
        """Override the active / inactive label+icon colours (Flutter
        ``labelColor`` / ``unselectedLabelColor``). ``None`` restores the role
        default."""
        self._label_color = selected
        self._unselected_label_color = unselected
        self.update()

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        active = self.isChecked()
        if active:
            role = ColorRole.ON_SURFACE if self._secondary else ColorRole.PRIMARY
            override = self._label_color
        else:
            role = ColorRole.ON_SURFACE_VARIANT
            override = self._unselected_label_color
        color = override if override is not None else theme.color(role)

        if self._icon and not self._secondary:
            # Stacked: icon above label.
            font = material_symbols_font(_ICON, filled=active)
            if font is not None:
                painter.setFont(font)
                painter.setPen(color)
                painter.drawText(QRectF(0, 4, self.width(), _ICON),
                                 Qt.AlignmentFlag.AlignCenter, self._icon)
            painter.setFont(self.font())
            painter.setPen(color)
            painter.drawText(QRectF(0, 4 + _ICON, self.width(), self.height() - _ICON - 8),
                             Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                             self.text())
        else:
            painter.setFont(self.font())
            painter.setPen(color)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class _TabStrip(QWidget):
    """Inner row that lays out the tabs and paints the divider + active
    indicator. Hosting the indicator on the same widget as the tabs means it
    tracks the scroll offset automatically when the strip scrolls inside
    :class:`MdTabs`."""

    def __init__(self, owner: MdTabs) -> None:
        super().__init__(owner)
        self._owner = owner
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self.setFixedHeight(_HEIGHT)

    def resizeEvent(self, event) -> None:  # noqa: N802
        # The strip resizes once its layout gives the tabs their real geometry;
        # that is the correct moment to (re)place the indicator under the active
        # tab. MdTabs.resizeEvent fires too early — before this inner layout pass.
        super().resizeEvent(event)
        self._owner._reposition_indicator()

    def paintEvent(self, event) -> None:  # noqa: N802
        owner = self._owner
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        # Bottom divider line under the whole strip.
        pen = QPen(owner._divider_color or theme.color(_DIVIDER_ROLE))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        y = self.height() - 0.5
        painter.drawLine(QPointF(0, y), QPointF(self.width(), y))
        # Active indicator — primary tabs use a 3px bar, secondary tabs 2px
        # (per the navigation-tab tokens). indicator_weight overrides the height.
        if owner._ind_w > 0:
            ind_h = owner._indicator_weight
            if ind_h <= 0:
                ind_h = 2.0 if owner._secondary else float(_INDICATOR_H)
            x = owner._ind - owner._ind_w / 2.0
            rect = QRectF(x, self.height() - ind_h, owner._ind_w, ind_h)
            radii = CornerRadii(ind_h, ind_h, 0.0, 0.0)
            color = owner._indicator_color or theme.color(ColorRole.PRIMARY)
            painter.fillPath(rounded_path(rect, radii), color)


class MdTabs(QWidget):
    """A tab bar with an animated active indicator."""

    changed = Signal(int)  # active index

    def __init__(self, parent: QWidget | None = None, *, secondary: bool = False,
                 scrollable: bool = False) -> None:
        super().__init__(parent)
        self._secondary = secondary
        self._scrollable = scrollable
        self._tabs: list[MdTab] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        # Theme overrides (None = use the role default).
        self._indicator_color: QColor | None = None
        self._indicator_weight = 0.0  # 0 = role default (3px / 2px)
        self._indicator_size = "tab" if secondary else "label"
        self._label_color: QColor | None = None
        self._unselected_label_color: QColor | None = None
        self._divider_color: QColor | None = None

        self._strip = _TabStrip(self)
        self._lay = self._strip._lay  # tabs live in the strip's HBox
        self._scroll = QScrollArea(self)
        self._scroll.setWidget(self._strip)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.viewport().setStyleSheet("background: transparent;")
        self._strip.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._scroll)
        self.setFixedHeight(_HEIGHT)

        self._ind = 0.0  # current indicator center x (strip coords)
        self._ind_w = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.SHORT4))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._on_anim)
        # Layout changes during the slide are skipped by _reposition_indicator;
        # re-snap once the animation lands so a mid-animation resize can't
        # leave the indicator misplaced until the next selection.
        self._anim.finished.connect(self._on_anim_finished)
        self._start = (0.0, 0.0)
        self._target = (0.0, 0.0)
        self._apply_scrollable()
        ThemeManager.instance().themeChanged.connect(self._strip.update)

    def add_tab(self, label: str, *, icon: str = "") -> MdTab:
        tab = MdTab(label, icon=icon, secondary=self._secondary)
        self._apply_tab_colors(tab)
        if self._scrollable:
            tab.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._group.addButton(tab, len(self._tabs))
        self._lay.addWidget(tab)
        self._tabs.append(tab)
        tab.toggled.connect(lambda on, t=tab: on and self._select(t))
        if len(self._tabs) == 1:
            tab.setChecked(True)
        return tab

    # -- selection (Flutter ``controller`` selected index / ``onTap``) ------

    @property
    def selected_index(self) -> int:
        """Index of the active tab, or ``-1`` if none."""
        return self._group.checkedId()

    @selected_index.setter
    def selected_index(self, index: int) -> None:
        self.set_selected_index(index)

    def set_selected_index(self, index: int) -> None:
        """Programmatically select the tab at ``index``."""
        button = self._group.button(index)
        if button is not None:
            button.setChecked(True)

    # -- scrollable (Flutter ``isScrollable``) ------------------------------

    @property
    def is_scrollable(self) -> bool:
        return self._scrollable

    def set_scrollable(self, scrollable: bool) -> None:
        if scrollable == self._scrollable:
            return
        self._scrollable = scrollable
        self._apply_scrollable()

    def _apply_scrollable(self) -> None:
        policy = (QSizePolicy.Policy.Fixed if self._scrollable
                  else QSizePolicy.Policy.Expanding)
        for tab in self._tabs:
            tab.setSizePolicy(policy, QSizePolicy.Policy.Fixed)
        # Non-scrollable tabs fill the width; scrollable tabs keep natural
        # width and left-align, overflowing into the scroll area.
        if self._scrollable:
            self._strip.setMinimumWidth(0)
            self._strip.setMaximumWidth(16777215)
        self._strip.updateGeometry()

    # -- theme overrides (Flutter indicator/label colours) ------------------

    def set_indicator_color(self, color: QColor | None) -> None:
        self._indicator_color = color
        self._strip.update()

    def set_indicator_weight(self, weight: float) -> None:
        """Indicator thickness in px (Flutter ``indicatorWeight``); 0 restores
        the role default (3px primary / 2px secondary)."""
        self._indicator_weight = weight
        self._strip.update()

    def set_indicator_size(self, size: str) -> None:
        """``"tab"`` (full tab width) or ``"label"`` (label width) — Flutter
        ``indicatorSize``."""
        self._indicator_size = size
        self._reposition_indicator()

    def set_label_color(self, color: QColor | None) -> None:
        self._label_color = color
        for tab in self._tabs:
            self._apply_tab_colors(tab)

    def set_unselected_label_color(self, color: QColor | None) -> None:
        self._unselected_label_color = color
        for tab in self._tabs:
            self._apply_tab_colors(tab)

    def set_divider_color(self, color: QColor | None) -> None:
        self._divider_color = color
        self._strip.update()

    def _apply_tab_colors(self, tab: MdTab) -> None:
        tab.set_label_colors(self._label_color, self._unselected_label_color)

    # -- indicator geometry / animation -------------------------------------

    def _indicator_target(self, tab: MdTab) -> tuple[float, float]:
        geo = tab.geometry()
        if self._indicator_size == "tab":
            return geo.center().x() + 0.5, geo.width()
        w = min(tab.label_width() + 16, geo.width())
        return geo.center().x() + 0.5, w

    def _reposition_indicator(self) -> None:
        # Snap the indicator under the active tab after a layout change. Skip
        # while a selection animation is running so we don't cut it short.
        if self._anim.state() == QVariantAnimation.State.Running:
            return
        checked = self._group.checkedButton()
        if checked is not None:
            self._ind, self._ind_w = self._indicator_target(checked)
            self._strip.update()

    def _select(self, tab: MdTab) -> None:
        self.changed.emit(self._tabs.index(tab))
        cx, w = self._indicator_target(tab)
        self._ensure_visible(tab)
        if not MOTION_ENABLED or self._ind_w == 0.0 or not self.isVisible():
            self._ind, self._ind_w = cx, w
            self._strip.update()
            return
        self._anim.stop()
        self._start = (self._ind, self._ind_w)
        self._target = (cx, w)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _ensure_visible(self, tab: MdTab) -> None:
        if self._scrollable:
            self._scroll.ensureWidgetVisible(tab, xmargin=24, ymargin=0)

    def _on_anim(self, t) -> None:
        t = float(t)
        (sx, sw), (tx, tw) = self._start, self._target
        self._ind = sx + (tx - sx) * t
        self._ind_w = sw + (tw - sw) * t
        self._strip.update()

    def _on_anim_finished(self) -> None:
        if not isValid(self) or not isValid(self._strip):
            return
        self._reposition_indicator()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        # Initialise the indicator under the active tab once laid out.
        checked = self._group.checkedButton()
        if checked is not None and self._ind_w == 0.0:
            self._ind, self._ind_w = self._indicator_target(checked)
            self._strip.update()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._reposition_indicator()


__all__ = ["MdTab", "MdTabs"]
