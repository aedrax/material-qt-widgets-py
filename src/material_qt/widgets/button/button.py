"""Material 3 common buttons for QtWidgets.

Ports Material Web's five common button variants (``button/``): text, elevated,
filled, filled-tonal, and outlined. Each is a pill-shaped (corner-full) control,
40px tall, with a ``label-large`` label and an optional leading Material Symbols
icon. State layers (hover/focus/press), the focus ring, and elevation are
provided by the shared foundation; per-variant container/label/outline colors and
elevation come straight from the component tokens.

Built on :class:`QAbstractButton` so the standard ``clicked`` signal, ``text``,
``enabled`` and keyboard activation (Space/Enter) work as expected, with the
:class:`MaterialWidgetMixin` adding the Material look and behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QWidget

from ...core.long_press import LongPressMixin
from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font


class IconAlignment(Enum):
    """Leading vs. trailing placement of the button's icon (Flutter parity)."""

    START = "start"
    END = "end"

# Shared measurements from the button tokens (all variants: height 40, shape full,
# label label-large, icon 18px). Padding/gap from the M3 button spec.
_HEIGHT = 40
_ICON_SIZE = 18
_LABEL_GAP = 8
_PAD = 24  # leading/trailing padding (text-only)
_PAD_WITH_ICON_LEADING = 16
_PAD_TEXT_VARIANT = 12  # text button has tighter padding
# Disabled opacities (from tokens).
_DISABLED_CONTAINER_OPACITY = 0.12
_DISABLED_LABEL_OPACITY = 0.38
_OUTLINE_WIDTH = 1.0


@dataclass(frozen=True)
class ButtonStyle:
    """Per-variant color/elevation spec, mirroring the component tokens."""

    container_role: ColorRole | None  # None -> transparent container
    label_role: ColorRole
    outline_role: ColorRole | None  # None -> no outline
    elevation: ElevationLevel
    hover_elevation: ElevationLevel
    pressed_elevation: ElevationLevel
    text_padding: bool = False  # text button uses tighter horizontal padding


class MdButton(LongPressMixin, MaterialWidgetMixin, QAbstractButton):
    """Base Material button. Use a variant subclass for concrete styling."""

    #: Emitted on a sustained press (Flutter ``onLongPress`` parity).
    longPressed = Signal()

    STYLE: ButtonStyle = ButtonStyle(
        container_role=ColorRole.PRIMARY,
        label_role=ColorRole.ON_PRIMARY,
        outline_role=None,
        elevation=ElevationLevel.LEVEL0,
        hover_elevation=ElevationLevel.LEVEL0,
        pressed_elevation=ElevationLevel.LEVEL0,
    )

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        icon_alignment: IconAlignment = IconAlignment.START,
        tooltip: str = "",
        autofocus: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self._icon_name = icon
        self._icon_alignment = icon_alignment
        style = self.STYLE
        self._init_material(
            shape=ShapeScale.FULL,
            typescale=TypescaleRole.LABEL_LARGE,
            elevation=style.elevation,
            ripple=True,
            focus_ring=True,
            ripple_role=style.label_role,
            surface_role=style.container_role or ColorRole.SURFACE,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
        self._autofocus_pending = autofocus

    # -- icon --------------------------------------------------------------

    @property
    def icon_name(self) -> str:
        return self._icon_name

    def set_icon(self, name: str) -> None:
        if name == self._icon_name:
            return
        self._icon_name = name
        self.updateGeometry()
        self.update()

    @property
    def icon_alignment(self) -> IconAlignment:
        return self._icon_alignment

    def set_icon_alignment(self, alignment: IconAlignment) -> None:
        if alignment == self._icon_alignment:
            return
        self._icon_alignment = alignment
        self.update()

    # -- sizing ------------------------------------------------------------

    def _label_advance(self) -> int:
        from PySide6.QtGui import QFontMetrics

        return QFontMetrics(self.font()).horizontalAdvance(self.text())

    def sizeHint(self) -> QSize:  # noqa: N802
        has_icon = bool(self._icon_name)
        lead = _PAD_TEXT_VARIANT if self.STYLE.text_padding else (
            _PAD_WITH_ICON_LEADING if has_icon else _PAD
        )
        trail = _PAD_TEXT_VARIANT if self.STYLE.text_padding else _PAD
        width = lead + trail + self._label_advance()
        if has_icon:
            width += _ICON_SIZE + _LABEL_GAP
        return QSize(width, _HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- elevation by interaction -----------------------------------------

    def _current_elevation(self) -> ElevationLevel:
        if not self.isEnabled():
            return ElevationLevel.LEVEL0  # disabled buttons cast no shadow
        if self.isDown():
            return self.STYLE.pressed_elevation
        if self.underMouse():
            return self.STYLE.hover_elevation
        return self.STYLE.elevation

    def _refresh_elevation(self) -> None:
        self.set_elevation(self._current_elevation())

    # -- repaint triggers --------------------------------------------------

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
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Type.EnabledChange:
            if self.ripple is not None:
                self.ripple.set_enabled(self.isEnabled())
            self._refresh_elevation()
        super().changeEvent(event)
        self.update()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        rect = QRectF(self.rect())
        path = self.clip_path()
        style = self.STYLE

        # Elevation is a QGraphicsDropShadowEffect kept in sync by
        # _refresh_elevation(); nothing to paint here.

        # Container fill.
        if style.container_role is not None:
            color = theme.color(style.container_role)
            if not enabled:
                color = theme.color(ColorRole.ON_SURFACE)
                color.setAlphaF(_DISABLED_CONTAINER_OPACITY)
            painter.fillPath(path, color)

        # Outline (outlined variant).
        if style.outline_role is not None:
            outline = theme.color(
                ColorRole.ON_SURFACE if not enabled else style.outline_role
            )
            if not enabled:
                outline.setAlphaF(_DISABLED_CONTAINER_OPACITY)
            pen = QPen(outline)
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = _OUTLINE_WIDTH / 2.0
            painter.drawPath(
                self._inset_path(rect.adjusted(inset, inset, -inset, -inset))
            )

        # Foreground (icon + label).
        label_color = theme.color(style.label_role)
        if not enabled:
            label_color = theme.color(ColorRole.ON_SURFACE)
            label_color.setAlphaF(_DISABLED_LABEL_OPACITY)

        has_icon = bool(self._icon_name)
        label_w = self._label_advance()
        content_w = label_w + (_ICON_SIZE + _LABEL_GAP if has_icon else 0)
        x = (self.width() - content_w) / 2.0

        def _draw_icon(at_x: float) -> None:
            icon_font = material_symbols_font(_ICON_SIZE, filled=False)
            if icon_font is None:
                return
            painter.setFont(icon_font)
            painter.setPen(label_color)
            painter.drawText(
                QRectF(at_x, 0, _ICON_SIZE, self.height()),
                Qt.AlignmentFlag.AlignCenter,
                self._icon_name,
            )

        def _draw_label(at_x: float) -> None:
            painter.setFont(self.font())
            painter.setPen(label_color)
            painter.drawText(
                QRectF(at_x, 0, self.width() - at_x, self.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self.text(),
            )

        leading_icon = not has_icon or self._icon_alignment is IconAlignment.START
        if leading_icon:
            if has_icon:
                _draw_icon(x)
                x += _ICON_SIZE + _LABEL_GAP
            _draw_label(x)
        else:
            _draw_label(x)
            _draw_icon(x + label_w + _LABEL_GAP)

    def _inset_path(self, rect: QRectF):
        from ...core.shape_util import rounded_path

        return rounded_path(rect, self._radii)


# -- variants --------------------------------------------------------------


class MdFilledButton(MdButton):
    STYLE = ButtonStyle(
        container_role=ColorRole.PRIMARY,
        label_role=ColorRole.ON_PRIMARY,
        outline_role=None,
        elevation=ElevationLevel.LEVEL0,
        hover_elevation=ElevationLevel.LEVEL1,
        pressed_elevation=ElevationLevel.LEVEL0,
    )


class MdFilledTonalButton(MdButton):
    STYLE = ButtonStyle(
        container_role=ColorRole.SECONDARY_CONTAINER,
        label_role=ColorRole.ON_SECONDARY_CONTAINER,
        outline_role=None,
        elevation=ElevationLevel.LEVEL0,
        hover_elevation=ElevationLevel.LEVEL1,
        pressed_elevation=ElevationLevel.LEVEL0,
    )


class MdElevatedButton(MdButton):
    STYLE = ButtonStyle(
        container_role=ColorRole.SURFACE_CONTAINER_LOW,
        label_role=ColorRole.PRIMARY,
        outline_role=None,
        elevation=ElevationLevel.LEVEL1,
        hover_elevation=ElevationLevel.LEVEL2,
        pressed_elevation=ElevationLevel.LEVEL1,
    )


class MdOutlinedButton(MdButton):
    STYLE = ButtonStyle(
        container_role=None,
        label_role=ColorRole.PRIMARY,
        outline_role=ColorRole.OUTLINE,
        elevation=ElevationLevel.LEVEL0,
        hover_elevation=ElevationLevel.LEVEL0,
        pressed_elevation=ElevationLevel.LEVEL0,
    )


class MdTextButton(MdButton):
    STYLE = ButtonStyle(
        container_role=None,
        label_role=ColorRole.PRIMARY,
        outline_role=None,
        elevation=ElevationLevel.LEVEL0,
        hover_elevation=ElevationLevel.LEVEL0,
        pressed_elevation=ElevationLevel.LEVEL0,
        text_padding=True,
    )


__all__ = [
    "ButtonStyle",
    "IconAlignment",
    "MdButton",
    "MdElevatedButton",
    "MdFilledButton",
    "MdFilledTonalButton",
    "MdOutlinedButton",
    "MdTextButton",
]
