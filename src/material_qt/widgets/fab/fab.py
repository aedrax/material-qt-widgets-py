"""Material 3 FAB (floating action button) for QtWidgets.

Ports Material Web's ``fab/`` — :class:`MdFab` and :class:`MdBrandedFab`. Three
sizes (small 40 / regular 56 / large 96) with corner-medium/large/extra-large
shapes, four color variants (surface/primary/secondary/tertiary), level-3
elevation that rises to level-4 on hover, and an extended form with a
``label-large`` label beside the icon. Built on :class:`QAbstractButton`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import QAbstractButton, QSizePolicy, QWidget

from ...core.long_press import LongPressMixin
from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole, spec_for
from ...core.typography_util import font_for
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font


class FabSize(Enum):
    SMALL = "small"
    REGULAR = "regular"
    LARGE = "large"


class FabColor(Enum):
    SURFACE = "surface"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


# size -> (container px, ShapeScale, icon px)
_SIZE_SPEC = {
    FabSize.SMALL: (40, ShapeScale.MEDIUM, 24),
    FabSize.REGULAR: (56, ShapeScale.LARGE, 24),
    FabSize.LARGE: (96, ShapeScale.EXTRA_LARGE, 36),
}

# color -> (container role, icon/label role)
_COLOR_SPEC = {
    FabColor.SURFACE: (ColorRole.SURFACE_CONTAINER_HIGH, ColorRole.PRIMARY),
    FabColor.PRIMARY: (ColorRole.PRIMARY_CONTAINER, ColorRole.ON_PRIMARY_CONTAINER),
    FabColor.SECONDARY: (
        ColorRole.SECONDARY_CONTAINER,
        ColorRole.ON_SECONDARY_CONTAINER,
    ),
    FabColor.TERTIARY: (
        ColorRole.TERTIARY_CONTAINER,
        ColorRole.ON_TERTIARY_CONTAINER,
    ),
}

_EXTENDED_HEIGHT = 56
_EXTENDED_PAD = 16
_EXTENDED_GAP = 12


@dataclass(frozen=True)
class _FabConfig:
    container_px: int
    shape: ShapeScale
    icon_px: int
    container_role: ColorRole
    fg_role: ColorRole


class MdFab(LongPressMixin, MaterialWidgetMixin, QAbstractButton):
    """A Material 3 floating action button."""

    #: Emitted on a sustained press (Flutter ``onLongPress`` parity).
    longPressed = Signal()

    def __init__(
        self,
        icon: str = "",
        parent: QWidget | None = None,
        *,
        size: FabSize = FabSize.REGULAR,
        color: FabColor = FabColor.SURFACE,
        label: str = "",
        lowered: bool = False,
        tooltip: str = "",
        autofocus: bool = False,
    ) -> None:
        super().__init__(parent)
        self._icon_name = icon
        self._label = label
        self._size = size
        self._color = color
        self._lowered = lowered
        container_px, shape, icon_px = _SIZE_SPEC[size]
        container_role, fg_role = _COLOR_SPEC[color]
        self._cfg = _FabConfig(container_px, shape, icon_px, container_role, fg_role)

        rest = ElevationLevel.LEVEL1 if lowered else ElevationLevel.LEVEL3
        # Extended FAB is always regular height with a large corner.
        eff_shape = ShapeScale.LARGE if label else shape
        self._init_material(
            shape=eff_shape,
            elevation=rest,
            ripple=True,
            focus_ring=True,
            ripple_role=fg_role,
        )
        if label:
            self.setFont(font_for(spec_for(TypescaleRole.LABEL_LARGE)))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if tooltip:
            self.setToolTip(tooltip)
        self._autofocus_pending = autofocus

    # -- content -----------------------------------------------------------

    def set_icon(self, name: str) -> None:
        self._icon_name = name
        self.update()

    # -- elevation by interaction -----------------------------------------

    def _rest_elevation(self) -> ElevationLevel:
        return ElevationLevel.LEVEL1 if self._lowered else ElevationLevel.LEVEL3

    def _current_elevation(self) -> ElevationLevel:
        if not self.isEnabled():
            return self._rest_elevation()
        if self.underMouse() and not self.isDown():
            return ElevationLevel.LEVEL4 if not self._lowered else ElevationLevel.LEVEL2
        return self._rest_elevation()

    def _refresh_elevation(self) -> None:
        self.set_elevation(self._current_elevation())

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        if self._label:
            metrics = QFontMetrics(self.font())
            text_w = metrics.horizontalAdvance(self._label)
            width = _EXTENDED_PAD + self._cfg.icon_px + _EXTENDED_GAP + text_w + _EXTENDED_PAD
            if not self._icon_name:
                width = _EXTENDED_PAD + text_w + _EXTENDED_PAD
            return QSize(width, _EXTENDED_HEIGHT)
        return QSize(self._cfg.container_px, self._cfg.container_px)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- repaint / enable --------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        # autofocus is honored on first show (setFocus is a no-op before show).
        if getattr(self, "_autofocus_pending", False):
            self._autofocus_pending = False
            self.setFocus()

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self._refresh_elevation()
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self._cancel_long_press()
        self._refresh_elevation()
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self._arm_long_press(event)
        self._refresh_elevation()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._consume_long_press_release():
            self._refresh_elevation()
            return  # a long press fired; suppress the tap (no clicked)
        super().mouseReleaseEvent(event)
        self._refresh_elevation()

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.EnabledChange and self.ripple is not None:
            self.ripple.set_enabled(self.isEnabled())
        super().changeEvent(event)
        self.update()

    # -- painting ----------------------------------------------------------

    def _paint_glyph(self, painter: QPainter, rect: QRectF, color) -> None:
        font = material_symbols_font(self._cfg.icon_px, filled=False)
        if font is None:
            return
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._icon_name)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        path = self.clip_path()

        # Elevation is a QGraphicsDropShadowEffect kept in sync by
        # _refresh_elevation(); nothing to paint here.
        painter.fillPath(path, theme.color(self._cfg.container_role))

        fg = theme.color(self._cfg.fg_role)
        if self._label:
            icon_w = self._cfg.icon_px if self._icon_name else 0
            gap = _EXTENDED_GAP if self._icon_name else 0
            metrics = QFontMetrics(self.font())
            text_w = metrics.horizontalAdvance(self._label)
            content_w = icon_w + gap + text_w
            x = (self.width() - content_w) / 2.0
            if self._icon_name:
                self._paint_glyph(
                    painter, QRectF(x, 0, icon_w, self.height()), fg
                )
                x += icon_w + gap
            painter.setFont(self.font())
            painter.setPen(fg)
            painter.drawText(
                QRectF(x, 0, self.width() - x, self.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self._label,
            )
        elif self._icon_name:
            self._paint_glyph(painter, QRectF(self.rect()), fg)


class MdBrandedFab(MdFab):
    """A branded FAB: a surface FAB whose icon slot holds a multicolor logo.

    The logo is a placeholder (four Material key colors) since branded logos are
    app-specific; set ``label`` for an extended branded FAB.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        size: FabSize = FabSize.REGULAR,
        label: str = "",
    ) -> None:
        # Reserve the leading icon slot (the logo overlay fills it); the glyph
        # draw is suppressed via the _paint_glyph override below.
        super().__init__(
            "logo", parent, size=size, color=FabColor.SURFACE, label=label
        )

    def _paint_glyph(self, painter, rect, color) -> None:  # noqa: D401
        return  # branded FAB draws a logo overlay instead of a glyph

    def _paint_logo(self, painter: QPainter, center, r: float) -> None:
        from PySide6.QtCore import QRectF as _R

        theme = ThemeManager.instance()
        quads = [
            (ColorRole.PRIMARY, 90, 90),
            (ColorRole.SECONDARY, 180, 90),
            (ColorRole.TERTIARY, 270, 90),
            (ColorRole.ERROR, 0, 90),
        ]
        painter.setPen(Qt.PenStyle.NoPen)
        box = _R(center.x() - r, center.y() - r, 2 * r, 2 * r)
        for role, start, span in quads:
            painter.setBrush(theme.color(role))
            painter.drawPie(box, start * 16, span * 16)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        # Overlay the placeholder logo where the icon would be.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r = self._cfg.icon_px / 2.0
        if self._label:
            metrics = QFontMetrics(self.font())
            text_w = metrics.horizontalAdvance(self._label)
            content_w = self._cfg.icon_px + _EXTENDED_GAP + text_w
            x = (self.width() - content_w) / 2.0 + self._cfg.icon_px / 2.0
            from PySide6.QtCore import QPointF

            self._paint_logo(painter, QPointF(x, self.height() / 2.0), r)
        else:
            from PySide6.QtCore import QPointF

            self._paint_logo(
                painter, QPointF(self.width() / 2.0, self.height() / 2.0), r
            )


__all__ = ["FabColor", "FabSize", "MdBrandedFab", "MdFab"]
