"""Material 3 navigation tab (labs) for QtWidgets.

Ports Material Web's ``labs/navigationtab`` — a destination in a navigation bar:
a 24px icon inside a pill active indicator with a ``label-medium`` label below.
When active, the indicator fills ``secondary-container``, the icon uses
``on-secondary-container`` (filled), and the label is ``on-surface``; inactive
uses ``on-surface-variant``. Built on :class:`QAbstractButton` (checkable).

Supports Flutter's ``labelBehavior`` (``"always"`` / ``"selected"`` / ``"hide"``;
when no label shows the icon centres vertically) and an optional badge on the
icon (a dot, or a small ``error`` count pill) via :meth:`set_badge`.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import QAbstractButton, QSizePolicy, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_ICON = 24
_INDICATOR_W = 64
_INDICATOR_H = 32
_TAB_HEIGHT = 64
_TOP = 12
_LABEL_GAP = 4
_BADGE_H = 16


class MdNavigationTab(MaterialWidgetMixin, QAbstractButton):
    """A single navigation destination (icon + label)."""

    def __init__(
        self,
        label: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        active_icon: str = "",
    ) -> None:
        super().__init__(parent)
        self.setText(label)
        self._icon = icon
        self._active_icon = active_icon or icon
        self._label_behavior = "always"  # "always" | "selected" | "hide"
        self._badge: str | None = None  # None=off, ""=dot, else count text
        self.setCheckable(True)
        # Ripple clipped to the pill indicator shape (corner-full).
        self._init_material(
            shape=CornerRadii.uniform(_INDICATOR_H / 2.0),
            typescale=TypescaleRole.LABEL_MEDIUM,
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE_VARIANT,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggled.connect(lambda *_: self.update())

    def set_label_behavior(self, behavior: str) -> None:
        self._label_behavior = behavior
        self.update()

    def set_badge(self, value: str | None) -> None:
        """Show a badge on the icon: ``""`` for a dot, a string for a count,
        ``None`` to hide it."""
        self._badge = value
        self.update()

    def _shows_label(self) -> bool:
        if self._label_behavior == "always":
            return True
        if self._label_behavior == "selected":
            return self.isChecked()
        return False

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = max(_INDICATOR_W, metrics.horizontalAdvance(self.text()) + 16)
        return QSize(w, _TAB_HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(_INDICATOR_W, _TAB_HEIGHT)

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

    def _indicator_rect(self) -> QRectF:
        cx = self.width() / 2.0
        top = _TOP if self._shows_label() else (_TAB_HEIGHT - _INDICATOR_H) / 2.0
        return QRectF(cx - _INDICATOR_W / 2.0, top, _INDICATOR_W, _INDICATOR_H)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        active = self.isChecked()
        indicator = self._indicator_rect()

        if active:
            path = rounded_path(indicator, CornerRadii.uniform(_INDICATOR_H / 2.0))
            painter.fillPath(path, theme.color(ColorRole.SECONDARY_CONTAINER))

        icon_color = theme.color(
            ColorRole.ON_SECONDARY_CONTAINER if active else ColorRole.ON_SURFACE_VARIANT
        )
        glyph = self._active_icon if active else self._icon
        if glyph:
            font = material_symbols_font(_ICON, filled=active)
            if font is not None:
                painter.setFont(font)
                painter.setPen(icon_color)
                painter.drawText(indicator, Qt.AlignmentFlag.AlignCenter, glyph)

        if self._badge is not None:
            self._paint_badge(painter, indicator, theme)

        if self._shows_label():
            label_color = theme.color(
                ColorRole.ON_SURFACE if active else ColorRole.ON_SURFACE_VARIANT
            )
            painter.setFont(self.font())
            painter.setPen(label_color)
            label_rect = QRectF(
                0, indicator.bottom() + _LABEL_GAP, self.width(),
                _TAB_HEIGHT - indicator.bottom() - _LABEL_GAP,
            )
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter
                             | Qt.AlignmentFlag.AlignTop, self.text())

    def _paint_badge(self, painter: QPainter, indicator: QRectF, theme) -> None:
        cx = self.width() / 2.0
        error = theme.color(ColorRole.ERROR)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(error)
        if self._badge == "":  # small dot at the icon's top-right
            painter.drawEllipse(QPointF(cx + 8, indicator.top() + 6), 3.0, 3.0)
            return
        # Count pill: error container with on-error label.
        painter.setFont(font_for_role(TypescaleRole.LABEL_SMALL))
        text = str(self._badge)
        tw = QFontMetrics(painter.font()).horizontalAdvance(text) + 8
        bx = cx + 6
        by = indicator.top() - 2
        rect = QRectF(bx, by, max(_BADGE_H, tw), _BADGE_H)
        painter.drawRoundedRect(rect, _BADGE_H / 2.0, _BADGE_H / 2.0)
        painter.setPen(theme.color(ColorRole.ON_ERROR))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


__all__ = ["MdNavigationTab"]
