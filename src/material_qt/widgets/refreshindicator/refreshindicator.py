"""Material 3 pull-to-refresh indicator for QtWidgets.

Ports Flutter's :class:`RefreshIndicator`: a container that wraps a scrollable
child and reveals a circular spinner that descends from the top edge when the
user pulls the content down past its top. Releasing past a threshold *triggers*
a refresh; the app then runs its work and calls :meth:`end` / :meth:`finish` to
dismiss the spinner.

Callbacks become Qt Signals: instead of Flutter's ``onRefresh`` future, this
emits the :attr:`refresh` :class:`Signal` when triggered. Because a real touch
drag is awkward to drive headlessly, the gesture is mirrored by programmatic
methods:

* :meth:`begin` — reveal the spinner at its resting ``displacement`` (no signal);
* :meth:`trigger` — reveal the spinner *and* emit ``refresh`` (a release past the
  threshold, or a manual refresh request);
* :meth:`end` / :meth:`finish` — dismiss the spinner.

The spinner is an indeterminate :class:`MdCircularProgress`, so it inherits the
looping (``setLoopCount(-1)``) animation handling. ``displacement`` is the
resting offset of the spinner from the top edge; ``color_role`` themes it.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QVariantAnimation, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED
from ...tokens.color import ColorRole
from ..progress import MdCircularProgress

_DEFAULT_DISPLACEMENT = 40
_SPINNER_SIZE = 36
# Pull distance (px) past which a release triggers a refresh.
_TRIGGER_THRESHOLD = 64
_REVEAL_MS = 200


class MdRefreshIndicator(MaterialWidgetMixin, QWidget):
    """Pull-to-refresh container wrapping a scrollable child.

    Connect to :attr:`refresh` to start your work, then call :meth:`end` (alias
    :meth:`finish`) when it completes.
    """

    #: Emitted when a refresh is triggered (release past threshold or
    #: :meth:`trigger`). Connect this to start the refresh work.
    refresh = Signal()

    def __init__(
        self,
        child: QWidget | None = None,
        parent: QWidget | None = None,
        *,
        displacement: int = _DEFAULT_DISPLACEMENT,
        color_role: ColorRole = ColorRole.PRIMARY,
    ) -> None:
        super().__init__(parent)
        self._init_material(shape=None, ripple=False, focus_ring=False)
        self._displacement = int(displacement)
        self._refreshing = False
        self._drag_origin: QPoint | None = None
        self._anim: QVariantAnimation | None = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._child: QWidget | None = None

        # Spinner overlay: a child of self, hidden offscreen until revealed.
        self._spinner = MdCircularProgress(
            self, indeterminate=True, size=_SPINNER_SIZE, color_role=color_role,
        )
        self._spinner.resize(_SPINNER_SIZE, _SPINNER_SIZE)
        self._spinner.hide()
        self._spinner_y = -_SPINNER_SIZE

        if child is not None:
            self.set_child(child)

    # -- child -------------------------------------------------------------

    def set_child(self, child: QWidget) -> None:
        """Set the scrollable child the indicator wraps."""
        if self._child is not None:
            self._layout.removeWidget(self._child)
            self._child.removeEventFilter(self)
        self._child = child
        self._layout.addWidget(child)
        child.installEventFilter(self)
        self._spinner.raise_()

    @property
    def child(self) -> QWidget | None:
        return self._child

    # -- properties --------------------------------------------------------

    @property
    def displacement(self) -> int:
        """Resting offset of the spinner from the top edge (Flutter ``displacement``)."""
        return self._displacement

    def set_displacement(self, value: int) -> None:
        self._displacement = int(value)
        if not self._spinner.isHidden():
            self._position_spinner(self._displacement)

    @property
    def color_role(self) -> ColorRole:
        """Theme role of the spinner (Flutter ``color``)."""
        return self._spinner.color_role

    def set_color_role(self, role: ColorRole) -> None:
        self._spinner.set_color_role(role)

    @property
    def is_refreshing(self) -> bool:
        """Whether the spinner is currently shown."""
        return self._refreshing

    # -- programmatic control ---------------------------------------------

    def begin(self) -> None:
        """Reveal the spinner at its resting displacement (no ``refresh`` signal)."""
        self._refreshing = True
        self._spinner.show()
        self._spinner.raise_()
        self._animate_to(self._displacement)

    def trigger(self) -> None:
        """Reveal the spinner and emit :attr:`refresh` (a release past threshold)."""
        self.begin()
        self.refresh.emit()

    def end(self) -> None:
        """Dismiss the spinner (call when the refresh work has finished)."""
        if not self._refreshing and self._spinner.isHidden():
            return
        self._refreshing = False
        self._animate_to(-_SPINNER_SIZE, on_done=self._spinner.hide)

    #: Alias for :meth:`end`.
    finish = end

    # -- positioning / animation ------------------------------------------

    def _position_spinner(self, top: float) -> None:
        self._spinner_y = top
        x = (self.width() - self._spinner.width()) // 2
        self._spinner.move(x, int(top))

    def _animate_to(self, target: float, on_done=None) -> None:
        self._stop_anim()
        if not MOTION_ENABLED:
            self._position_spinner(target)
            if on_done is not None:
                on_done()
            return
        anim = QVariantAnimation(self)
        anim.setStartValue(float(self._spinner_y))
        anim.setEndValue(float(target))
        anim.setDuration(_REVEAL_MS)
        anim.valueChanged.connect(self._position_spinner)
        if on_done is not None:
            anim.finished.connect(on_done)
        anim.finished.connect(self._stop_anim)
        anim.start()
        self._anim = anim

    def _stop_anim(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim.deleteLater()
            self._anim = None

    # -- pull gesture (best-effort) ---------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._child and not self._refreshing:
            etype = event.type()
            if etype == QEvent.Type.MouseButtonPress:
                self._drag_origin = event.position().toPoint()
            elif etype == QEvent.Type.MouseMove and self._drag_origin is not None:
                dy = event.position().toPoint().y() - self._drag_origin.y()
                if dy > 0:
                    self._spinner.show()
                    self._spinner.raise_()
                    # Track the finger from offscreen toward the resting
                    # displacement so release settles without a jump.
                    top = -_SPINNER_SIZE + min(dy, self._displacement + _SPINNER_SIZE)
                    self._position_spinner(min(top, self._displacement))
            elif etype == QEvent.Type.MouseButtonRelease and self._drag_origin is not None:
                dy = event.position().toPoint().y() - self._drag_origin.y()
                self._drag_origin = None
                if dy >= _TRIGGER_THRESHOLD:
                    self.trigger()
                else:
                    self._spinner.hide()
                    self._position_spinner(-_SPINNER_SIZE)
        return False

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_spinner(self._spinner_y)

    def hideEvent(self, event) -> None:  # noqa: N802
        self._stop_anim()
        super().hideEvent(event)


__all__ = ["MdRefreshIndicator"]
