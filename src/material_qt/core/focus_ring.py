"""Focus ring: a keyboard-focus-only animated outline drawn outside the host.

Matches ``focus/internal/_focus-ring.scss`` + ``_md-comp-focus-ring.scss``:
secondary color, pill (full) shape, 2px outward offset, stroke animating
3 -> 8 -> 3 px over 600ms (emphasized easing). Shown only for keyboard focus
reasons (Tab / Backtab / Shortcut); hidden on mouse press or focus out.
"""

from __future__ import annotations

from PySide6.QtCore import Property, QEvent, QObject, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from ..tokens.color import ColorRole
from ..tokens.motion import Duration, Easing
from ..tokens.shape import CornerRadii
from ..theme.theme_manager import ThemeManager
from .motion import MOTION_ENABLED, animate
from .shape_util import rounded_path

# From _md-comp-focus-ring.scss.
WIDTH = 3.0
ACTIVE_WIDTH = 8.0
OUTWARD_OFFSET = 2.0
DURATION = Duration.LONG4  # 600ms

_KEYBOARD_REASONS = (
    Qt.FocusReason.TabFocusReason,
    Qt.FocusReason.BacktabFocusReason,
    Qt.FocusReason.ShortcutFocusReason,
)


class _FocusOverlay(QWidget):
    """Transparent overlay that draws the animated ring just outside the host."""

    def __init__(self, host: QWidget) -> None:
        # Parent to the host initially so the overlay is never a top-level
        # window (host.parentWidget() is often None at construction, before the
        # host is added to a layout). reposition() reparents it to the host's
        # actual parent at show time so the ring can extend beyond the host.
        super().__init__(host)
        self._host = host
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._radii = CornerRadii.from_scale("full")
        self._stroke = WIDTH
        self._visible = False
        self.hide()

    def get_stroke(self) -> float:
        return self._stroke

    def set_stroke(self, value: float) -> None:
        self._stroke = float(value)
        self.update()

    stroke = Property(float, get_stroke, set_stroke)

    def set_radii(self, radii: CornerRadii) -> None:
        self._radii = radii
        self.update()

    def reposition(self) -> None:
        """Cover the host's geometry expanded by the outward offset + stroke.

        The geometry is in the host's parent coordinate space, so keep the
        overlay parented to the host's current parent (this also follows the
        host when it is reparented between containers). With no parent there is
        nothing to draw the ring against.
        """
        host = self._host
        if not isValid(host):
            return
        parent = host.parentWidget()
        if parent is None:
            return
        if self.parentWidget() is not parent:
            self.setParent(parent)
            if self._visible:
                self.show()
        margin = OUTWARD_OFFSET + ACTIVE_WIDTH
        geo = host.geometry()
        self.setGeometry(geo.adjusted(-margin, -margin, margin, margin))
        self.raise_()

    def paintEvent(self, event) -> None:  # noqa: N802
        # The overlay lives in the host's *parent*, so it can be asked to paint
        # after the host's C++ object is gone (deleteLater on a focused host).
        if not self._visible or self._stroke <= 0 or not isValid(self._host):
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        margin = OUTWARD_OFFSET + ACTIVE_WIDTH
        # The host rect within this overlay, expanded outward by OUTWARD_OFFSET.
        host_rect = QRectF(
            margin - OUTWARD_OFFSET,
            margin - OUTWARD_OFFSET,
            self._host.width() + 2 * OUTWARD_OFFSET,
            self._host.height() + 2 * OUTWARD_OFFSET,
        )
        # Inset by half the stroke so the outline stays within the overlay.
        half = self._stroke / 2.0
        ring_rect = host_rect.adjusted(half, half, -half, -half)
        color = ThemeManager.instance().color(ColorRole.SECONDARY)
        pen = QPen(color)
        pen.setWidthF(self._stroke)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawPath(rounded_path(ring_rect, self._radii))


def _drop_overlay(overlay: _FocusOverlay) -> None:
    """Tear down a host's focus overlay when the host is destroyed."""
    if isValid(overlay):
        overlay._visible = False
        overlay.hide()
        overlay.deleteLater()


class FocusRingController(QObject):
    """Shows an animated focus ring around ``host`` for keyboard focus only."""

    def __init__(self, host: QWidget) -> None:
        super().__init__(host)
        self._host = host
        self._overlay = _FocusOverlay(host)
        self._grow_anim = None
        self._shrink_anim = None
        host.installEventFilter(self)
        # Once shown, the overlay is reparented to the host's parent and would
        # outlive the host — a dangling ring at best, a use-after-free paint at
        # worst. Connect a lambda, NOT a bound method: PySide holds bound-method
        # slots weakly, and if this controller's wrapper is GC'd first the emit
        # fails with "Slot not found". The connection itself owns the lambda
        # and dies with the host.
        host.destroyed.connect(lambda *_, ov=self._overlay: _drop_overlay(ov))

    @property
    def overlay(self) -> _FocusOverlay:
        return self._overlay

    def set_radii(self, radii: CornerRadii) -> None:
        self._overlay.set_radii(radii)

    @property
    def visible(self) -> bool:
        return self._overlay._visible

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        # The overlay is parented to the host's parent, so during teardown its
        # C++ object may be destroyed before this filter is removed. Bail if so.
        if obj is self._host and isValid(self._overlay):
            et = event.type()
            if et == QEvent.Type.FocusIn:
                if event.reason() in _KEYBOARD_REASONS:
                    self.show_ring()
            elif et == QEvent.Type.FocusOut:
                self.hide_ring()
            elif et == QEvent.Type.MouseButtonPress:
                self.hide_ring()
            elif et in (QEvent.Type.Resize, QEvent.Type.Move, QEvent.Type.Show):
                if self._overlay._visible:
                    self._overlay.reposition()
        return False

    # -- show / hide -------------------------------------------------------

    def show_ring(self) -> None:
        ov = self._overlay
        if not isValid(ov):
            return
        ov._visible = True
        ov.reposition()
        ov.show()
        ov.raise_()
        if not MOTION_ENABLED:
            ov.set_stroke(WIDTH)
            return
        # Grow 3 -> 8 over the first quarter, then shrink 8 -> 3 over the rest,
        # both with emphasized easing (matches the SCSS two-keyframe animation).
        quarter = DURATION.ms // 4
        rest = DURATION.ms - quarter

        def _shrink() -> None:
            if not ov._visible:
                return
            self._shrink_anim = animate(
                ov,
                "stroke",
                WIDTH,
                duration=rest,
                easing=Easing.EMPHASIZED,
                start=ACTIVE_WIDTH,
            )

        self._grow_anim = animate(
            ov,
            "stroke",
            ACTIVE_WIDTH,
            duration=quarter,
            easing=Easing.EMPHASIZED,
            start=WIDTH,
            on_finished=_shrink,
        )

    def hide_ring(self) -> None:
        ov = self._overlay
        if not isValid(ov):
            return
        ov._visible = False
        ov.hide()


__all__ = [
    "ACTIVE_WIDTH",
    "DURATION",
    "OUTWARD_OFFSET",
    "WIDTH",
    "FocusRingController",
]
