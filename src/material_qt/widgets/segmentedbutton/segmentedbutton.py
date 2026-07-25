"""Material 3 segmented buttons for QtWidgets.

Ports Material Web's ``labs/segmentedbutton`` + ``segmentedbuttonset`` — a row of
connected outlined segments, 40px tall, with corner-full outer ends. Segments
are selectable; the set supports single-select (exclusive) or multi-select. A
selected segment fills with ``secondary-container`` and shows a leading
checkmark.

This mirrors Flutter's ``SegmentedButton`` / ``ButtonSegment`` pair:

* :class:`MdSegmentedButtonSet` ↔ ``SegmentedButton`` — owns ``selected``,
  ``multiSelectionEnabled``, ``emptySelectionAllowed``, ``showSelectedIcon``,
  ``selectedIcon`` and the ``onSelectionChanged`` callback (the ``changed`` /
  ``selectionChanged`` Signals here).
* :class:`MdSegmentedButton` ↔ ``ButtonSegment`` — a single segment carrying a
  ``value``, label (``text``), ``icon``, ``tooltip`` and ``enabled`` flag.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
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
_DEFAULT_SELECTED_ICON = "check"

# Distinct sentinel so a caller-supplied ``value=None`` is preserved rather than
# being mistaken for "unset" and replaced with the segment index.
_UNSET = object()


class _Pos(Enum):
    ONLY = "only"
    FIRST = "first"
    MIDDLE = "middle"
    LAST = "last"


class MdSegmentedButton(MaterialWidgetMixin, QAbstractButton):
    """A single segment in a segmented button set.

    Maps to Flutter ``ButtonSegment``: carries a ``value`` (used to identify the
    segment in selection sets), an optional ``icon`` and label (``text``), an
    optional ``tooltip`` (via native ``setToolTip``) and an ``enabled`` flag (via
    native ``setEnabled``).
    """

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        value: Any = _UNSET,
        tooltip: str = "",
        enabled: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self._icon = icon
        self._value = value
        self._pos = _Pos.ONLY
        # Selected-icon behaviour is owned by the parent set, but stored per
        # segment so painting is self-contained.
        self._show_selected_icon = True
        self._selected_icon = _DEFAULT_SELECTED_ICON
        if tooltip:
            self.setToolTip(tooltip)
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
        self.toggled.connect(self._on_toggled)
        self.setEnabled(enabled)
        self._apply_pos()

    def _on_toggled(self, *_) -> None:
        # Selection adds/removes the leading checkmark, so the size hint
        # changes — re-query the layout (updateGeometry), don't just repaint,
        # or a snug layout clips the check + label.
        self.updateGeometry()
        self.update()

    # -- value (Flutter ButtonSegment.value) ------------------------------

    def has_explicit_value(self) -> bool:
        """Whether a ``value`` was supplied (vs. the index-fallback sentinel)."""
        return self._value is not _UNSET

    def value(self) -> Any:
        """The segment's identifying value (defaults to its index if unset)."""
        return None if self._value is _UNSET else self._value

    def set_value(self, value: Any) -> None:
        self._value = value

    # -- selected-icon config (driven by the parent set) ------------------

    def set_show_selected_icon(self, show: bool) -> None:
        if self._show_selected_icon != show:
            self._show_selected_icon = show
            self.updateGeometry()
            self.update()

    def set_selected_icon(self, name: str) -> None:
        name = name or _DEFAULT_SELECTED_ICON
        if self._selected_icon != name:
            self._selected_icon = name
            self.update()

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

    def _shows_leading_glyph(self) -> bool:
        """Whether a leading glyph (selected check or icon) is drawn."""
        if self.isChecked() and self._show_selected_icon:
            return True
        return bool(self._icon)

    def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        w = _PAD * 2 + metrics.horizontalAdvance(self.text())
        if self._shows_leading_glyph():
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
        show_check = self.isChecked() and self._show_selected_icon
        lead = _ICON + _GAP if (show_check or self._icon) else 0
        x = (self.width() - (lead + text_w)) / 2.0
        if show_check:
            self._glyph(painter, self._selected_icon, x, color)
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
    """A connected row of segments (single- or multi-select).

    Maps to Flutter ``SegmentedButton``. The selection changes are reported via
    the ``changed`` Signal (a list of selected indices, mirroring sibling
    :class:`~material_qt.widgets.buttongroup.MdButtonGroup`); ``selectionChanged``
    is an alias that carries the list of selected segment *values*, closer to
    Flutter's ``onSelectionChanged(Set<T>)``.

    Args:
        multi: if ``True`` more than one segment may be selected at a time
            (Flutter ``multiSelectionEnabled``).
        empty_selection_allowed: if ``True`` the user may deselect the last
            selected segment, leaving nothing selected (Flutter
            ``emptySelectionAllowed``). When ``False`` (default) at least one
            segment stays selected once any is.
        show_selected_icon: if ``True`` (default) a leading checkmark is shown on
            selected segments (Flutter ``showSelectedIcon``).
        selected_icon: the glyph used for the selected indicator (Flutter
            ``selectedIcon``); defaults to ``"check"``.
    """

    #: Emitted with the list of selected segment indices when the selection
    #: changes (mirrors :class:`MdButtonGroup`).
    changed = Signal(list)
    #: Emitted with the list of selected segment values (Flutter parity alias
    #: for ``onSelectionChanged``).
    selectionChanged = Signal(list)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        multi: bool = False,
        empty_selection_allowed: bool = False,
        show_selected_icon: bool = True,
        selected_icon: str = _DEFAULT_SELECTED_ICON,
    ) -> None:
        super().__init__(parent)
        self._multi = multi
        self._empty_allowed = empty_selection_allowed
        self._show_selected_icon = show_selected_icon
        self._selected_icon = selected_icon or _DEFAULT_SELECTED_ICON
        self._segments: list[MdSegmentedButton] = []
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        # A native exclusive QButtonGroup gives us single-select where the last
        # selection cannot be cleared by clicking it — exactly the
        # empty-disallowed single-select behaviour. Every other combination
        # (multi-select, or single-select that allows an empty selection) is
        # managed manually in ``_on_toggled``.
        self._group: QButtonGroup | None = None
        if not multi and not empty_selection_allowed:
            self._group = QButtonGroup(self)
            self._group.setExclusive(True)
        self.setFixedHeight(_HEIGHT)

    # -- segments ----------------------------------------------------------

    def add_segment(self, segment: MdSegmentedButton) -> None:
        if not segment.has_explicit_value():
            segment.set_value(len(self._segments))
        segment.set_show_selected_icon(self._show_selected_icon)
        segment.set_selected_icon(self._selected_icon)
        self._segments.append(segment)
        self._lay.addWidget(segment)
        if self._group is not None:
            self._group.addButton(segment, len(self._segments) - 1)
        segment.toggled.connect(self._on_toggled)
        self._restyle_positions()

    def segments(self) -> list[MdSegmentedButton]:
        return list(self._segments)

    # -- selection ---------------------------------------------------------

    def selected_indices(self) -> list[int]:
        return [i for i, s in enumerate(self._segments) if s.isChecked()]

    def selected_values(self) -> list[Any]:
        return [s.value() for s in self._segments if s.isChecked()]

    def set_selected_indices(self, indices) -> None:
        """Programmatically set the selection (does not emit ``changed``)."""
        wanted = set(indices)
        if not self._multi and len(wanted) > 1:
            raise ValueError("single-select set cannot select multiple segments")
        if not wanted and not self._empty_allowed and self._segments:
            raise ValueError("emptying the selection is not allowed")
        # Block every segment for the whole loop: with an exclusive QButtonGroup,
        # checking one segment auto-unchecks a sibling, which would otherwise emit
        # ``toggled`` (and break the documented no-emit contract) if only the
        # currently-iterated segment were blocked.
        for seg in self._segments:
            seg.blockSignals(True)
        try:
            for i, seg in enumerate(self._segments):
                seg.setChecked(i in wanted)
        finally:
            for seg in self._segments:
                seg.blockSignals(False)
        for seg in self._segments:
            seg.update()

    def _on_toggled(self, checked: bool) -> None:
        sender = self.sender()
        if self._group is not None:
            # The exclusive QButtonGroup manages mutual exclusion and the
            # non-empty invariant natively. A single user switch fires two
            # ``toggled`` signals (old segment off, new segment on); emit only on
            # the selection (``checked``) so the set reports one change per click.
            if checked:
                self.changed.emit(self.selected_indices())
                self.selectionChanged.emit(self.selected_values())
            return
        if not self._multi and checked:
            # Manual single-select: uncheck the others.
            for seg in self._segments:
                if seg is not sender and seg.isChecked():
                    seg.blockSignals(True)
                    seg.setChecked(False)
                    seg.blockSignals(False)
                    seg.update()
        if (
            not checked
            and not self._empty_allowed
            and not self.selected_indices()
            and sender is not None
        ):
            # Re-assert the last selection: empty is not allowed.
            sender.blockSignals(True)
            sender.setChecked(True)
            sender.blockSignals(False)
            sender.update()
            return
        self.changed.emit(self.selected_indices())
        self.selectionChanged.emit(self.selected_values())

    # -- showSelectedIcon / selectedIcon ----------------------------------

    def show_selected_icon(self) -> bool:
        return self._show_selected_icon

    def set_show_selected_icon(self, show: bool) -> None:
        self._show_selected_icon = show
        for seg in self._segments:
            seg.set_show_selected_icon(show)

    def selected_icon(self) -> str:
        return self._selected_icon

    def set_selected_icon(self, name: str) -> None:
        self._selected_icon = name or _DEFAULT_SELECTED_ICON
        for seg in self._segments:
            seg.set_selected_icon(self._selected_icon)

    def multi_selection_enabled(self) -> bool:
        return self._multi

    def empty_selection_allowed(self) -> bool:
        return self._empty_allowed

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
