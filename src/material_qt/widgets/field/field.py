"""Material 3 field container for QtWidgets.

Ports Material Web's ``field/`` — the visual chrome shared by text fields and
selects, in filled and outlined variants. Provides a floating label, an active
indicator (filled) or notched outline (outlined), supporting text, an error
state, optional leading/trailing icon slots, and a content slot where an input
(e.g. a ``QLineEdit``) is placed. :class:`MdField` tracks focus of its content
widget to float the label.

Tokens: filled container ``surface-container-highest``, active indicator
``on-surface-variant`` 1px -> ``primary`` 2px on focus; outlined ``outline`` 1px
-> ``primary`` 2px; label ``on-surface-variant`` -> ``primary``; corner 4px
(filled: top only).
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QEvent, QObject, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.shape_util import rounded_path
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager

_FIELD_H = 56
_PAD = 16
_SUPPORT_H = 20
_CORNER = 4.0
_ANIM = Duration.SHORT3


class FieldVariant(Enum):
    FILLED = "filled"
    OUTLINED = "outlined"


class MdField(MaterialWidgetMixin, QWidget):
    """The Material field chrome (filled or outlined) with a content slot."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        variant: FieldVariant = FieldVariant.FILLED,
        label: str = "",
        supporting_text: str = "",
        error: bool = False,
    ) -> None:
        super().__init__(parent)
        self._variant = variant
        self._label = label
        self._supporting = supporting_text
        self._error = error
        self._focused = False
        self._populated = False
        self._content: QWidget | None = None
        self._float = 0.0  # 0 = resting, 1 = floated

        if variant is FieldVariant.FILLED:
            radii = CornerRadii(_CORNER, _CORNER, 0.0, 0.0)
        else:
            radii = CornerRadii(_CORNER, _CORNER, _CORNER, _CORNER)
        self._init_material(
            shape=radii,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_HIGHEST,
        )
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(_ANIM))
        self._anim.setEasingCurve(easing_curve(Easing.STANDARD))
        self._anim.valueChanged.connect(self._set_float)

        self._label_font = font_for_role(TypescaleRole.BODY_LARGE)
        self._float_font = font_for_role(TypescaleRole.BODY_SMALL)
        self._support_font = font_for_role(TypescaleRole.BODY_SMALL)

    # -- content -----------------------------------------------------------

    def set_content(self, widget: QWidget) -> None:
        """Place the input/content widget inside the field and track its focus."""
        self._content = widget
        widget.setParent(self)
        widget.installEventFilter(self)
        self._relayout_content()
        widget.show()

    def set_populated(self, populated: bool) -> None:
        populated = bool(populated)
        if populated == self._populated:
            return
        self._populated = populated
        self._sync_float()

    def set_error(self, error: bool) -> None:
        self._error = bool(error)
        self.update()

    @property
    def variant(self) -> FieldVariant:
        return self._variant

    # -- focus / float -----------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._content:
            if event.type() == QEvent.Type.FocusIn:
                self._focused = True
                self._sync_float()
                self.update()
            elif event.type() == QEvent.Type.FocusOut:
                self._focused = False
                self._sync_float()
                self.update()
        return False

    def _should_float(self) -> bool:
        return self._focused or self._populated

    def _sync_float(self) -> None:
        target = 1.0 if self._should_float() else 0.0
        self._anim.stop()
        if not MOTION_ENABLED or not self.isVisible():
            self._set_float(target)
            return
        self._anim.setStartValue(self._float)
        self._anim.setEndValue(target)
        self._anim.start()

    def _set_float(self, value) -> None:
        self._float = float(value)
        self.update()

    # -- geometry ----------------------------------------------------------

    def sizeHint(self):  # noqa: N802
        from PySide6.QtCore import QSize

        h = _FIELD_H + (_SUPPORT_H if (self._supporting or self._error) else 0)
        return QSize(210, h)

    def minimumSizeHint(self):  # noqa: N802
        from PySide6.QtCore import QSize

        return QSize(120, self.sizeHint().height())

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._relayout_content()

    def _relayout_content(self) -> None:
        if self._content is None:
            return
        # Content sits in the lower part of the 56px box, leaving room for the
        # floated label at the top.
        top = 24 if self._label else 16
        self._content.setGeometry(
            _PAD, top, max(0, self.width() - 2 * _PAD), _FIELD_H - top - 8
        )

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        box = QRectF(0, 0, self.width(), _FIELD_H)

        accent = ColorRole.ERROR if self._error else (
            ColorRole.PRIMARY if self._focused else None
        )

        if self._variant is FieldVariant.FILLED:
            self._paint_filled(painter, theme, box, accent)
        else:
            self._paint_outlined(painter, theme, box, accent)

        self._paint_label(painter, theme, accent)
        self._paint_supporting(painter, theme)

    def _paint_filled(self, painter, theme, box, accent) -> None:
        path = rounded_path(box, self._radii)
        painter.fillPath(path, theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST))
        # Active indicator along the bottom.
        focused = accent is not None
        height = 2.0 if focused else 1.0
        role = accent or ColorRole.ON_SURFACE_VARIANT
        pen = QPen(theme.color(role))
        pen.setWidthF(height)
        painter.setPen(pen)
        y = _FIELD_H - height / 2.0
        painter.drawLine(QPointF(0, y), QPointF(self.width(), y))

    def _paint_outlined(self, painter, theme, box, accent) -> None:
        focused = accent is not None
        width = 2.0 if focused else 1.0
        role = accent or ColorRole.OUTLINE
        pen = QPen(theme.color(role))
        pen.setWidthF(width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        inset = width / 2.0
        rect = box.adjusted(inset, inset, -inset, -inset)
        path = rounded_path(rect, self._radii)
        # Notch the top border for the floated label.
        if self._label and self._float > 0.5:
            painter.save()
            metrics = QFontMetrics(self._float_font)
            label_w = metrics.horizontalAdvance(self._label) + 8
            from PySide6.QtGui import QRegion

            notch = QRegion(self.rect())
            notch = notch.subtracted(
                QRegion(int(_PAD - 2), 0, int(label_w), int(width + 2))
            )
            painter.setClipRegion(notch)
            painter.drawPath(path)
            painter.restore()
        else:
            painter.drawPath(path)

    def _paint_label(self, painter, theme, accent) -> None:
        if not self._label:
            return
        t = self._float
        role = accent or ColorRole.ON_SURFACE_VARIANT
        if not self.isEnabled():
            role = ColorRole.ON_SURFACE
        painter.setPen(theme.color(role))
        # Interpolate position/size between resting (centered) and floated (top).
        resting_y, floated_y = (_FIELD_H - 24) / 2.0 + 4, 6.0
        y = resting_y + (floated_y - resting_y) * t
        font = self._label_font if t < 0.5 else self._float_font
        painter.setFont(font)
        painter.drawText(
            QRectF(_PAD, y, self.width() - 2 * _PAD, 22),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._label,
        )

    def _paint_supporting(self, painter, theme) -> None:
        if not (self._supporting or self._error):
            return
        text = self._supporting
        role = ColorRole.ERROR if self._error else ColorRole.ON_SURFACE_VARIANT
        painter.setFont(self._support_font)
        painter.setPen(theme.color(role))
        painter.drawText(
            QRectF(_PAD, _FIELD_H + 2, self.width() - 2 * _PAD, _SUPPORT_H),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text,
        )


__all__ = ["FieldVariant", "MdField"]
