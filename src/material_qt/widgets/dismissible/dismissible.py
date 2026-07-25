"""Material swipe-to-dismiss wrapper for QtWidgets.

Ports Flutter's ``Dismissible`` (``widgets/dismissible.dart``) — wrap a content
widget and let the user swipe it away. A drag past a threshold flings the
content off-screen, collapses the perpendicular extent to zero (reflowing the
host layout), then emits :attr:`MdDismissible.dismissed` with the resolved
:class:`DismissDirection`. A drag that stops short springs back.

Like the reorderable list, this widget **owns its lifecycle**: ``dismissed`` is
a pure notification (fired exactly once) and the consumer removes the item from
its model at leisure — there is no Flutter "a dismissed Dismissible is still in
the tree / you must remove it" footgun, and no required ``key``.

The drop decision is the pure, unit-testable :func:`resolve_dismiss`. The drag
itself is a best-effort event-filter layer over the content subtree.

Deferred (vs Flutter): async ``confirmDismiss`` (here ``confirm`` is a sync
``bool`` callback — a modal ``dialog.exec()`` composes naturally), per-direction
thresholds (single ``threshold`` here), and ``crossAxisEndOffset``. Limitation:
children added *after* construction aren't covered by the drag filter.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from PySide6.QtCore import QEvent, QPoint, QPointF, QSize, Property, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import isValid

from ...core.motion import MOTION_ENABLED, animate
from ...tokens.motion import Duration, Easing

_CLAIM_PX = 8  # axis movement before a press is claimed as a swipe


class DismissDirection(Enum):
    """Allowed swipe directions (mirrors Flutter's ``DismissDirection``)."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    START_TO_END = "startToEnd"  # drag right (LTR)
    END_TO_START = "endToStart"  # drag left (LTR)
    UP = "up"
    DOWN = "down"


_HORIZONTAL = {
    DismissDirection.HORIZONTAL,
    DismissDirection.START_TO_END,
    DismissDirection.END_TO_START,
}


class _State(Enum):
    IDLE = 0
    DRAGGING = 1
    FLINGING = 2
    COLLAPSING = 3
    DISMISSED = 4


def resolve_dismiss(
    direction: DismissDirection,
    dx: float,
    dy: float,
    extent_x: float,
    extent_y: float,
    threshold: float,
) -> DismissDirection | None:
    """Resolve a release into the concrete direction to dismiss, or ``None``.

    ``dx``/``dy`` are the signed drag offset; ``extent_x``/``extent_y`` the
    widget extents. Returns ``START_TO_END``/``END_TO_START``/``UP``/``DOWN``
    when the drag along the allowed axis reaches ``threshold`` (a fraction of
    the extent) in an allowed sign, else ``None`` (spring back). Zero extent
    yields ``None`` (no divide-by-zero).
    """
    if direction in _HORIZONTAL:
        frac = dx / extent_x if extent_x else 0.0
        if frac >= threshold and direction in (
            DismissDirection.HORIZONTAL,
            DismissDirection.START_TO_END,
        ):
            return DismissDirection.START_TO_END
        if frac <= -threshold and direction in (
            DismissDirection.HORIZONTAL,
            DismissDirection.END_TO_START,
        ):
            return DismissDirection.END_TO_START
        return None
    frac = dy / extent_y if extent_y else 0.0
    if frac <= -threshold and direction in (
        DismissDirection.VERTICAL,
        DismissDirection.UP,
    ):
        return DismissDirection.UP
    if frac >= threshold and direction in (
        DismissDirection.VERTICAL,
        DismissDirection.DOWN,
    ):
        return DismissDirection.DOWN
    return None


class MdDismissible(QWidget):
    """Wrap ``content`` so the user can swipe it away."""

    dismissed = Signal(object)  # carries the resolved DismissDirection

    def __init__(
        self,
        content: QWidget,
        parent: QWidget | None = None,
        *,
        direction: DismissDirection = DismissDirection.HORIZONTAL,
        background: QWidget | None = None,
        secondary_background: QWidget | None = None,
        threshold: float = 0.4,
        confirm: Callable[[DismissDirection], bool] | None = None,
    ) -> None:
        super().__init__(parent)
        self._direction = direction
        self._threshold = float(threshold)
        self._confirm = confirm
        self._state = _State.IDLE
        self._offset = 0.0
        self._collapse = 1.0
        self._full_cross: int | None = None
        self._pending_dir: DismissDirection | None = None
        # drag bookkeeping
        self._press_global = QPoint()
        self._press_offset = 0.0
        self._press_receiver: QWidget | None = None
        self._claimed = False
        self._cancelling_child = False
        self._settle_anim = None

        # backgrounds sit behind; content rides on top.
        self._background = background
        self._secondary = secondary_background
        for bg in (background, secondary_background):
            if bg is not None:
                bg.setParent(self)
                bg.hide()
        self._content = content
        content.setParent(self)
        content.show()
        content.raise_()

        self._install_filters(content)

    # -- public API --------------------------------------------------------

    @property
    def content(self) -> QWidget:
        return self._content

    @property
    def direction(self) -> DismissDirection:
        return self._direction

    def dismiss(self, direction: DismissDirection | None = None) -> None:
        """Programmatically dismiss, animating then emitting :attr:`dismissed`."""
        if self._state in (_State.FLINGING, _State.COLLAPSING, _State.DISMISSED):
            return
        self._fling(direction or self._default_direction())

    def _default_direction(self) -> DismissDirection:
        if self._direction == DismissDirection.HORIZONTAL:
            return DismissDirection.END_TO_START
        if self._direction == DismissDirection.VERTICAL:
            return DismissDirection.UP
        return self._direction

    # -- geometry ----------------------------------------------------------

    def _is_horizontal(self) -> bool:
        return self._direction in _HORIZONTAL

    def _content_size(self) -> tuple[int, int]:
        hint = self._content.sizeHint()
        return max(1, hint.width()), max(1, hint.height())

    def sizeHint(self) -> QSize:  # noqa: N802
        cw, ch = self._content_size()
        if self._is_horizontal():
            return QSize(cw, max(0, round(ch * self._collapse)))
        return QSize(max(0, round(cw * self._collapse)), ch)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    def _relayout(self) -> None:
        # The swipe-axis extent stays full during collapse; the cross extent is
        # what shrinks, so children keep full size and get clipped by the parent.
        off = int(self._offset)
        if self._is_horizontal():
            full_w = self.width()
            full_h = self._full_cross if self._full_cross is not None else self.height()
            content_rect = (off, 0, full_w, full_h)
        else:
            full_w = self._full_cross if self._full_cross is not None else self.width()
            full_h = self.height()
            content_rect = (0, off, full_w, full_h)
        for bg in (self._background, self._secondary):
            if bg is not None:
                bg.setGeometry(0, 0, full_w, full_h)
        self._content.setGeometry(*content_rect)
        self._content.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._relayout()

    def _update_backgrounds(self) -> None:
        if self._background is not None:
            self._background.setVisible(self._offset > 0)
        if self._secondary is not None:
            self._secondary.setVisible(self._offset < 0)

    # -- animatable properties ---------------------------------------------

    def get_offset(self) -> float:
        return self._offset

    def set_offset(self, value: float) -> None:
        self._offset = float(value)
        self._update_backgrounds()
        self._relayout()

    offset = Property(float, get_offset, set_offset)

    def get_collapse(self) -> float:
        return self._collapse

    def set_collapse(self, value: float) -> None:
        self._collapse = max(0.0, min(1.0, float(value)))
        self.updateGeometry()  # reflow the host layout
        self._relayout()

    collapse = Property(float, get_collapse, set_collapse)

    # -- dismiss lifecycle -------------------------------------------------

    def _clamp_offset(self, raw: float) -> float:
        d = self._direction
        if d in (DismissDirection.START_TO_END, DismissDirection.DOWN):
            return max(0.0, raw)
        if d in (DismissDirection.END_TO_START, DismissDirection.UP):
            return min(0.0, raw)
        return raw

    def _release(self) -> None:
        result = resolve_dismiss(
            self._direction,
            self._offset if self._is_horizontal() else 0.0,
            self._offset if not self._is_horizontal() else 0.0,
            self.width(),
            self.height(),
            self._threshold,
        )
        if result is None:
            self._spring_back()
            return
        if self._confirm is not None and not self._confirm(result):
            self._spring_back()
            return
        self._fling(result)

    def _spring_back(self) -> None:
        self._state = _State.IDLE
        if not MOTION_ENABLED:
            self.set_offset(0.0)
            return
        self._settle_anim = animate(
            self, b"offset", 0.0, duration=Duration.SHORT3, easing=Easing.STANDARD
        )

    def _stop_settle(self) -> None:
        # A running spring-back would keep writing `offset` under a new drag,
        # yanking the row out of the user's hand.
        anim = self._settle_anim
        self._settle_anim = None
        if anim is not None and isValid(anim):
            anim.stop()  # DeleteWhenStopped: the C++ object dies here

    def _fling(self, direction: DismissDirection) -> None:
        if self._state in (_State.FLINGING, _State.COLLAPSING, _State.DISMISSED):
            return
        self._state = _State.FLINGING
        self._pending_dir = direction
        self._full_cross = self.height() if self._is_horizontal() else self.width()
        extent = self.width() if self._is_horizontal() else self.height()
        sign = 1.0 if direction in (
            DismissDirection.START_TO_END,
            DismissDirection.DOWN,
        ) else -1.0
        end = sign * extent
        if not MOTION_ENABLED:
            self.set_offset(end)
            self._collapse_then_emit()
            return
        animate(
            self,
            b"offset",
            end,
            duration=Duration.SHORT3,
            easing=Easing.EMPHASIZED_ACCELERATE,
            on_finished=self._collapse_then_emit,
        )

    def _collapse_then_emit(self) -> None:
        if self._state in (_State.COLLAPSING, _State.DISMISSED):
            return
        self._state = _State.COLLAPSING
        if not MOTION_ENABLED:
            self.set_collapse(0.0)
            self._emit_dismissed()
            return
        animate(
            self,
            b"collapse",
            0.0,
            duration=Duration.MEDIUM2,
            easing=Easing.EMPHASIZED,
            on_finished=self._emit_dismissed,
        )

    def _emit_dismissed(self) -> None:
        if self._state == _State.DISMISSED:
            return
        self._state = _State.DISMISSED
        self.hide()
        self.dismissed.emit(self._pending_dir)

    # -- drag (event-filter layer over the content subtree) ----------------

    def _install_filters(self, root: QWidget) -> None:
        root.installEventFilter(self)
        for child in root.findChildren(QWidget):
            child.installEventFilter(self)

    def _cancel_child_press(self, move_event) -> None:
        """Un-press the child that accepted the press once the swipe claims it.

        The filter swallows the eventual release, so without this a button (or
        state-layer) under the finger stays stuck down (Flutter cancels the
        child gesture at the same point). A synthetic release far outside the
        child releases it without clicking it.
        """
        target = self._press_receiver
        self._press_receiver = None
        if target is None or not isValid(target):
            return
        far = QPointF(-10000.0, -10000.0)
        release = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            far,
            far,
            move_event.globalPosition(),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        self._cancelling_child = True
        try:
            QApplication.sendEvent(target, release)
        finally:
            self._cancelling_child = False

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        et = event.type()
        if et == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton and self._state in (
                _State.IDLE,
                _State.DRAGGING,
            ):
                self._stop_settle()
                self._press_global = event.globalPosition().toPoint()
                self._press_offset = self._offset
                self._press_receiver = obj if isinstance(obj, QWidget) else None
                self._claimed = False
            return False
        if et == QEvent.Type.MouseMove:
            if self._press_global.isNull() or self._state not in (
                _State.IDLE,
                _State.DRAGGING,
            ):
                return False
            delta = event.globalPosition().toPoint() - self._press_global
            along = delta.x() if self._is_horizontal() else delta.y()
            if not self._claimed:
                if abs(along) < _CLAIM_PX:
                    return False
                self._claimed = True
                self._state = _State.DRAGGING
                self._cancel_child_press(event)
            self.set_offset(self._clamp_offset(self._press_offset + float(along)))
            return True
        if et == QEvent.Type.MouseButtonRelease:
            if self._cancelling_child:
                return False
            if not self._claimed:
                self._press_global = QPoint()
                self._press_receiver = None
                return False
            self._claimed = False
            self._press_global = QPoint()
            self._press_receiver = None
            self._release()
            return True
        return False


__all__ = ["MdDismissible", "DismissDirection", "resolve_dismiss"]
