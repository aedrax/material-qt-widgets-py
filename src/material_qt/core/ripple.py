"""Ripple: a transparent overlay child driven by an event filter on the host.

Reproduces the Material ripple behavior from ``ripple/internal/ripple.ts`` and
``_ripple.scss``:

* hover/focus state layer cross-fading over 15ms (linear);
* press ripple as a radial gradient growing over 450ms (standard easing) with a
  225ms minimum press, 105ms fade-in and 375ms fade-out (linear);
* ripple origin from the pointer (or centered for keyboard activation);
* max radius ``hypot(w, h) + 10``; clipped to the host's shape.
"""

from __future__ import annotations

import math

from PySide6.QtCore import (
    Property,
    QEvent,
    QObject,
    QPointF,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import QColor, QPainter, QPainterPath, QRadialGradient
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from ..tokens.color import ColorRole
from ..tokens.motion import Duration, Easing
from ..tokens.shape import CornerRadii
from ..tokens.state import StateLayer
from ..theme.theme_manager import ThemeManager
from .motion import MOTION_ENABLED, duration_ms, easing_curve
from .shape_util import rounded_path

# Geometry constants from ripple.ts.
INITIAL_ORIGIN_SCALE = 0.2
PADDING = 10
SOFT_EDGE_MINIMUM_SIZE = 75
SOFT_EDGE_CONTAINER_RATIO = 0.35

# Timings (ms).
PRESS_GROW_MS = Duration.LONG1.ms  # 450
MINIMUM_PRESS_MS = 225
PRESS_FADE_IN_MS = 105
PRESS_FADE_OUT_MS = 375
HOVER_FADE_MS = 15


class _RippleOverlay(QWidget):
    """Transparent child that paints the hover layer and the press ripple."""

    def __init__(self, host: QWidget, color_role: ColorRole) -> None:
        super().__init__(host)
        self.color_role = color_role
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._radii = CornerRadii.uniform(0.0)
        # state-layer opacity (hover/focus), animated 0..token.
        self._hover_opacity = 0.0
        # press ripple
        self._press_opacity = 0.0
        self._press_radius = 0.0
        self._press_origin = QPointF()
        self._press_max_radius = 0.0

    # -- properties animated via QPropertyAnimation ------------------------

    def get_hover_opacity(self) -> float:
        return self._hover_opacity

    def set_hover_opacity(self, value: float) -> None:
        self._hover_opacity = float(value)
        self.update()

    def get_press_opacity(self) -> float:
        return self._press_opacity

    def set_press_opacity(self, value: float) -> None:
        self._press_opacity = float(value)
        self.update()

    def get_press_radius(self) -> float:
        return self._press_radius

    def set_press_radius(self, value: float) -> None:
        self._press_radius = float(value)
        self.update()

    hoverOpacity = Property(float, get_hover_opacity, set_hover_opacity)
    pressOpacity = Property(float, get_press_opacity, set_press_opacity)
    pressRadius = Property(float, get_press_radius, set_press_radius)

    # -- painting ----------------------------------------------------------

    def set_radii(self, radii: CornerRadii) -> None:
        self._radii = radii
        self.update()

    def _clip_path(self) -> QPainterPath:
        return rounded_path(QRectF(self.rect()), self._radii)

    def paintEvent(self, event) -> None:  # noqa: N802
        if self._hover_opacity <= 0 and self._press_opacity <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        clip = self._clip_path()
        painter.setClipPath(clip)
        painter.setPen(Qt.PenStyle.NoPen)

        base = ThemeManager.instance().color(self.color_role)

        if self._hover_opacity > 0:
            color = QColor(base)
            color.setAlphaF(min(self._hover_opacity, 1.0))
            painter.fillPath(clip, color)

        if self._press_opacity > 0 and self._press_radius > 0:
            gradient = QRadialGradient(self._press_origin, self._press_radius)
            inner = QColor(base)
            inner.setAlphaF(min(self._press_opacity, 1.0))
            edge = QColor(base)
            edge.setAlphaF(min(self._press_opacity, 1.0))
            transparent = QColor(base)
            transparent.setAlphaF(0.0)
            # Solid core out to ~65%, then fade (matches the SCSS radial-gradient).
            gradient.setColorAt(0.0, inner)
            gradient.setColorAt(0.65, edge)
            gradient.setColorAt(1.0, transparent)
            painter.setBrush(gradient)
            painter.drawEllipse(
                self._press_origin,
                self._press_radius,
                self._press_radius,
            )


class RippleController(QObject):
    """Installs an event filter on ``host`` and manages a ripple overlay child.

    Construct with the host widget; the controller resizes/raises its overlay to
    cover the host and reacts to enter/leave, mouse press/release, focus, and
    keyboard activation events.
    """

    def __init__(
        self,
        host: QWidget,
        *,
        color_role: ColorRole = ColorRole.ON_SURFACE,
    ) -> None:
        super().__init__(host)
        self._host = host
        self._overlay = _RippleOverlay(host, color_role)
        self._overlay.setGeometry(host.rect())
        self._overlay.show()
        self._overlay.raise_()
        self._enabled = True
        self._pressed = False
        self._hovered = False
        self._focused = False
        self._press_anim = None
        self._opacity_anim = None
        self._min_press_timer = QTimer(self)
        self._min_press_timer.setSingleShot(True)
        self._release_pending = False
        host.installEventFilter(self)

    # -- public API --------------------------------------------------------

    @property
    def overlay(self) -> _RippleOverlay:
        return self._overlay

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self._set_hover(False)
            self._end_press(force=True)

    def set_radii(self, radii: CornerRadii) -> None:
        self._overlay.set_radii(radii)

    def set_color_role(self, role: ColorRole) -> None:
        self._overlay.color_role = role
        self._overlay.update()

    # -- event filter ------------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        # The overlay's C++ object may be destroyed during teardown before this
        # filter is removed; bail to avoid touching a deleted object.
        if obj is self._host and isValid(self._overlay):
            et = event.type()
            if et == QEvent.Type.Resize:
                self._overlay.setGeometry(self._host.rect())
                self._overlay.raise_()
            elif not self._enabled:
                return False
            elif et == QEvent.Type.Enter:
                self._set_hover(True)
            elif et == QEvent.Type.Leave:
                self._set_hover(False)
                if self._pressed:
                    self._end_press()
            elif et == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._start_press(event.position())
            elif et in (QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick):
                if self._pressed:
                    self._end_press()
            elif et == QEvent.Type.KeyPress:
                if event.key() in (
                    Qt.Key.Key_Space,
                    Qt.Key.Key_Return,
                    Qt.Key.Key_Enter,
                ) and not event.isAutoRepeat():
                    self._activate_keyboard()
            elif et == QEvent.Type.FocusIn:
                if event.reason() in (
                    Qt.FocusReason.TabFocusReason,
                    Qt.FocusReason.BacktabFocusReason,
                    Qt.FocusReason.ShortcutFocusReason,
                ):
                    self.set_focus_layer(True)
            elif et == QEvent.Type.FocusOut:
                self.set_focus_layer(False)
        return False

    # -- hover / focus state layer -----------------------------------------

    def set_focus_layer(self, focused: bool) -> None:
        """Show the focus state layer (same overlay, focus opacity)."""
        self._focused = focused
        self._animate_hover(self._state_layer_target())

    def _set_hover(self, hovered: bool) -> None:
        self._hovered = hovered
        self._animate_hover(self._state_layer_target())

    def _state_layer_target(self) -> float:
        # Focus (keyboard) takes precedence over hover, matching Material.
        if self._focused:
            return StateLayer.FOCUS.opacity
        if self._hovered:
            return StateLayer.HOVER.opacity
        return 0.0

    def _animate_hover(self, target: float) -> None:
        from .motion import animate

        if not MOTION_ENABLED:
            self._overlay.set_hover_opacity(target)
            return
        self._opacity_anim = animate(
            self._overlay,
            "hoverOpacity",
            target,
            duration=HOVER_FADE_MS,
            easing=Easing.LINEAR,
            start=self._overlay.get_hover_opacity(),
        )

    # -- press ripple ------------------------------------------------------

    def _geometry(self) -> tuple[float, float, float]:
        rect = self._host.rect()
        w = float(rect.width())
        h = float(rect.height())
        max_radius = math.hypot(w, h) + PADDING
        return w, h, max_radius

    def _start_press(self, origin: QPointF | None) -> None:
        from .motion import animate

        w, h, max_radius = self._geometry()
        if origin is None:
            origin = QPointF(w / 2.0, h / 2.0)
        self._pressed = True
        self._release_pending = False
        ov = self._overlay
        ov._press_origin = QPointF(origin)
        ov._press_max_radius = max_radius
        initial_radius = max(w, h) * INITIAL_ORIGIN_SCALE / 2.0

        # Minimum-press guard timer.
        self._min_press_timer.start(MINIMUM_PRESS_MS)

        if not MOTION_ENABLED:
            ov.set_press_radius(max_radius)
            ov.set_press_opacity(StateLayer.PRESSED.opacity)
            return

        # Grow radius (450ms standard) and fade in opacity (105ms linear).
        self._press_anim = animate(
            ov,
            "pressRadius",
            max_radius,
            duration=PRESS_GROW_MS,
            easing=Easing.STANDARD,
            start=initial_radius,
        )
        animate(
            ov,
            "pressOpacity",
            StateLayer.PRESSED.opacity,
            duration=PRESS_FADE_IN_MS,
            easing=Easing.LINEAR,
            start=ov.get_press_opacity(),
        )

    def _activate_keyboard(self) -> None:
        # Centered ripple for keyboard activation; immediately schedule release.
        self._start_press(None)
        self._end_press()

    def _end_press(self, *, force: bool = False) -> None:
        if not self._pressed:
            return
        if force:
            self._min_press_timer.stop()
            self._fade_out_press()
            return
        # Respect the minimum press duration before fading out.
        if self._min_press_timer.isActive():
            self._release_pending = True
            self._min_press_timer.timeout.connect(self._on_min_press_elapsed)
        else:
            self._fade_out_press()

    def _on_min_press_elapsed(self) -> None:
        try:
            self._min_press_timer.timeout.disconnect(self._on_min_press_elapsed)
        except (RuntimeError, TypeError):
            pass
        if self._release_pending:
            self._fade_out_press()

    def _fade_out_press(self) -> None:
        from .motion import animate

        self._pressed = False
        self._release_pending = False
        ov = self._overlay

        def _reset() -> None:
            ov.set_press_radius(0.0)

        if not MOTION_ENABLED:
            ov.set_press_opacity(0.0)
            _reset()
            return
        animate(
            ov,
            "pressOpacity",
            0.0,
            duration=PRESS_FADE_OUT_MS,
            easing=Easing.LINEAR,
            start=ov.get_press_opacity(),
            on_finished=_reset,
        )


__all__ = [
    "INITIAL_ORIGIN_SCALE",
    "MINIMUM_PRESS_MS",
    "PADDING",
    "PRESS_FADE_IN_MS",
    "PRESS_FADE_OUT_MS",
    "PRESS_GROW_MS",
    "SOFT_EDGE_CONTAINER_RATIO",
    "SOFT_EDGE_MINIMUM_SIZE",
    "RippleController",
]
