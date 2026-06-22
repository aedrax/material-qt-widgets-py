"""Material 3 navigation rail for QtWidgets.

Ports the Material 3 navigation rail (cf. Flutter's ``NavigationRail`` /
``_NavigationRailDefaultsM3``) — a vertical ``surface`` rail of destinations with
exclusive selection. Each destination is a 24px icon in a 56x32
``secondary-container`` pill indicator. ``changed(index)`` fires when the active
destination changes.

Beyond the compact 80px rail it supports the full NavigationRail surface:

* **extended** — animate to a 256px rail with labels beside the icons
  (:meth:`set_extended`);
* **label type** — ``"all"`` / ``"selected"`` / ``"none"`` controls compact-mode
  labels (:meth:`set_label_type`);
* **group alignment** — ``"top"`` / ``"center"`` / ``"bottom"`` positions the
  destination group (:meth:`set_group_alignment`);
* **leading / trailing** widgets pinned above / below the group.

The public API mirrors :class:`MdNavigationBar`: ``changed = Signal(int)`` and
``add_destination(label, *, icon, active_icon)``.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_RAIL_WIDTH = 80
_EXTENDED_WIDTH = 256
_ICON = 24
_INDICATOR_W = 56
_INDICATOR_H = 32
_DEST_H = 56  # with a label
_DEST_H_NO_LABEL = 48
_LABEL_GAP = 4
_DEST_SPACING = 12
_TOP_PADDING = 8
_LABEL_PAD = 12


class _RailDestination(MaterialWidgetMixin, QAbstractButton):
    """A single navigation-rail destination (icon pill + label)."""

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
        self._extended = False
        self._label_type = "all"
        self.setCheckable(True)
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

    # -- configuration (set by the rail) -----------------------------------

    def set_extended(self, extended: bool) -> None:
        self._extended = extended
        self.updateGeometry()
        self.update()

    def set_label_type(self, label_type: str) -> None:
        self._label_type = label_type
        self.updateGeometry()
        self.update()

    def _shows_label(self) -> bool:
        if self._extended or self._label_type == "all":
            return True
        if self._label_type == "selected":
            return self.isChecked()
        return False

    def _height(self) -> int:
        if self._extended or self._label_type != "none":
            return _DEST_H
        return _DEST_H_NO_LABEL

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        w = _EXTENDED_WIDTH if self._extended else _RAIL_WIDTH
        return QSize(w, self._height())

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(_INDICATOR_W, self._height())

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

    def _indicator_rect(self) -> QRectF:
        # The icon stays centered in the compact 80px zone in both modes, so
        # extending only reveals labels to the right.
        cx = _RAIL_WIDTH / 2.0
        if self._extended:
            cy = self.height() / 2.0
            return QRectF(cx - _INDICATOR_W / 2.0, cy - _INDICATOR_H / 2.0,
                          _INDICATOR_W, _INDICATOR_H)
        top = 0.0 if self._shows_label() else (self.height() - _INDICATOR_H) / 2.0
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

        if not self._shows_label() or not self.text():
            return
        label_color = theme.color(
            ColorRole.ON_SURFACE if active else ColorRole.ON_SURFACE_VARIANT
        )
        painter.setFont(self.font())
        painter.setPen(label_color)
        if self._extended:
            label_rect = QRectF(_RAIL_WIDTH, 0,
                                self.width() - _RAIL_WIDTH - _LABEL_PAD, self.height())
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignVCenter
                             | Qt.AlignmentFlag.AlignLeft, self.text())
        else:
            label_rect = QRectF(0, indicator.bottom() + _LABEL_GAP, self.width(),
                                self.height() - indicator.bottom() - _LABEL_GAP)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter
                             | Qt.AlignmentFlag.AlignTop, self.text())


class MdNavigationRail(MaterialWidgetMixin, QWidget):
    """A vertical navigation rail of icon+label destinations."""

    changed = Signal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        extended: bool = False,
        label_type: str = "all",
        group_alignment: str = "top",
        leading_at_top: bool = True,
        trailing_at_bottom: bool = False,
    ) -> None:
        super().__init__(parent)
        self._dests: list[_RailDestination] = []
        self._leading: QWidget | None = None
        self._trailing: QWidget | None = None
        self._extended = extended
        self._label_type = label_type
        self._group = group_alignment
        self._leading_at_top = leading_at_top
        self._trailing_at_bottom = trailing_at_bottom
        self._buttons = QButtonGroup(self)
        self._buttons.setExclusive(True)

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, _TOP_PADDING, 0, _TOP_PADDING)
        self._lay.setSpacing(_DEST_SPACING)
        self._init_material(
            shape=CornerRadii.uniform(0.0),
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        self.setFixedWidth(_EXTENDED_WIDTH if extended else _RAIL_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._width_anim = QVariantAnimation(self)
        self._width_anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._width_anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._width_anim.valueChanged.connect(lambda v: self.setFixedWidth(int(v)))
        self._relayout()

    # -- slots / destinations ---------------------------------------------

    def set_leading(self, widget: QWidget, *, at_top: bool | None = None) -> None:
        self._leading = widget
        if at_top is not None:
            self._leading_at_top = at_top
        self._relayout()

    def set_trailing(self, widget: QWidget, *, at_bottom: bool | None = None) -> None:
        self._trailing = widget
        if at_bottom is not None:
            self._trailing_at_bottom = at_bottom
        self._relayout()

    # -- selection (Flutter ``selectedIndex`` / ``onDestinationSelected``) ---

    @property
    def selected_index(self) -> int:
        """Index of the active destination, or ``-1`` if none."""
        return self._buttons.checkedId()

    @selected_index.setter
    def selected_index(self, index: int) -> None:
        self.set_selected_index(index)

    def set_selected_index(self, index: int) -> None:
        """Programmatically select the destination at ``index``."""
        button = self._buttons.button(index)
        if button is not None:
            button.setChecked(True)

    def add_destination(self, label: str, *, icon: str = "",
                        active_icon: str = "") -> _RailDestination:
        dest = _RailDestination(label, icon=icon, active_icon=active_icon)
        dest.set_extended(self._extended)
        dest.set_label_type(self._label_type)
        self._buttons.addButton(dest, len(self._dests))
        self._dests.append(dest)
        dest.toggled.connect(
            lambda on, d=dest: on and self.changed.emit(self._dests.index(d))
        )
        if len(self._dests) == 1:
            dest.setChecked(True)
        self._relayout()
        return dest

    # -- configuration -----------------------------------------------------

    @property
    def extended(self) -> bool:
        return self._extended

    def set_extended(self, extended: bool, *, animated: bool = True) -> None:
        if extended == self._extended:
            return
        self._extended = extended
        for d in self._dests:
            d.set_extended(extended)
        target = _EXTENDED_WIDTH if extended else _RAIL_WIDTH
        if animated and MOTION_ENABLED:
            self._width_anim.stop()
            self._width_anim.setStartValue(self.width())
            self._width_anim.setEndValue(target)
            self._width_anim.start()
        else:
            self.setFixedWidth(target)

    def set_label_type(self, label_type: str) -> None:
        self._label_type = label_type
        for d in self._dests:
            d.set_label_type(label_type)

    def set_group_alignment(self, alignment: str) -> None:
        self._group = alignment
        self._relayout()

    def set_leading_at_top(self, at_top: bool) -> None:
        """``True`` pins the leading widget to the rail's top; ``False`` keeps it
        adjacent to the destination group (Flutter ``leadingAtTop``)."""
        self._leading_at_top = at_top
        self._relayout()

    def set_trailing_at_bottom(self, at_bottom: bool) -> None:
        """``True`` pins the trailing widget to the rail's bottom; ``False`` keeps
        it adjacent to the destination group (Flutter ``trailingAtBottom``)."""
        self._trailing_at_bottom = at_bottom
        self._relayout()

    # -- layout ------------------------------------------------------------

    def _relayout(self) -> None:
        while self._lay.count():
            self._lay.takeAt(0)  # widgets stay parented to self; spacers dropped
        # leadingAtTop: pin above the group's leading stretch; otherwise let it
        # ride with the destinations after the stretch.
        if self._leading is not None and self._leading_at_top:
            self._lay.addWidget(self._leading, 0, Qt.AlignmentFlag.AlignHCenter)
        if self._group in ("center", "bottom"):
            self._lay.addStretch(1)
        if self._leading is not None and not self._leading_at_top:
            self._lay.addWidget(self._leading, 0, Qt.AlignmentFlag.AlignHCenter)
        for d in self._dests:
            self._lay.addWidget(d)
        # trailingAtBottom: pin below the group's trailing stretch; otherwise
        # place it directly under the destinations.
        if self._trailing is not None and not self._trailing_at_bottom:
            self._lay.addWidget(self._trailing, 0, Qt.AlignmentFlag.AlignHCenter)
        if self._group in ("center", "top"):
            self._lay.addStretch(1)
        if self._trailing is not None and self._trailing_at_bottom:
            self._lay.addWidget(self._trailing, 0, Qt.AlignmentFlag.AlignHCenter)

    def sizeHint(self) -> QSize:  # noqa: N802
        w = _EXTENDED_WIDTH if self._extended else _RAIL_WIDTH
        height = _TOP_PADDING * 2 + sum(d.sizeHint().height() for d in self._dests) \
            + _DEST_SPACING * max(0, len(self._dests) - 1)
        return QSize(w, max(height, _RAIL_WIDTH))

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdNavigationRail"]
