"""Material split button for QtWidgets.

A split button is a connected pair: a primary action button (leading) and a
smaller trailing button (typically a dropdown arrow that opens a menu). Ported
in filled / elevated / tonal / outlined color variants, mirroring the
experimental ``labs/gb`` split button. The two halves are visually joined —
shared container color, outer ends rounded (corner-full), a divider between —
each with its own ripple + focus ring and ``clicked`` signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QSizePolicy, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font
from ..menu import MdMenu

_HEIGHT = 40
_RADIUS = _HEIGHT / 2.0  # corner-full ends
_ICON = 18
_GAP = 8
_PAD = 24
_PAD_WITH_ICON = 16
_TRAILING_W = 40
_OUTLINE_WIDTH = 1.0
_DISABLED_CONTAINER_OPACITY = 0.12
_DISABLED_LABEL_OPACITY = 0.38


class SplitButtonColor(Enum):
    FILLED = "filled"
    ELEVATED = "elevated"
    TONAL = "tonal"
    OUTLINED = "outlined"


@dataclass(frozen=True)
class _ColorSpec:
    container: ColorRole | None
    fg: ColorRole
    outline: ColorRole | None
    elevation: ElevationLevel
    hover_elevation: ElevationLevel


_SPECS = {
    SplitButtonColor.FILLED: _ColorSpec(
        ColorRole.PRIMARY, ColorRole.ON_PRIMARY, None,
        ElevationLevel.LEVEL0, ElevationLevel.LEVEL1,
    ),
    SplitButtonColor.TONAL: _ColorSpec(
        ColorRole.SECONDARY_CONTAINER, ColorRole.ON_SECONDARY_CONTAINER, None,
        ElevationLevel.LEVEL0, ElevationLevel.LEVEL1,
    ),
    SplitButtonColor.ELEVATED: _ColorSpec(
        ColorRole.SURFACE_CONTAINER_LOW, ColorRole.PRIMARY, None,
        ElevationLevel.LEVEL1, ElevationLevel.LEVEL2,
    ),
    SplitButtonColor.OUTLINED: _ColorSpec(
        None, ColorRole.PRIMARY, ColorRole.OUTLINE,
        ElevationLevel.LEVEL0, ElevationLevel.LEVEL0,
    ),
}


class _Segment(MaterialWidgetMixin, QAbstractButton):
    """One half of a split button (leading label/icon, or trailing arrow)."""

    def __init__(
        self,
        spec: _ColorSpec,
        side: str,
        parent: QWidget | None = None,
        *,
        text: str = "",
        icon: str = "",
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self._icon = icon
        self._spec = spec
        self._side = side  # "leading" | "trailing"
        if side == "leading":
            radii = CornerRadii(_RADIUS, 0.0, 0.0, _RADIUS)
        else:
            radii = CornerRadii(0.0, _RADIUS, _RADIUS, 0.0)
        self._init_material(
            shape=radii,
            typescale=TypescaleRole.LABEL_LARGE,
            elevation=spec.elevation,
            ripple=True,
            focus_ring=True,
            ripple_role=spec.fg,
            surface_role=spec.container or ColorRole.SURFACE,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if side == "trailing":
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    # -- elevation by interaction -----------------------------------------

    def _current_elevation(self) -> ElevationLevel:
        if not self.isEnabled():
            return ElevationLevel.LEVEL0
        if self.underMouse() and not self.isDown():
            return self._spec.hover_elevation
        return self._spec.elevation

    def _refresh_elevation(self) -> None:
        self.set_elevation(self._current_elevation())

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self._refresh_elevation()
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self._refresh_elevation()
        self.update()

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.EnabledChange and self.ripple is not None:
            self.ripple.set_enabled(self.isEnabled())
            self._refresh_elevation()
        super().changeEvent(event)
        self.update()

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        if self._side == "trailing":
            return QSize(_TRAILING_W, _HEIGHT)
        metrics = QFontMetrics(self.font())
        w = metrics.horizontalAdvance(self.text())
        lead = _PAD_WITH_ICON if self._icon else _PAD
        width = lead + w + _PAD
        if self._icon:
            width += _ICON + _GAP
        return QSize(width, _HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        path = self.clip_path()
        spec = self._spec

        if spec.container is not None:
            color = theme.color(spec.container)
            if not enabled:
                color = theme.color(ColorRole.ON_SURFACE)
                color.setAlphaF(_DISABLED_CONTAINER_OPACITY)
            painter.fillPath(path, color)

        if spec.outline is not None:
            oc = theme.color(ColorRole.ON_SURFACE if not enabled else spec.outline)
            if not enabled:
                oc.setAlphaF(_DISABLED_CONTAINER_OPACITY)
            pen = QPen(oc)
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = _OUTLINE_WIDTH / 2.0
            painter.drawPath(
                rounded_path(
                    QRectF(self.rect()).adjusted(inset, inset, -inset, -inset),
                    self._radii,
                )
            )

        fg = theme.color(spec.fg)
        if not enabled:
            fg = theme.color(ColorRole.ON_SURFACE)
            fg.setAlphaF(_DISABLED_LABEL_OPACITY)

        if self._side == "trailing":
            font = material_symbols_font(_ICON + 6, filled=False)
            if font is not None:
                painter.setFont(font)
                painter.setPen(fg)
                painter.drawText(QRectF(self.rect()), Qt.AlignmentFlag.AlignCenter,
                                 self._icon or "arrow_drop_down")
            return

        # Leading: optional icon + label, centered as a group.
        has_icon = bool(self._icon)
        content_w = QFontMetrics(self.font()).horizontalAdvance(self.text())
        if has_icon:
            content_w += _ICON + _GAP
        x = (self.width() - content_w) / 2.0
        if has_icon:
            ifont = material_symbols_font(_ICON, filled=False)
            if ifont is not None:
                painter.setFont(ifont)
                painter.setPen(fg)
                painter.drawText(QRectF(x, 0, _ICON, self.height()),
                                 Qt.AlignmentFlag.AlignCenter, self._icon)
            x += _ICON + _GAP
        painter.setFont(self.font())
        painter.setPen(fg)
        painter.drawText(QRectF(x, 0, self.width() - x, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self.text())


class MdSplitButton(QWidget):
    """A Material split button: leading action + trailing dropdown."""

    clicked = Signal()
    trailing_clicked = Signal()

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        color: SplitButtonColor = SplitButtonColor.FILLED,
        icon: str = "",
        trailing_icon: str = "arrow_drop_down",
    ) -> None:
        super().__init__(parent)
        self._spec = _SPECS[color]
        self._menu: MdMenu | None = None
        self._leading = _Segment(self._spec, "leading", text=text, icon=icon)
        self._trailing = _Segment(self._spec, "trailing", icon=trailing_icon)
        self._leading.clicked.connect(self.clicked)
        self._trailing.clicked.connect(self._on_trailing)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)  # 1px gap shows the surface behind as a divider
        lay.addWidget(self._leading)
        lay.addWidget(self._trailing)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(_HEIGHT)

    # -- menu --------------------------------------------------------------

    def set_menu(self, menu: MdMenu) -> None:
        """Attach a menu opened by the trailing button."""
        self._menu = menu

    def _on_trailing(self) -> None:
        self.trailing_clicked.emit()
        if self._menu is not None:
            self._menu.open_at(self._trailing)

    # -- passthroughs ------------------------------------------------------

    def set_text(self, text: str) -> None:
        self._leading.setText(text)
        self._leading.updateGeometry()

    def text(self) -> str:
        return self._leading.text()

    def setEnabled(self, enabled: bool) -> None:  # noqa: N802
        super().setEnabled(enabled)
        self._leading.setEnabled(enabled)
        self._trailing.setEnabled(enabled)


__all__ = ["MdSplitButton", "SplitButtonColor"]
