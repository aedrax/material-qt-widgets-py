"""Material 3 navigation rail for QtWidgets.

Ports the Material 3 navigation rail (cf. Flutter's ``NavigationRail`` /
``_NavigationRailDefaultsM3``) — a vertical ``surface`` rail, 80px wide, holding
3-7 destinations with exclusive selection. Each destination is a 24px icon in a
56x32 ``secondary-container`` pill indicator with a ``label-medium`` label below.
An optional leading widget (e.g. a FAB or menu button) sits above the
destinations. ``changed(index)`` fires when the active destination changes.

The public API mirrors :class:`MdNavigationBar` so the two navigation widgets
are siblings: ``changed = Signal(int)`` and
``add_destination(label, *, icon, active_icon)``.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QButtonGroup,
    QAbstractButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_RAIL_WIDTH = 80
_ICON = 24
_INDICATOR_W = 56
_INDICATOR_H = 32
_DEST_HEIGHT = 56
_LABEL_GAP = 4
_DEST_SPACING = 12
_TOP_PADDING = 8


class _RailDestination(MaterialWidgetMixin, QAbstractButton):
    """A single navigation-rail destination (icon pill + label below).

    Mirrors :class:`MdNavigationTab`'s color logic with rail dimensions: the
    active indicator is 56x32 (vs the bar's 64x32) and the item fills the rail
    width.
    """

    def __init__(
        self,
        label: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        active_icon: str = "",
    ) -> None:
        super().__init__(parent)
        self.setText(label)
        self._icon = icon
        self._active_icon = active_icon or icon
        self.setCheckable(True)
        self._init_material(
            shape=CornerRadii.uniform(_INDICATOR_H / 2.0),
            typescale=TypescaleRole.LABEL_MEDIUM,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE_VARIANT,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggled.connect(lambda *_: self.update())

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_RAIL_WIDTH, _DEST_HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(_INDICATOR_W, _DEST_HEIGHT)

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.EnabledChange and self.ripple is not None:
            self.ripple.set_enabled(self.isEnabled())
        super().changeEvent(event)
        self.update()

    def _indicator_rect(self) -> QRectF:
        cx = self.width() / 2.0
        return QRectF(cx - _INDICATOR_W / 2.0, 0, _INDICATOR_W, _INDICATOR_H)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        active = self.isChecked()
        indicator = self._indicator_rect()

        if active:
            path = rounded_path(indicator, CornerRadii.uniform(_INDICATOR_H / 2.0))
            painter.fillPath(path, theme.color(ColorRole.SECONDARY_CONTAINER))

        icon_color = theme.color(
            ColorRole.ON_SECONDARY_CONTAINER if active else ColorRole.ON_SURFACE_VARIANT
        )
        glyph = self._active_icon if active else self._icon
        if glyph:
            font = material_symbols_font(_ICON, filled=active)
            if font is not None:
                painter.setFont(font)
                painter.setPen(icon_color)
                painter.drawText(indicator, Qt.AlignmentFlag.AlignCenter, glyph)

        label_color = theme.color(
            ColorRole.ON_SURFACE if active else ColorRole.ON_SURFACE_VARIANT
        )
        painter.setFont(self.font())
        painter.setPen(label_color)
        label_rect = QRectF(
            0, indicator.bottom() + _LABEL_GAP, self.width(),
            _DEST_HEIGHT - indicator.bottom() - _LABEL_GAP,
        )
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                         self.text())


class MdNavigationRail(MaterialWidgetMixin, QWidget):
    """A vertical navigation rail of icon+label destinations."""

    changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._dests: list[_RailDestination] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, _TOP_PADDING, 0, _TOP_PADDING)
        self._lay.setSpacing(_DEST_SPACING)
        self._lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._init_material(
            shape=CornerRadii.uniform(0.0),
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        self.setFixedWidth(_RAIL_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def set_leading(self, widget: QWidget) -> None:
        """Place a leading widget (e.g. a FAB or menu button) above the
        destinations."""
        self._lay.insertWidget(0, widget, 0, Qt.AlignmentFlag.AlignHCenter)

    def add_destination(self, label: str, *, icon: str = "",
                        active_icon: str = "") -> _RailDestination:
        dest = _RailDestination(label, icon=icon, active_icon=active_icon)
        self._group.addButton(dest, len(self._dests))
        self._lay.addWidget(dest)
        self._dests.append(dest)
        dest.toggled.connect(
            lambda on, d=dest: on and self.changed.emit(self._dests.index(d))
        )
        if len(self._dests) == 1:
            dest.setChecked(True)
        return dest

    def sizeHint(self) -> QSize:  # noqa: N802
        height = _TOP_PADDING * 2 + sum(
            d.sizeHint().height() for d in self._dests
        ) + _DEST_SPACING * max(0, len(self._dests) - 1)
        return QSize(_RAIL_WIDTH, max(height, _RAIL_WIDTH))

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdNavigationRail"]
