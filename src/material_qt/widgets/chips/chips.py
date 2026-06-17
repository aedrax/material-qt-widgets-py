"""Material 3 chips for QtWidgets.

Ports Material Web's ``chips/`` — assist, suggestion, filter and input chips plus
a chip set container. All chips are 32px tall, corner-small (8px), with a
``label-large`` label, an optional leading Material Symbols icon, ripple and
focus ring. Filter chips are selectable (secondary-container fill + leading
checkmark when selected); input chips carry a trailing remove icon and emit
``removed``.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QSizePolicy, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_HEIGHT = 32
_ICON = 18
_GAP = 8
_PAD = 16
_PAD_ICON = 8
_OUTLINE_WIDTH = 1.0
_DISABLED_LABEL_OPACITY = 0.38
_DISABLED_OUTLINE_OPACITY = 0.12


class MdChip(MaterialWidgetMixin, QAbstractButton):
    """Base chip. Use a variant subclass."""

    removed = Signal()

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        leading_icon: str = "",
        trailing_icon: str = "",
        selectable: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self._leading_icon = leading_icon
        self._trailing_icon = trailing_icon
        self.setCheckable(selectable)
        self._init_material(
            shape=ShapeScale.SMALL,
            typescale=TypescaleRole.LABEL_LARGE,
            ripple=True,
            focus_ring=True,
            ripple_role=ColorRole.ON_SURFACE_VARIANT,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, *_) -> None:
        # Selection can change the leading content (e.g. a filter chip's
        # checkmark), so the size hint changes — re-query the layout, don't just
        # repaint, or the label gets clipped.
        self.updateGeometry()
        self.adjustSize()
        self.update()

    # -- selection-dependent colors (overridden by FilterChip) -------------

    def _container_role(self) -> ColorRole | None:
        return None  # transparent (outlined)

    def _label_role(self) -> ColorRole:
        return ColorRole.ON_SURFACE

    def _outline_visible(self) -> bool:
        return self._container_role() is None

    def _show_leading_check(self) -> bool:
        return False

    # -- sizing ------------------------------------------------------------

    def _has_leading(self) -> bool:
        return bool(self._leading_icon) or self._show_leading_check()

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = metrics.horizontalAdvance(self.text())
        left = _PAD_ICON if self._has_leading() else _PAD
        right = _PAD_ICON if self._trailing_icon else _PAD
        total = left + w + right
        if self._has_leading():
            total += _ICON + _GAP
        if self._trailing_icon:
            total += _ICON + _GAP
        return QSize(total, _HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- interaction -------------------------------------------------------

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        # Trailing remove icon hit-test (input chips).
        if self._trailing_icon and self.rect().contains(event.position().toPoint()):
            x = self.width() - _PAD_ICON - _ICON
            if event.position().x() >= x:
                self.removed.emit()
                event.accept()
                return
        super().mouseReleaseEvent(event)

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

    def _glyph(self, painter, name, x, color) -> None:
        font = material_symbols_font(_ICON, filled=False)
        if font is None:
            return
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(QRectF(x, 0, _ICON, self.height()),
                         Qt.AlignmentFlag.AlignCenter, name)

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
                color.setAlphaF(_DISABLED_OUTLINE_OPACITY)
            painter.fillPath(path, color)

        if self._outline_visible():
            oc = theme.color(ColorRole.ON_SURFACE if not enabled else ColorRole.OUTLINE)
            if not enabled:
                oc.setAlphaF(_DISABLED_OUTLINE_OPACITY)
            pen = QPen(oc)
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = _OUTLINE_WIDTH / 2.0
            from ...core.shape_util import rounded_path

            painter.drawPath(
                rounded_path(QRectF(self.rect()).adjusted(inset, inset, -inset, -inset),
                             self._radii)
            )

        label_color = theme.color(self._label_role())
        if not enabled:
            label_color = theme.color(ColorRole.ON_SURFACE)
            label_color.setAlphaF(_DISABLED_LABEL_OPACITY)

        x = _PAD_ICON if self._has_leading() else _PAD
        if self._show_leading_check():
            self._glyph(painter, "check", x, label_color)
            x += _ICON + _GAP
        elif self._leading_icon:
            self._glyph(painter, self._leading_icon, x, label_color)
            x += _ICON + _GAP

        painter.setFont(self.font())
        painter.setPen(label_color)
        text_w = QFontMetrics(self.font()).horizontalAdvance(self.text())
        painter.drawText(QRectF(x, 0, text_w, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self.text())

        if self._trailing_icon:
            tx = self.width() - _PAD_ICON - _ICON
            self._glyph(painter, self._trailing_icon, tx, label_color)


class MdAssistChip(MdChip):
    def __init__(self, text="", parent=None, *, icon="") -> None:
        super().__init__(text, parent, leading_icon=icon)


class MdSuggestionChip(MdChip):
    def _label_role(self) -> ColorRole:
        return ColorRole.ON_SURFACE_VARIANT


class MdFilterChip(MdChip):
    def __init__(self, text="", parent=None, *, selected=False) -> None:
        super().__init__(text, parent, selectable=True)
        if selected:
            self.setChecked(True)

    def _container_role(self) -> ColorRole | None:
        return ColorRole.SECONDARY_CONTAINER if self.isChecked() else None

    def _label_role(self) -> ColorRole:
        return (
            ColorRole.ON_SECONDARY_CONTAINER
            if self.isChecked()
            else ColorRole.ON_SURFACE_VARIANT
        )

    def _show_leading_check(self) -> bool:
        return self.isChecked()


class MdInputChip(MdChip):
    def __init__(self, text="", parent=None, *, icon="") -> None:
        super().__init__(text, parent, leading_icon=icon, trailing_icon="close")


class MdChipSet(QWidget):
    """A horizontal container holding chips with consistent spacing."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(_GAP)
        self._lay.addStretch(1)

    def add_chip(self, chip: MdChip) -> None:
        self._lay.insertWidget(self._lay.count() - 1, chip)
        if isinstance(chip, MdInputChip):
            chip.removed.connect(lambda: self.remove_chip(chip))

    def remove_chip(self, chip: MdChip) -> None:
        self._lay.removeWidget(chip)
        chip.setParent(None)
        chip.deleteLater()


__all__ = [
    "MdAssistChip",
    "MdChip",
    "MdChipSet",
    "MdFilterChip",
    "MdInputChip",
    "MdSuggestionChip",
]
