"""Material 3 segmented buttons for QtWidgets.

Ports Material Web's ``labs/segmentedbutton`` + ``segmentedbuttonset`` — a row of
connected outlined segments, 40px tall, with corner-full outer ends. Segments
are selectable; the set supports single-select (exclusive) or multi-select. A
selected segment fills with ``secondary-container`` and shows a leading
checkmark.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QEvent, QRectF, QSize, Qt
from PySide6.QtGui import QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_HEIGHT = 40
_RADIUS = _HEIGHT / 2.0  # corner-full ends
_ICON = 18
_GAP = 8
_PAD = 12
_OUTLINE_WIDTH = 1.0


class _Pos(Enum):
    ONLY = "only"
    FIRST = "first"
    MIDDLE = "middle"
    LAST = "last"


class MdSegmentedButton(MaterialWidgetMixin, QAbstractButton):
    """A single segment in a segmented button set."""

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        super().__init__(parent)
        self.setText(text)
        self._icon = icon
        self._pos = _Pos.ONLY
        self.setCheckable(True)
        self._init_material(
            shape=CornerRadii(0.0, 0.0, 0.0, 0.0),  # real shape set in _apply_pos
            typescale=TypescaleRole.LABEL_LARGE,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggled.connect(lambda *_: self.update())
        self._apply_pos()

    def set_position(self, pos: _Pos) -> None:
        self._pos = pos
        self._apply_pos()

    def _apply_pos(self) -> None:
        if self._pos is _Pos.ONLY:
            radii = CornerRadii(_RADIUS, _RADIUS, _RADIUS, _RADIUS)
        elif self._pos is _Pos.FIRST:
            radii = CornerRadii(_RADIUS, 0.0, 0.0, _RADIUS)
        elif self._pos is _Pos.LAST:
            radii = CornerRadii(0.0, _RADIUS, _RADIUS, 0.0)
        else:
            radii = CornerRadii(0.0, 0.0, 0.0, 0.0)
        self.set_radii(radii)

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = _PAD * 2 + metrics.horizontalAdvance(self.text())
        if self._icon or self.isChecked():
            w += _ICON + _GAP
        return QSize(max(w, 48), _HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(48, _HEIGHT)

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

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        path = self.clip_path()

        if self.isChecked():
            painter.fillPath(path, theme.color(ColorRole.SECONDARY_CONTAINER))

        # Outline: draw the segment border. Shared inner edges overlap exactly.
        pen = QPen(theme.color(ColorRole.OUTLINE))
        pen.setWidthF(_OUTLINE_WIDTH)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        inset = _OUTLINE_WIDTH / 2.0
        painter.drawPath(
            rounded_path(QRectF(self.rect()).adjusted(inset, inset, -inset, -inset),
                         self._radii)
        )

        label_role = (
            ColorRole.ON_SECONDARY_CONTAINER if self.isChecked()
            else ColorRole.ON_SURFACE
        )
        color = theme.color(label_role)
        metrics = QFontMetrics(self.font())
        text_w = metrics.horizontalAdvance(self.text())
        lead = _ICON + _GAP if (self.isChecked() or self._icon) else 0
        x = (self.width() - (lead + text_w)) / 2.0
        if self.isChecked():
            self._glyph(painter, "check", x, color)
            x += _ICON + _GAP
        elif self._icon:
            self._glyph(painter, self._icon, x, color)
            x += _ICON + _GAP
        painter.setFont(self.font())
        painter.setPen(color)
        painter.drawText(QRectF(x, 0, text_w, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self.text())

    def _glyph(self, painter, name, x, color) -> None:
        font = material_symbols_font(_ICON, filled=False)
        if font is None:
            return
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(QRectF(x, 0, _ICON, self.height()),
                         Qt.AlignmentFlag.AlignCenter, name)


class MdSegmentedButtonSet(QWidget):
    """A connected row of segments (single- or multi-select)."""

    def __init__(self, parent: QWidget | None = None, *, multi: bool = False) -> None:
        super().__init__(parent)
        self._multi = multi
        self._segments: list[MdSegmentedButton] = []
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._group = None if multi else QButtonGroup(self)
        if self._group is not None:
            self._group.setExclusive(True)
        self.setFixedHeight(_HEIGHT)

    def add_segment(self, segment: MdSegmentedButton) -> None:
        self._segments.append(segment)
        self._lay.addWidget(segment)
        if self._group is not None:
            self._group.addButton(segment)
        self._restyle_positions()

    def _restyle_positions(self) -> None:
        n = len(self._segments)
        for i, seg in enumerate(self._segments):
            if n == 1:
                seg.set_position(_Pos.ONLY)
            elif i == 0:
                seg.set_position(_Pos.FIRST)
            elif i == n - 1:
                seg.set_position(_Pos.LAST)
            else:
                seg.set_position(_Pos.MIDDLE)


__all__ = ["MdSegmentedButton", "MdSegmentedButtonSet"]
