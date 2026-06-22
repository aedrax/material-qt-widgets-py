"""Material 3 snackbar for QtWidgets.

A brief message at the bottom of the screen on an ``inverse-surface`` container
(``body-medium`` ``inverse-on-surface`` text, 4px corners, level-3 elevation),
with an optional single ``inverse-primary`` text action. It slides up from the
bottom edge of its host, auto-dismisses after ``duration`` (default 4000ms, per
Flutter's ``_snackBarDisplayDuration``), and can be dismissed early via its
action. ``action`` fires on the action click; ``dismissed`` fires when it closes.
Snackbars are transient and one-shot — connect ``dismissed`` to ``deleteLater``
to avoid accumulating hidden instances if you create one per message.

No :class:`QGraphicsOpacityEffect` is used — the panel carries an elevation drop
shadow, and nesting effects makes Qt spam "painter not active" (see
``dialog.py``). The transition is a pure slide, which needs no opacity effect.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, QVariantAnimation, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ..icon.icon import MdIcon

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.motion import Duration, Easing
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager

_MARGIN = 16
_MIN_W = 344
_MAX_W = 600
_MIN_H = 48
_PAD_TEXT = 16
_PAD_ACTION = 8
_DEFAULT_DURATION = 4000


class MdSnackbar(MaterialWidgetMixin, QWidget):
    """A transient snackbar pinned to the bottom of its host."""

    action = Signal()
    dismissed = Signal()

    def __init__(
        self,
        parent: QWidget,
        text: str = "",
        *,
        action_label: str = "",
        duration: int = _DEFAULT_DURATION,
        behavior: str = "floating",
        show_close_icon: bool = False,
    ) -> None:
        super().__init__(parent)
        self._duration = duration
        self._shown = 0.0  # 0 = below the edge, 1 = resting position
        # Flutter's SnackBarBehavior: "floating" (inset, rounded) or "fixed"
        # (flush full-width against the bottom edge).
        self._behavior = behavior if behavior in ("floating", "fixed") else "floating"

        self._init_material(
            shape=ShapeScale.EXTRA_SMALL,
            elevation=ElevationLevel.LEVEL3,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.INVERSE_SURFACE,
        )

        lay = QHBoxLayout(self)
        trailing = _PAD_ACTION if (action_label or show_close_icon) else _PAD_TEXT
        lay.setContentsMargins(_PAD_TEXT, 0, trailing, 0)
        lay.setSpacing(8)

        self._label = QLabel(text)
        self._label.setFont(font_for_role(TypescaleRole.BODY_MEDIUM))
        lay.addWidget(self._label)
        lay.addStretch(1)

        self._action_label: QLabel | None = None
        if action_label:
            a = QLabel(action_label)
            a.setFont(font_for_role(TypescaleRole.LABEL_LARGE))
            a.setCursor(Qt.CursorShape.PointingHandCursor)
            a.mousePressEvent = self._on_action  # type: ignore[method-assign]
            self._action_label = a
            lay.addWidget(a)

        self._close_icon: MdIcon | None = None
        if show_close_icon:
            ci = MdIcon("close", size=20, color_role=ColorRole.INVERSE_ON_SURFACE)
            ci.setCursor(Qt.CursorShape.PointingHandCursor)
            ci.mousePressEvent = self._on_close_icon  # type: ignore[method-assign]
            self._close_icon = ci
            lay.addWidget(ci)

        self.setMinimumHeight(_MIN_H)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.SHORT4))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_shown)

        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.timeout.connect(self.dismiss)

        parent.installEventFilter(self)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)
        self.hide()

    # -- styling -----------------------------------------------------------

    def _restyle(self) -> None:
        theme = ThemeManager.instance()
        self._label.setStyleSheet(
            f"color: {theme.color(ColorRole.INVERSE_ON_SURFACE).name()};"
        )
        if self._action_label is not None:
            self._action_label.setStyleSheet(
                f"color: {theme.color(ColorRole.INVERSE_PRIMARY).name()};"
            )
        self.update()

    # -- open / dismiss ----------------------------------------------------

    def open(self) -> None:
        self._reposition()
        self.raise_()
        self.show()
        if self._duration > 0:
            self._dismiss_timer.start(self._duration)
        if MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(self._shown)
            self._anim.setEndValue(1.0)
            self._anim.start()
        else:
            self._set_shown(1.0)

    def dismiss(self) -> None:
        if self.isHidden():
            return
        self._dismiss_timer.stop()
        if MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(self._shown)
            self._anim.setEndValue(0.0)
            self._anim.start()  # _set_shown hides + emits when it reaches 0
        else:
            self._shown = 0.0
            self.hide()
            self.dismissed.emit()

    def _on_action(self, event) -> None:
        self.action.emit()
        self.dismiss()

    def _on_close_icon(self, event) -> None:
        # The close icon dismisses without emitting `action`.
        self.dismiss()

    @property
    def behavior(self) -> str:
        return self._behavior

    # -- geometry ----------------------------------------------------------

    def _set_shown(self, value) -> None:
        self._shown = float(value)
        self._reposition()
        # Collapsed to the bottom edge while dismissing: hide once, emit once.
        if self._shown <= 0.01 and self._anim.endValue() == 0.0 and not self.isHidden():
            self.hide()
            self.dismissed.emit()

    def _reposition(self) -> None:
        host = self.parentWidget()
        if host is None:
            return
        avail = host.width()
        h = max(_MIN_H, self.sizeHint().height())
        if self._behavior == "fixed":
            # Flush full-width, no bottom margin (pinned to the edge).
            w = avail
            x = 0
            margin = 0
        else:
            w = max(_MIN_W, min(_MAX_W, avail - 2 * _MARGIN))
            x = int((avail - w) / 2)
            margin = _MARGIN
        resting_y = host.height() - h - margin
        offscreen_y = host.height()
        y = int(offscreen_y + (resting_y - offscreen_y) * self._shown)
        self.setGeometry(x, y, int(w), int(h))

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible():
                self._reposition()
        return False

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdSnackbar"]
