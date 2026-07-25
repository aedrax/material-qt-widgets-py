"""Material 3 chips for QtWidgets.

Ports Material Web's ``chips/`` — assist, suggestion, choice, filter and input
chips plus a chip set container. All chips are 32px tall, corner-small (8px),
with a ``label-large`` label, an optional leading Material Symbols icon or
avatar image, ripple and focus ring. Filter and choice chips are selectable
(secondary-container fill when selected); filter chips also show a leading
checkmark. Input chips (and optionally filter chips) carry a trailing remove
icon and emit ``removed``. An ``elevated`` form drops the outline for a
surface-container-low fill plus a level-1 shadow.

Idiomatic QObject surface (mirrors ``QAbstractButton``):

* ``clicked`` — emitted on tap (Flutter ``onPressed``).
* ``toggled(bool)`` — selection changes (Flutter ``onSelected``).
* ``removed`` — the trailing delete affordance was activated (``onDeleted``).
* ``set_label`` / ``label`` — the chip text (Flutter ``label``).
* ``set_label_style`` — the label ``QFont`` (Flutter ``labelStyle``).
* ``set_selected`` / ``selected`` — selection state (Flutter ``selected``).
* ``set_leading_icon`` / ``set_avatar`` / ``set_trailing_icon`` — leading glyph,
  leading image, trailing glyph.
* ``set_background_color`` / ``set_selected_color`` — container theme
  :class:`ColorRole` overrides (Flutter ``backgroundColor`` / ``selectedColor``).
* ``set_checkmark_color`` / ``set_show_checkmark`` — filter/choice check styling.
* ``setEnabled`` / ``setToolTip`` — Flutter ``isEnabled`` / ``tooltip``.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QSizePolicy, QWidget

from ...core.elevation import apply_elevation
from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import CornerRadii, ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_HEIGHT = 32
_ICON = 18
_AVATAR = 24
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
        avatar: QPixmap | None = None,
        selectable: bool = False,
        elevated: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self._leading_icon = leading_icon
        self._trailing_icon = trailing_icon
        self._avatar: QPixmap | None = avatar
        self._elevated = elevated
        # Theme-role color overrides (None -> use the variant default).
        self._background_role: ColorRole | None = None
        self._selected_role: ColorRole | None = None
        self._checkmark_role: ColorRole | None = None
        self._show_checkmark = True
        self._press_in_trailing = False
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
        if self._elevated:
            ThemeManager.instance().themeChanged.connect(self._apply_elevation)
            self._apply_elevation()

    def _on_toggled(self, *_) -> None:
        # Selection can change the leading content (e.g. a filter chip's
        # checkmark), so the size hint changes — re-query the layout, don't just
        # repaint, or the label gets clipped.
        self.updateGeometry()
        self.adjustSize()
        self.update()

    def _apply_elevation(self) -> None:
        level = ElevationLevel.LEVEL1 if self.isEnabled() else ElevationLevel.LEVEL0
        apply_elevation(self, level)

    # -- idiomatic property surface ---------------------------------------

    @property
    def label(self) -> str:
        """The chip text (Flutter ``label``)."""
        return self.text()

    def set_label(self, text: str) -> None:
        """Set the chip text."""
        self.setText(text)
        self.updateGeometry()
        self.adjustSize()
        self.update()

    def set_label_style(self, font: QFont) -> None:
        """Set the label ``QFont`` (Flutter ``labelStyle``)."""
        self.setFont(font)
        self.updateGeometry()
        self.adjustSize()
        self.update()

    @property
    def selected(self) -> bool:
        """Selection state (Flutter ``selected``); only meaningful when selectable."""
        return self.isChecked()

    def set_selected(self, value: bool) -> None:
        """Set the selection state."""
        self.setChecked(bool(value))

    def set_leading_icon(self, name: str) -> None:
        """Set the leading Material Symbols glyph name (empty clears it)."""
        self._leading_icon = name
        self.updateGeometry()
        self.adjustSize()
        self.update()

    def set_avatar(self, pixmap: QPixmap | None) -> None:
        """Set the leading avatar image (Flutter ``avatar``); ``None`` clears it."""
        self._avatar = pixmap
        self.updateGeometry()
        self.adjustSize()
        self.update()

    @property
    def avatar(self) -> QPixmap | None:
        """The leading avatar image, if any."""
        return self._avatar

    def set_trailing_icon(self, name: str) -> None:
        """Set the trailing Material Symbols glyph name (empty clears it)."""
        self._trailing_icon = name
        self.updateGeometry()
        self.adjustSize()
        self.update()

    def set_background_color(self, role: ColorRole | None) -> None:
        """Override the unselected container :class:`ColorRole` (Flutter ``backgroundColor``)."""
        self._background_role = role
        self.update()

    def set_selected_color(self, role: ColorRole | None) -> None:
        """Override the selected container :class:`ColorRole` (Flutter ``selectedColor``)."""
        self._selected_role = role
        self.update()

    def set_checkmark_color(self, role: ColorRole | None) -> None:
        """Override the leading checkmark :class:`ColorRole` (Flutter ``checkmarkColor``)."""
        self._checkmark_role = role
        self.update()

    def set_show_checkmark(self, value: bool) -> None:
        """Whether selected filter/choice chips show a leading checkmark (Flutter ``showCheckmark``)."""
        self._show_checkmark = bool(value)
        self.updateGeometry()
        self.adjustSize()
        self.update()

    # -- selection-dependent colors (overridden by subclasses) -------------

    def _container_role(self) -> ColorRole | None:
        if self._background_role is not None:
            return self._background_role
        # Elevated chips have a filled body (no outline); flat chips are
        # transparent and rely on the outline.
        return ColorRole.SURFACE_CONTAINER_LOW if self._elevated else None

    def _label_role(self) -> ColorRole:
        return ColorRole.ON_SURFACE

    def _outline_visible(self) -> bool:
        # The outline shows only on a flat, unfilled chip.
        return not self._elevated and self._container_role() is None

    def _show_leading_check(self) -> bool:
        return False

    # -- sizing ------------------------------------------------------------

    def _has_leading(self) -> bool:
        return (
            bool(self._leading_icon)
            or self._avatar is not None
            or self._show_leading_check()
        )

    def _leading_size(self) -> int:
        if self._show_leading_check():
            return _ICON
        return _AVATAR if self._avatar is not None else _ICON

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = metrics.horizontalAdvance(self.text())
        left = _PAD_ICON if self._has_leading() else _PAD
        right = _PAD_ICON if self._trailing_icon else _PAD
        total = left + w + right
        if self._has_leading():
            total += self._leading_size() + _GAP
        if self._trailing_icon:
            total += _ICON + _GAP
        return QSize(total, _HEIGHT)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- interaction -------------------------------------------------------

    def _in_trailing_zone(self, pos) -> bool:
        """Whether ``pos`` hits the trailing remove icon zone."""
        if not self._trailing_icon:
            return False
        if not self.rect().contains(pos.toPoint()):
            return False
        return pos.x() >= self.width() - _PAD_ICON - _ICON

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self._press_in_trailing = self._in_trailing_zone(event.position())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        # Trailing remove icon hit-test (input chips / deletable filter chips):
        # activate only when the press also started in the trailing zone.
        press_in_trailing = self._press_in_trailing
        self._press_in_trailing = False
        if press_in_trailing and self._in_trailing_zone(event.position()):
            self.setDown(False)  # super() is skipped; don't leave the chip pressed
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
        if event.type() == QEvent.Type.EnabledChange:
            if self.ripple is not None:
                self.ripple.set_enabled(self.isEnabled())
            if self._elevated:
                self._apply_elevation()
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

    def _draw_avatar(self, painter, x) -> None:
        pm = self._avatar
        if pm is None or pm.isNull():
            return
        y = (self.height() - _AVATAR) / 2.0
        target = QRectF(x, y, _AVATAR, _AVATAR)
        painter.save()
        painter.setClipPath(rounded_path(target, CornerRadii.uniform(_AVATAR / 2.0)))
        painter.drawPixmap(target, pm, QRectF(pm.rect()))
        painter.restore()

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
            check_color = label_color
            if enabled and self._checkmark_role is not None:
                check_color = theme.color(self._checkmark_role)
            self._glyph(painter, "check", x, check_color)
            x += _ICON + _GAP
        elif self._avatar is not None:
            self._draw_avatar(painter, x)
            x += _AVATAR + _GAP
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
    """Action chip — performs an action (Flutter ``ActionChip``)."""

    def __init__(self, text="", parent=None, *, icon="", avatar=None, elevated=False) -> None:
        super().__init__(text, parent, leading_icon=icon, avatar=avatar, elevated=elevated)


class MdSuggestionChip(MdChip):
    """Suggestion chip — a dynamically generated action (Flutter ``ActionChip``)."""

    def __init__(self, text="", parent=None, *, icon="", avatar=None, elevated=False) -> None:
        super().__init__(text, parent, leading_icon=icon, avatar=avatar, elevated=elevated)

    def _label_role(self) -> ColorRole:
        return ColorRole.ON_SURFACE_VARIANT


class _SelectableChip(MdChip):
    """Shared base for chips that toggle a secondary-container fill on selection."""

    def __init__(self, text="", parent=None, *, icon="", avatar=None,
                 selected=False, elevated=False, **kwargs) -> None:
        super().__init__(text, parent, leading_icon=icon, avatar=avatar,
                         selectable=True, elevated=elevated, **kwargs)
        if selected:
            self.setChecked(True)

    def _container_role(self) -> ColorRole | None:
        if self.isChecked():
            return self._selected_role or ColorRole.SECONDARY_CONTAINER
        if self._background_role is not None:
            return self._background_role
        # An elevated chip keeps a filled body even when unselected.
        return ColorRole.SURFACE_CONTAINER_LOW if self._elevated else None

    def _label_role(self) -> ColorRole:
        return (
            ColorRole.ON_SECONDARY_CONTAINER
            if self.isChecked()
            else ColorRole.ON_SURFACE_VARIANT
        )

    def _outline_visible(self) -> bool:
        # The outline shows only on a flat, unfilled, unselected chip.
        return not self._elevated and not self.isChecked() and self._container_role() is None


class MdChoiceChip(_SelectableChip):
    """Choice chip — single-select within a set (Flutter ``ChoiceChip``).

    Unlike a filter chip, a choice chip shows **no** leading checkmark when
    selected — selection is conveyed by the container fill alone. Group several
    in a ``QButtonGroup`` (exclusive) for single-select behaviour.
    """


class MdFilterChip(_SelectableChip):
    """Filter chip — toggles a filter and shows a leading checkmark when selected
    (Flutter ``FilterChip``). Pass ``deletable=True`` for a trailing remove
    affordance that emits ``removed`` (Flutter ``onDeleted``)."""

    def __init__(self, text="", parent=None, *, icon="", avatar=None,
                 selected=False, deletable=False, elevated=False) -> None:
        super().__init__(text, parent, icon=icon, avatar=avatar,
                         selected=selected, elevated=elevated,
                         trailing_icon="close" if deletable else "")

    def _show_leading_check(self) -> bool:
        return self.isChecked() and self._show_checkmark


class MdInputChip(MdChip):
    """Input chip — represents a discrete piece of input; deletable (Flutter
    ``InputChip``). Emits ``removed`` when the trailing icon is activated."""

    def __init__(self, text="", parent=None, *, icon="", avatar=None) -> None:
        super().__init__(text, parent, leading_icon=icon, avatar=avatar,
                         trailing_icon="close")


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
        # Any chip that exposes a delete affordance is removed from the set on
        # ``removed`` (input chips, and filter chips created with deletable=True).
        if chip._trailing_icon:
            chip.removed.connect(lambda: self.remove_chip(chip))

    def remove_chip(self, chip: MdChip) -> None:
        self._lay.removeWidget(chip)
        chip.setParent(None)
        chip.deleteLater()


__all__ = [
    "MdAssistChip",
    "MdChip",
    "MdChipSet",
    "MdChoiceChip",
    "MdFilterChip",
    "MdInputChip",
    "MdSuggestionChip",
]
