"""Material 3 checkbox for QtWidgets.

Ports Material Web's ``md-checkbox``. An 18px box inside a 40px state-layer
target, with unselected (2px ``on-surface-variant`` outline), selected (filled
``primary`` container + ``on-primary`` checkmark) and indeterminate (dash)
states, plus an error variant. The checkmark/dash is animated on change. Built on
:class:`QAbstractButton` (checkable) so ``toggled``/``clicked``, keyboard (Space)
and ``checked`` work as standard, with the foundation supplying the ripple state
layer and focus ring.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii, ShapeScale
from ...theme.theme_manager import ThemeManager

_STATE_LAYER_SIZE = 40
_BOX_SIZE = 18
_BOX_CORNER = 2.0
_OUTLINE_WIDTH = 2.0
_DISABLED_OPACITY = 0.38
_ANIM = Duration.SHORT3  # 150ms check draw


class MdCheckbox(MaterialWidgetMixin, QAbstractButton):
    """A Material 3 checkbox (selected / unselected / indeterminate / error)."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        checked: bool = False,
        indeterminate: bool = False,
        error: bool = False,
        label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self._indeterminate = bool(indeterminate)
        self._error = bool(error)
        if label is not None:
            self.setAccessibleName(label)
        self._check_t = 1.0 if (checked or self._indeterminate) else 0.0
        # One persistent animation, reused per toggle (never deleted mid-flight,
        # so repeated clicks never hit a stale C++ object).
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(_ANIM))
        self._anim.setEasingCurve(easing_curve(Easing.STANDARD))
        self._anim.valueChanged.connect(self._set_check_t)
        # 40px circular state layer; the 18px box is painted centered.
        self._init_material(
            shape=ShapeScale.FULL,
            ripple=True,
            focus_ring=True,
            ripple_role=ColorRole.PRIMARY if checked else ColorRole.ON_SURFACE,
        )
        if checked:
            self.setChecked(True)
        self.toggled.connect(self._on_toggled)

    # -- properties --------------------------------------------------------

    @property
    def indeterminate(self) -> bool:
        return self._indeterminate

    def set_indeterminate(self, value: bool) -> None:
        value = bool(value)
        if value == self._indeterminate:
            return
        self._indeterminate = value
        self._sync_marker()
        self.update()

    @property
    def error(self) -> bool:
        return self._error

    def set_error(self, value: bool) -> None:
        self._error = bool(value)
        self.update()

    @property
    def label(self) -> str:
        """Accessible name (Material ``semanticLabel``)."""
        return self.accessibleName()

    def set_label(self, label: str | None) -> None:
        self.setAccessibleName(label or "")

    # -- state -------------------------------------------------------------

    def _marked(self) -> bool:
        return self.isChecked() or self._indeterminate

    def _on_toggled(self, checked: bool) -> None:
        if checked:
            self._indeterminate = False
        self._sync_marker()

    def _sync_marker(self) -> None:
        target = 1.0 if self._marked() else 0.0
        role = ColorRole.PRIMARY if self._marked() else ColorRole.ON_SURFACE
        if self.ripple is not None:
            self.ripple.set_color_role(ColorRole.ERROR if self._error else role)
        self._anim.stop()
        # Snap (no animation) for programmatic state set before the widget is
        # shown, or when motion is disabled.
        if not MOTION_ENABLED or not self.isVisible():
            self._check_t = target
            self.update()
            return
        self._anim.setStartValue(self._check_t)
        self._anim.setEndValue(target)
        self._anim.start()

    def _set_check_t(self, value) -> None:
        self._check_t = float(value)
        self.update()

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

    def _box_rect(self) -> QRectF:
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        return QRectF(cx - _BOX_SIZE / 2, cy - _BOX_SIZE / 2, _BOX_SIZE, _BOX_SIZE)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        box = self._box_rect()
        radii = CornerRadii.uniform(_BOX_CORNER)
        path = rounded_path(box, radii)

        marked = self._marked()
        fill_role = ColorRole.ERROR if self._error else ColorRole.PRIMARY
        outline_role = (
            ColorRole.ERROR if self._error else ColorRole.ON_SURFACE_VARIANT
        )
        mark_role = ColorRole.ON_ERROR if self._error else ColorRole.ON_PRIMARY

        # Crossfade container fill (marked) vs outline (unmarked) by check_t.
        t = self._check_t
        if t > 0:  # filled container
            fill = theme.color(fill_role)
            if not enabled:
                fill = theme.color(ColorRole.ON_SURFACE)
                fill.setAlphaF(_DISABLED_OPACITY)
            else:
                fill.setAlphaF(t)
            painter.fillPath(path, fill)
        if t < 1:  # outline box
            outline = theme.color(outline_role)
            if not enabled:
                outline = theme.color(ColorRole.ON_SURFACE)
                outline.setAlphaF(_DISABLED_OPACITY)
            else:
                outline.setAlphaF(1.0 - t)
            pen = QPen(outline)
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = _OUTLINE_WIDTH / 2.0
            painter.drawPath(
                rounded_path(box.adjusted(inset, inset, -inset, -inset), radii)
            )

        # Marker (checkmark or indeterminate dash), drawn proportional to t.
        if marked and t > 0:
            mark = theme.color(ColorRole.SURFACE if not enabled else mark_role)
            pen = QPen(mark)
            pen.setWidthF(2.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if self._indeterminate:
                y = box.center().y()
                x0 = box.left() + 4
                x1 = box.right() - 4
                painter.drawLine(QPointF(x0, y), QPointF(x1, y))
            else:
                # Checkmark polyline scaled by t (draws in as it animates).
                p1 = QPointF(box.left() + 4.0, box.top() + 9.5)
                p2 = QPointF(box.left() + 7.5, box.top() + 13.0)
                p3 = QPointF(box.left() + 14.0, box.top() + 5.0)
                if t >= 1.0:
                    painter.drawLine(p1, p2)
                    painter.drawLine(p2, p3)
                else:
                    # Animate the two segments sequentially.
                    seg1 = min(t / 0.4, 1.0)
                    painter.drawLine(p1, _lerp(p1, p2, seg1))
                    if t > 0.4:
                        seg2 = (t - 0.4) / 0.6
                        painter.drawLine(p2, _lerp(p2, p3, seg2))


def _lerp(a: QPointF, b: QPointF, f: float) -> QPointF:
    return QPointF(a.x() + (b.x() - a.x()) * f, a.y() + (b.y() - a.y()) * f)


__all__ = ["MdCheckbox"]
