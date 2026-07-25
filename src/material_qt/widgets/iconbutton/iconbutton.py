"""Material 3 icon buttons for QtWidgets.

Ports Material Web's ``iconbutton/``: standard, filled, filled-tonal and outlined
icon buttons, each a 40px circular target with a 24px Material Symbols glyph.
Supports toggle mode (``checkable``) where selected/unselected use distinct
container/icon colors, mirroring the component tokens. Built on
:class:`QAbstractButton`; ripple + focus ring come from the foundation.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QSizePolicy, QWidget

from ...core.long_press import LongPressMixin
from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_SIZE = 40
_ICON_SIZE = 24
_OUTLINE_WIDTH = 1.0
_DISABLED_CONTAINER_OPACITY = 0.12
_DISABLED_ICON_OPACITY = 0.38


@dataclass(frozen=True)
class IconButtonStyle:
    """Per-variant colors for static and toggle (selected/unselected) modes."""

    container_role: ColorRole | None
    icon_role: ColorRole
    outline_role: ColorRole | None = None
    toggle_unselected_container: ColorRole | None = None
    toggle_unselected_icon: ColorRole = ColorRole.ON_SURFACE_VARIANT
    toggle_selected_container: ColorRole | None = None
    toggle_selected_icon: ColorRole = ColorRole.PRIMARY
    toggle_unselected_outline: ColorRole | None = None


class MdIconButton(LongPressMixin, MaterialWidgetMixin, QAbstractButton):
    """Standard Material icon button (no container)."""

    #: Emitted on a sustained press (Flutter ``onLongPress`` parity).
    longPressed = Signal()

    STYLE = IconButtonStyle(
        container_role=None,
        icon_role=ColorRole.ON_SURFACE_VARIANT,
        toggle_unselected_icon=ColorRole.ON_SURFACE_VARIANT,
        toggle_selected_icon=ColorRole.PRIMARY,
    )

    def __init__(
        self,
        icon: str = "",
        parent: QWidget | None = None,
        *,
        toggle: bool = False,
        selected_icon: str = "",
        checked: bool = False,
        tooltip: str = "",
        autofocus: bool = False,
    ) -> None:
        super().__init__(parent)
        self._icon_name = icon
        self._selected_icon = selected_icon
        self.setCheckable(toggle)
        self._init_material(
            shape=ShapeScale.FULL,
            ripple=True,
            focus_ring=True,
            ripple_role=self._icon_color_role(),
        )
        # Connect before the initial setChecked so a checked-at-construction
        # toggle button resyncs its ripple role to the selected state.
        self.toggled.connect(self._on_toggled)
        if toggle and checked:
            self.setChecked(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if tooltip:
            self.setToolTip(tooltip)
        self._autofocus_pending = autofocus

    # -- resolution --------------------------------------------------------

    def _is_toggle(self) -> bool:
        return self.isCheckable()

    def _container_role(self) -> ColorRole | None:
        s = self.STYLE
        if not self._is_toggle():
            return s.container_role
        return (
            s.toggle_selected_container
            if self.isChecked()
            else s.toggle_unselected_container
        )

    def _icon_color_role(self) -> ColorRole:
        s = self.STYLE
        if not self._is_toggle():
            return s.icon_role
        return s.toggle_selected_icon if self.isChecked() else s.toggle_unselected_icon

    def _outline_role(self) -> ColorRole | None:
        s = self.STYLE
        if not self._is_toggle():
            return s.outline_role
        # Outlined toggle: outline only while unselected.
        return None if self.isChecked() else s.toggle_unselected_outline

    def _current_icon(self) -> str:
        if self._is_toggle() and self.isChecked() and self._selected_icon:
            return self._selected_icon
        return self._icon_name

    # -- properties --------------------------------------------------------

    @property
    def icon_name(self) -> str:
        return self._icon_name

    def set_icon(self, name: str) -> None:
        self._icon_name = name
        self.update()

    def _on_toggled(self, checked: bool) -> None:
        if self.ripple is not None:
            self.ripple.set_color_role(self._icon_color_role())
        self.update()

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_SIZE, _SIZE)

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
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self._cancel_long_press()
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self._arm_long_press(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._consume_long_press_release():
            return  # a long press fired; suppress the tap (no clicked)
        super().mouseReleaseEvent(event)

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.EnabledChange and self.ripple is not None:
            self.ripple.set_enabled(self.isEnabled())
        super().changeEvent(event)
        self.update()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        path = self.clip_path()

        container = self._container_role()
        if container is not None:
            color = theme.color(container)
            if not enabled:
                color = theme.color(ColorRole.ON_SURFACE)
                color.setAlphaF(_DISABLED_CONTAINER_OPACITY)
            painter.fillPath(path, color)

        outline = self._outline_role()
        if outline is not None:
            oc = theme.color(ColorRole.ON_SURFACE if not enabled else outline)
            if not enabled:
                oc.setAlphaF(_DISABLED_CONTAINER_OPACITY)
            pen = QPen(oc)
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = _OUTLINE_WIDTH / 2.0
            from ...core.shape_util import rounded_path

            painter.drawPath(
                rounded_path(
                    QRectF(self.rect()).adjusted(inset, inset, -inset, -inset),
                    self._radii,
                )
            )

        glyph = self._current_icon()
        if glyph:
            icon_color = theme.color(self._icon_color_role())
            if not enabled:
                icon_color = theme.color(ColorRole.ON_SURFACE)
                icon_color.setAlphaF(_DISABLED_ICON_OPACITY)
            font = material_symbols_font(_ICON_SIZE, filled=False)
            if font is not None:
                painter.setFont(font)
                painter.setPen(icon_color)
                painter.drawText(
                    QRectF(self.rect()), Qt.AlignmentFlag.AlignCenter, glyph
                )


class MdFilledIconButton(MdIconButton):
    STYLE = IconButtonStyle(
        container_role=ColorRole.PRIMARY,
        icon_role=ColorRole.ON_PRIMARY,
        toggle_unselected_container=ColorRole.SURFACE_CONTAINER_HIGHEST,
        toggle_unselected_icon=ColorRole.PRIMARY,
        toggle_selected_container=ColorRole.PRIMARY,
        toggle_selected_icon=ColorRole.ON_PRIMARY,
    )


class MdFilledTonalIconButton(MdIconButton):
    STYLE = IconButtonStyle(
        container_role=ColorRole.SECONDARY_CONTAINER,
        icon_role=ColorRole.ON_SECONDARY_CONTAINER,
        toggle_unselected_container=ColorRole.SURFACE_CONTAINER_HIGHEST,
        toggle_unselected_icon=ColorRole.ON_SURFACE_VARIANT,
        toggle_selected_container=ColorRole.SECONDARY_CONTAINER,
        toggle_selected_icon=ColorRole.ON_SECONDARY_CONTAINER,
    )


class MdOutlinedIconButton(MdIconButton):
    STYLE = IconButtonStyle(
        container_role=None,
        icon_role=ColorRole.ON_SURFACE_VARIANT,
        outline_role=ColorRole.OUTLINE,
        toggle_unselected_container=None,
        toggle_unselected_icon=ColorRole.ON_SURFACE_VARIANT,
        toggle_unselected_outline=ColorRole.OUTLINE,
        toggle_selected_container=ColorRole.INVERSE_SURFACE,
        toggle_selected_icon=ColorRole.INVERSE_ON_SURFACE,
    )


__all__ = [
    "IconButtonStyle",
    "MdFilledIconButton",
    "MdFilledTonalIconButton",
    "MdIconButton",
    "MdOutlinedIconButton",
]
