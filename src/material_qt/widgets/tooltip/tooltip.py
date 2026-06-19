"""Material 3 plain tooltip for QtWidgets.

Ports the Material 3 plain tooltip (cf. Flutter's ``Tooltip`` /
``_TooltipDefaultsM3``): a small ``inverse-surface`` label (``body-small``
``inverse-on-surface`` text, 4px corners, 8x4 padding) shown on hover above a
target widget. It appears after ``wait_ms`` of hovering and hides on leave or
after ``show_ms`` (defaults match Flutter: wait 500ms, show 1500ms).

The tooltip is parented to the target's top-level window rather than being a
separate native popup — the repo deliberately avoids top-level overlay windows
(see the focus-ring overlay). It sits above the target, flipping below when there
is no room.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, Qt, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager

_PAD_H = 8
_PAD_V = 4
_GAP = 8
_DEFAULT_WAIT = 500
_DEFAULT_SHOW = 1500


class MdTooltip(MaterialWidgetMixin, QWidget):
    """A plain tooltip attached to a target widget."""

    def __init__(
        self,
        target: QWidget,
        text: str = "",
        *,
        wait_ms: int = _DEFAULT_WAIT,
        show_ms: int = _DEFAULT_SHOW,
    ) -> None:
        super().__init__(target.window())
        self._target = target
        self._wait_ms = wait_ms
        self._show_ms = show_ms

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._init_material(
            shape=ShapeScale.EXTRA_SMALL,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.INVERSE_SURFACE,
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(_PAD_H, _PAD_V, _PAD_H, _PAD_V)
        self._label = QLabel(text)
        self._label.setFont(font_for_role(TypescaleRole.BODY_SMALL))
        lay.addWidget(self._label)

        self._wait_timer = QTimer(self)
        self._wait_timer.setSingleShot(True)
        self._wait_timer.timeout.connect(self._show_tooltip)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide_tooltip)

        target.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        target.installEventFilter(self)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)
        self.hide()

    @classmethod
    def attach(cls, target: QWidget, text: str, **kwargs) -> MdTooltip:
        """Attach a tooltip to ``target`` and return it."""
        return cls(target, text, **kwargs)

    def set_text(self, text: str) -> None:
        self._label.setText(text)

    def _restyle(self) -> None:
        self._label.setStyleSheet(
            f"color: {ThemeManager.instance().color(ColorRole.INVERSE_ON_SURFACE).name()};"
        )
        self.update()

    # -- show / hide -------------------------------------------------------

    def _show_tooltip(self) -> None:
        if self._target.isHidden():
            return
        self.adjustSize()
        self._position()
        self.raise_()
        self.show()
        if self._show_ms > 0:
            self._hide_timer.start(self._show_ms)

    def hide_tooltip(self) -> None:
        self._wait_timer.stop()
        self._hide_timer.stop()
        self.hide()

    def _position(self) -> None:
        window = self._target.window()
        size = self.sizeHint()
        # Center horizontally over the target, place above it (flip below if the
        # top would clip).
        top_left = self._target.mapTo(window, QPoint(0, 0))
        cx = top_left.x() + self._target.width() // 2
        x = cx - size.width() // 2
        y = top_left.y() - size.height() - _GAP
        if y < 0:
            y = top_left.y() + self._target.height() + _GAP
        x = max(0, min(x, window.width() - size.width()))
        self.move(x, y)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._target:
            etype = event.type()
            if etype in (QEvent.Type.Enter, QEvent.Type.HoverEnter):
                self._hide_timer.stop()
                self._wait_timer.start(self._wait_ms)
            elif etype in (
                QEvent.Type.Leave,
                QEvent.Type.HoverLeave,
                QEvent.Type.Hide,
                QEvent.Type.MouseButtonPress,
            ):
                self.hide_tooltip()
        return False

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdTooltip"]
