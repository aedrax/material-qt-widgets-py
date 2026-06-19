"""Material 3 button group (Expressive) for QtWidgets.

Ports the Material 3 Expressive button group: a row of related toggle buttons
that share a pill shape but are visually separated by small gaps (unlike the
connected :class:`MdSegmentedButtonSet`). Selected buttons fill
``secondary-container``; unselected use ``surface-container-low``. Supports
single-select (exclusive) or multi-select. ``changed`` fires when the selection
changes, with the list of selected indices.

Deferred (scaffold): the press-morph animation (the pressed button widening as
neighbors shrink).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QAbstractButton, QButtonGroup, QHBoxLayout, QSizePolicy, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_HEIGHT = 48
_GAP = 8
_ICON = 18
_PAD = 16


class _GroupButton(MaterialWidgetMixin, QAbstractButton):
    """A single pill toggle button within a button group."""

    def __init__(self, label: str = "", *, icon: str = "",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText(label)
        self._icon = icon
        self.setCheckable(True)
        self._init_material(
            shape=CornerRadii.uniform(_HEIGHT / 2.0),
            typescale=TypescaleRole.LABEL_LARGE,
            ripple=True,
            focus_ring=True,
            ripple_role=ColorRole.ON_SURFACE_VARIANT,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.toggled.connect(lambda *_: self.update())

    def sizeHint(self) -> QSize:  # noqa: N802
        from PySide6.QtGui import QFontMetrics
        w = QFontMetrics(self.font()).horizontalAdvance(self.text()) + 2 * _PAD
        if self._icon:
            w += _ICON + 8
        return QSize(max(w, _HEIGHT), _HEIGHT)

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
        selected = self.isChecked()
        path = rounded_path(QRectF(self.rect()), self._radii)
        bg = theme.color(
            ColorRole.SECONDARY_CONTAINER if selected else ColorRole.SURFACE_CONTAINER_LOW
        )
        painter.fillPath(path, bg)
        fg = theme.color(
            ColorRole.ON_SECONDARY_CONTAINER if selected else ColorRole.ON_SURFACE_VARIANT
        )
        x = _PAD
        if self._icon:
            font = material_symbols_font(_ICON, filled=selected)
            if font is not None:
                painter.setFont(font)
                painter.setPen(fg)
                painter.drawText(QRectF(x, 0, _ICON, self.height()),
                                 Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                                 self._icon)
            x += _ICON + 8
        painter.setFont(self.font())
        painter.setPen(fg)
        painter.drawText(QRectF(x, 0, self.width() - x - _PAD, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self.text())


class MdButtonGroup(MaterialWidgetMixin, QWidget):
    """A row of separated pill toggle buttons."""

    changed = Signal(list)

    def __init__(self, parent: QWidget | None = None, *, multi: bool = True) -> None:
        super().__init__(parent)
        self._multi = multi
        self._buttons: list[_GroupButton] = []
        self._group = None if multi else QButtonGroup(self)
        if self._group is not None:
            self._group.setExclusive(True)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(_GAP)
        self._lay.addStretch(1)
        self._init_material(shape=None, ripple=False, focus_ring=False,
                            surface_role=ColorRole.SURFACE)

    def add_button(self, label: str = "", *, icon: str = "") -> _GroupButton:
        btn = _GroupButton(label, icon=icon)
        if self._group is not None:
            self._group.addButton(btn, len(self._buttons))
        self._lay.insertWidget(self._lay.count() - 1, btn)
        self._buttons.append(btn)
        btn.toggled.connect(lambda *_: self.changed.emit(self.selected_indices()))
        return btn

    def selected_indices(self) -> list[int]:
        return [i for i, b in enumerate(self._buttons) if b.isChecked()]

    def paintEvent(self, event) -> None:  # noqa: N802
        pass  # transparent container


__all__ = ["MdButtonGroup"]
