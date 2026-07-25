"""Material 3 radio button for QtWidgets.

Ports Material Web's ``md-radio``. A 20px circle inside a 40px state-layer
target: unselected is a 2px ``on-surface-variant`` ring; selected is a 2px
``primary`` ring with an animated filled ``primary`` inner dot. Built on
:class:`QAbstractButton` with ``autoExclusive`` enabled so radios sharing a
parent (or a ``QButtonGroup``) are mutually exclusive, mirroring the web
single-selection controller. The foundation supplies the ripple state layer and
focus ring.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager

_STATE_LAYER_SIZE = 40
_CIRCLE_SIZE = 20
_RING_WIDTH = 2.0
_DOT_DIAMETER = 10.0
_DISABLED_OPACITY = 0.38
_ANIM = Duration.SHORT3  # 150ms dot scale-in


class MdRadio(MaterialWidgetMixin, QAbstractButton):
    """A Material 3 radio button (mutually exclusive within its parent/group)."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        checked: bool = False,
        toggleable: bool = False,
        label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        # toggleable: clicking the already-selected radio deselects it (Material
        # ``toggleable``). autoExclusive normally blocks this, so the click is
        # intercepted in nextCheckState().
        self._toggleable = bool(toggleable)
        if label is not None:
            self.setAccessibleName(label)
        self._dot_t = 1.0 if checked else 0.0
        # One persistent animation, reused per toggle (avoids stale C++ object
        # on repeated clicks once an animation has finished).
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(_ANIM))
        self._anim.setEasingCurve(easing_curve(Easing.STANDARD))
        self._anim.valueChanged.connect(self._set_dot_t)
        self._init_material(
            shape=ShapeScale.FULL,
            ripple=True,
            focus_ring=True,
            ripple_role=ColorRole.PRIMARY if checked else ColorRole.ON_SURFACE,
        )
        if checked:
            self.setChecked(True)
        self.toggled.connect(self._on_toggled)

    # -- state -------------------------------------------------------------

    def _on_toggled(self, checked: bool) -> None:
        target = 1.0 if checked else 0.0
        if self.ripple is not None:
            self.ripple.set_color_role(
                ColorRole.PRIMARY if checked else ColorRole.ON_SURFACE
            )
        self._anim.stop()
        if not MOTION_ENABLED or not self.isVisible():
            self._dot_t = target
            self.update()
            return
        self._anim.setStartValue(self._dot_t)
        self._anim.setEndValue(target)
        self._anim.start()

    def _set_dot_t(self, value) -> None:
        self._dot_t = float(value)
        self.update()

    # -- properties --------------------------------------------------------

    @property
    def toggleable(self) -> bool:
        """Whether clicking the selected radio deselects it (Material ``toggleable``)."""
        return self._toggleable

    def set_toggleable(self, value: bool) -> None:
        self._toggleable = bool(value)

    @property
    def label(self) -> str:
        """Accessible name (Material ``semanticLabel``)."""
        return self.accessibleName()

    def set_label(self, label: str | None) -> None:
        self.setAccessibleName(label or "")

    # -- toggleable (deselect-on-click) ------------------------------------

    def _run_with_exclusivity_off(self, fn) -> None:
        """Run ``fn`` with exclusivity temporarily disabled.

        Both ``QButtonGroup`` exclusivity and ``autoExclusive`` block unchecking
        the currently-selected button (and skip ``clicked``/``toggled``). Clearing
        the relevant guard lets Qt's own click machinery perform the deselect and
        emit the standard signals.
        """
        grp = self.group()
        if grp is not None and grp.exclusive():
            grp.setExclusive(False)
            try:
                fn()
            finally:
                grp.setExclusive(True)
        else:
            self.setAutoExclusive(False)
            try:
                fn()
            finally:
                self.setAutoExclusive(True)

    def click(self) -> None:
        """Programmatic click; deselects when toggleable and already selected."""
        if self._toggleable and self.isChecked():
            self._run_with_exclusivity_off(lambda: super(MdRadio, self).click())
            return
        super().click()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        """GUI click; deselects when toggleable and already selected."""
        if (
            self._toggleable
            and self.isChecked()
            and self.hitButton(event.position().toPoint())
        ):
            self._run_with_exclusivity_off(
                lambda: super(MdRadio, self).mouseReleaseEvent(event)
            )
            return
        super().mouseReleaseEvent(event)

    def keyReleaseEvent(self, event) -> None:  # noqa: N802
        """Space activation; deselects when toggleable and already selected.

        Qt activates buttons on Space release through the C++ click path,
        which bypasses the Python ``click()`` shadow above, so the toggleable
        deselect has to be routed here explicitly.
        """
        if (
            event.key() == Qt.Key.Key_Space
            and not event.isAutoRepeat()
            and self.isDown()
            and self._toggleable
            and self.isChecked()
        ):
            self._run_with_exclusivity_off(
                lambda: super(MdRadio, self).keyReleaseEvent(event)
            )
            return
        super().keyReleaseEvent(event)

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_STATE_LAYER_SIZE, _STATE_LAYER_SIZE)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- repaint / enable --------------------------------------------------

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

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        cx = self.width() / 2.0
        cy = self.height() / 2.0

        selected = self.isChecked()
        ring_role = (
            ColorRole.PRIMARY if selected else ColorRole.ON_SURFACE_VARIANT
        )
        ring = theme.color(ColorRole.ON_SURFACE if not enabled else ring_role)
        if not enabled:
            ring.setAlphaF(_DISABLED_OPACITY)

        # Outer ring.
        pen = QPen(ring)
        pen.setWidthF(_RING_WIDTH)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        r = _CIRCLE_SIZE / 2.0 - _RING_WIDTH / 2.0
        painter.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))

        # Inner dot, scaled by animation progress.
        if self._dot_t > 0:
            dot = theme.color(ColorRole.ON_SURFACE if not enabled else ColorRole.PRIMARY)
            if not enabled:
                dot.setAlphaF(_DISABLED_OPACITY)
            dr = (_DOT_DIAMETER / 2.0) * self._dot_t
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(dot)
            painter.drawEllipse(QRectF(cx - dr, cy - dr, 2 * dr, 2 * dr))


__all__ = ["MdRadio"]
