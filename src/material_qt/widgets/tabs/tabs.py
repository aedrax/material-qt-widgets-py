"""Material 3 tabs for QtWidgets.

Ports Material Web's ``tabs/`` — :class:`MdTabs` holding :class:`MdTab` buttons
with an animated ``primary`` active indicator that slides to the selected tab.
Primary tabs stack an optional icon above the label with a short rounded
indicator under the label; secondary tabs are label-only with a full-width
indicator. Active label/icon uses ``primary`` (primary) / ``on-surface``
(secondary); inactive uses ``on-surface-variant``.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

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
        else:
            role = ColorRole.ON_SURFACE_VARIANT
        color = theme.color(role)

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


class MdTabs(QWidget):
    """A tab bar with an animated active indicator."""

    changed = Signal(int)  # active index

    def __init__(self, parent: QWidget | None = None, *, secondary: bool = False) -> None:
        super().__init__(parent)
        self._secondary = secondary
        self._tabs: list[MdTab] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self.setFixedHeight(_HEIGHT)
        self._ind = 0.0  # current indicator center x
        self._ind_w = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.SHORT4))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._on_anim)
        self._start = (0.0, 0.0)
        self._target = (0.0, 0.0)
        ThemeManager.instance().themeChanged.connect(self.update)

    def add_tab(self, label: str, *, icon: str = "") -> MdTab:
        tab = MdTab(label, icon=icon, secondary=self._secondary)
        self._group.addButton(tab, len(self._tabs))
        self._lay.addWidget(tab)
        self._tabs.append(tab)
        tab.toggled.connect(lambda on, t=tab: on and self._select(t))
        if len(self._tabs) == 1:
            tab.setChecked(True)
        return tab

    def _indicator_target(self, tab: MdTab) -> tuple[float, float]:
        geo = tab.geometry()
        if self._secondary:
            return geo.center().x() + 0.5, geo.width()
        w = min(tab.label_width() + 16, geo.width())
        return geo.center().x() + 0.5, w

    def _select(self, tab: MdTab) -> None:
        self.changed.emit(self._tabs.index(tab))
        cx, w = self._indicator_target(tab)
        if not MOTION_ENABLED or self._ind_w == 0.0 or not self.isVisible():
            self._ind, self._ind_w = cx, w
            self.update()
            return
        self._anim.stop()
        self._start = (self._ind, self._ind_w)
        self._target = (cx, w)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _on_anim(self, t) -> None:
        t = float(t)
        (sx, sw), (tx, tw) = self._start, self._target
        self._ind = sx + (tx - sx) * t
        self._ind_w = sw + (tw - sw) * t
        self.update()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        # Initialise the indicator under the active tab once laid out.
        checked = self._group.checkedButton()
        if checked is not None and self._ind_w == 0.0:
            self._ind, self._ind_w = self._indicator_target(checked)
            self.update()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        checked = self._group.checkedButton()
        if checked is not None:
            self._ind, self._ind_w = self._indicator_target(checked)
            self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        # Bottom divider line for the whole bar.
        from PySide6.QtGui import QPen

        pen = QPen(theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        from PySide6.QtCore import QPointF

        y = self.height() - 0.5
        painter.drawLine(QPointF(0, y), QPointF(self.width(), y))
        # Active indicator.
        if self._ind_w > 0:
            x = self._ind - self._ind_w / 2.0
            rect = QRectF(x, self.height() - _INDICATOR_H, self._ind_w, _INDICATOR_H)
            radii = CornerRadii(_INDICATOR_H, _INDICATOR_H, 0.0, 0.0)
            painter.fillPath(rounded_path(rect, radii), theme.color(ColorRole.PRIMARY))


__all__ = ["MdTab", "MdTabs"]
