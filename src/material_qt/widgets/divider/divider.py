"""MdDivider: a thin separator line matching Material's md-divider.

The web component renders a 1px line in the ``outline-variant`` color, full
width by default, with optional 16px insets on the leading/trailing edges
(``inset``, ``inset-start``, ``inset-end``). It primarily lays out
horizontally; this port also supports a vertical orientation where the line
runs top-to-bottom and insets apply to the top/bottom edges.

Source of truth: ``divider/internal/_divider.scss`` and the divider tokens
(``--md-divider-thickness: 1px``, ``--md-divider-color:
--md-sys-color-outline-variant``, inset padding ``16px``).
"""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...tokens.color import ColorRole
from ...theme.theme_manager import ThemeManager

# Matches the web tokens: --md-divider-thickness: 1px; inset padding: 16px.
THICKNESS_PX = 1
INSET_PX = 16

_QWIDGETSIZE_MAX = 16777215


class MdDivider(QWidget):
    """A thin line that groups content in lists and containers.

    Args:
        parent: Optional parent widget.
        orientation: ``Qt.Orientation.Horizontal`` (default) draws a
            full-width 1px line; ``Qt.Orientation.Vertical`` draws a
            full-height 1px line.

    The color is resolved from the theme in :meth:`paintEvent` (so theme
    switches repaint correctly) using the ``outline-variant`` role, matching
    the web ``--md-divider-color`` default. The widget is decorative and does
    not handle pointer or focus events.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    ) -> None:
        super().__init__(parent)
        self._orientation = orientation
        self._inset = False
        self._inset_start = False
        self._inset_end = False
        self._color_role = ColorRole.OUTLINE_VARIANT

        # Decorative by default; not focusable, transparent to mouse events.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._apply_size_policy()

        ThemeManager.instance().themeChanged.connect(self.update)

    # -- sizing ------------------------------------------------------------

    def _apply_size_policy(self) -> None:
        if self._orientation == Qt.Orientation.Horizontal:
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            self.setFixedHeight(THICKNESS_PX)
        else:
            self.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
            )
            self.setFixedWidth(THICKNESS_PX)

    def orientation(self) -> Qt.Orientation:
        return self._orientation

    def set_orientation(self, orientation: Qt.Orientation) -> None:
        if orientation == self._orientation:
            return
        # Release the previously fixed dimension before applying new policy.
        self.setMinimumSize(0, 0)
        self.setMaximumSize(_QWIDGETSIZE_MAX, _QWIDGETSIZE_MAX)
        self._orientation = orientation
        self._apply_size_policy()
        self.updateGeometry()
        self.update()

    # -- inset properties --------------------------------------------------

    @property
    def inset(self) -> bool:
        """Indents the divider with equal padding on both sides."""
        return self._inset

    @inset.setter
    def inset(self, value: bool) -> None:
        value = bool(value)
        if value != self._inset:
            self._inset = value
            self.update()

    @property
    def inset_start(self) -> bool:
        """Indents the divider with padding on the leading side."""
        return self._inset_start

    @inset_start.setter
    def inset_start(self, value: bool) -> None:
        value = bool(value)
        if value != self._inset_start:
            self._inset_start = value
            self.update()

    @property
    def inset_end(self) -> bool:
        """Indents the divider with padding on the trailing side."""
        return self._inset_end

    @inset_end.setter
    def inset_end(self, value: bool) -> None:
        value = bool(value)
        if value != self._inset_end:
            self._inset_end = value
            self.update()

    # -- painting ----------------------------------------------------------

    def _line_rect(self) -> QRect:
        """Compute the painted line rect, applying insets.

        Insets shorten the line on the leading/trailing edges. For a
        horizontal divider those are the left/right edges; for vertical, the
        top/bottom edges. ``inset`` implies both. Leading/trailing respect the
        widget's layout direction for the horizontal case.
        """
        rect = self.rect()
        start = self._inset or self._inset_start
        end = self._inset or self._inset_end

        if self._orientation == Qt.Orientation.Horizontal:
            left_inset = start
            right_inset = end
            # Honor RTL: leading == right edge when layout is RTL.
            if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
                left_inset, right_inset = right_inset, left_inset
            x = rect.left() + (INSET_PX if left_inset else 0)
            right = rect.right() - (INSET_PX if right_inset else 0)
            width = max(0, right - x + 1)
            return QRect(x, rect.top(), width, THICKNESS_PX)

        # Vertical: insets apply to the top (leading) and bottom (trailing).
        y = rect.top() + (INSET_PX if start else 0)
        bottom = rect.bottom() - (INSET_PX if end else 0)
        height = max(0, bottom - y + 1)
        return QRect(rect.left(), y, THICKNESS_PX, height)

    def paintEvent(self, event) -> None:  # noqa: N802
        line = self._line_rect()
        if line.isEmpty():
            return
        color: QColor = ThemeManager.instance().color(self._color_role)
        painter = QPainter(self)
        painter.fillRect(line, color)


__all__ = ["MdDivider"]
