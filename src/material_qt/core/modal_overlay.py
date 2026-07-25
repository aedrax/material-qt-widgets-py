"""Shared base for centered, scrim-backed modal overlays.

:class:`ModalOverlay` factors out the scaffolding common to the dialog and the
date / time pickers: a full-parent scrim that fades in/out, a centered panel
that slides up slightly as it fades, dismissal on a scrim click or Escape, and
focus handling on close. Subclasses build ``self._panel`` (the centered content
widget), call :meth:`_init_overlay`, define their own result signal (e.g.
``accepted(QDate)``) and OK/Cancel handlers, and otherwise inherit everything.

The panel width is the one real variation: pickers use a fixed-width panel,
while the dialog clamps to an available-width range — so :meth:`_panel_width`
is the override seam.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import isValid

from ..tokens.color import ColorRole
from ..tokens.motion import Duration, Easing
from ..theme.theme_manager import ThemeManager
from .focus_util import drop_focus_within
from .motion import MOTION_ENABLED, duration_ms, easing_curve

SCRIM_OPACITY = 0.32
_SLIDE = 12  # px the panel rises as it fades in (M3 subtle enter motion)


class ModalOverlay(QWidget):
    """A centered modal overlay with a fading scrim.

    Subclass contract:
      * build ``self._panel`` before calling :meth:`_init_overlay`;
      * declare an ``accepted`` signal with whatever payload fits;
      * emit ``accepted`` then call :meth:`_close` on confirm, and
        :meth:`dismiss` (which emits :attr:`rejected`) on cancel.
    """

    rejected = Signal()
    closed = Signal()

    _panel: QWidget  # the centered content widget, built by the subclass

    def _init_overlay(self, parent: QWidget) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._fade = 0.0
        self._prev_focus: QWidget | None = None  # focus owner before open()
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_fade)
        parent.installEventFilter(self)
        ThemeManager.instance().themeChanged.connect(self.update)
        self.hide()

    # -- open / close ------------------------------------------------------

    def open(self) -> None:
        if self.isHidden():
            # Remember the focus owner so _close() can hand focus back. Only on
            # a hidden->shown transition: a re-open while visible would record
            # a widget inside the overlay itself.
            self._prev_focus = QApplication.focusWidget()
        self.setGeometry(self.parentWidget().rect())
        self._center_panel()
        self.raise_()
        self.show()
        self.setFocus()
        if MOTION_ENABLED:
            # Resume from the current fade (not 0.0) so re-opening mid-fade
            # doesn't blink the scrim back to transparent.
            self._anim.stop()
            self._anim.setStartValue(self._fade)
            self._anim.setEndValue(1.0)
            self._anim.start()
        else:
            self._set_fade(1.0)

    def _close(self) -> None:
        # Stop the fade so a dismissed-during-fade-in overlay doesn't keep
        # ticking _set_fade (adjustSize + update per frame) while hidden.
        self._anim.stop()
        # Drop focus before hiding so Qt doesn't reassign it to a sibling with
        # TabFocusReason, which would show a spurious keyboard focus ring.
        drop_focus_within(self)
        self.hide()
        self._fade = 0.0  # the next open() fades in from scratch
        prev = self._prev_focus
        self._prev_focus = None
        if (
            prev is not None
            and isValid(prev)
            and prev.isVisible()
            and not self.isAncestorOf(prev)
        ):
            prev.setFocus(Qt.FocusReason.OtherFocusReason)
        self.closed.emit()

    def dismiss(self) -> None:
        """Reject and close (scrim click, Escape, or a Cancel action)."""
        self.rejected.emit()
        self._close()

    def _set_fade(self, value) -> None:
        self._fade = float(value)
        self._center_panel()
        self.update()

    # -- keyboard focus trap -------------------------------------------------

    def _tab_targets(self) -> list[QWidget]:
        """Tab-focusable descendants of the overlay, in focus-chain order."""
        targets: list[QWidget] = []
        w = self.nextInFocusChain()
        while w is not None and w is not self:
            if (
                self.isAncestorOf(w)
                and w.isVisibleTo(self)
                and w.isEnabled()
                and w.focusPolicy() & Qt.FocusPolicy.TabFocus
            ):
                targets.append(w)
            w = w.nextInFocusChain()
        return targets

    def focusNextPrevChild(self, forward: bool) -> bool:  # noqa: N802
        # While the overlay is shown it is modal: the mouse is blocked by the
        # scrim, so Tab must not walk into widgets behind it either. Confine
        # Tab / Backtab to the overlay's own focusable descendants, wrapping.
        if self.isHidden():
            return super().focusNextPrevChild(forward)
        targets = self._tab_targets()
        if not targets:
            return True  # swallow: never let focus escape the modal
        current = QApplication.focusWidget()
        try:
            index = targets.index(current)
        except ValueError:
            index = -1 if forward else 0
        index = (index + (1 if forward else -1)) % len(targets)
        reason = (
            Qt.FocusReason.TabFocusReason
            if forward
            else Qt.FocusReason.BacktabFocusReason
        )
        targets[index].setFocus(reason)
        return True

    # -- geometry / scrim --------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible():
                self.setGeometry(self.parentWidget().rect())
                self._center_panel()
        return False

    def _panel_width(self) -> int:
        """Width for the centered panel; override to clamp to available space."""
        return self._panel.width()

    def _center_panel(self) -> None:
        self._panel.adjustSize()
        w = self._panel_width()
        h = self._panel.sizeHint().height()
        slide = int((1.0 - self._fade) * _SLIDE)
        self._panel.setGeometry(
            int((self.width() - w) / 2),
            int((self.height() - h) / 2) + slide, int(w), int(h),
        )

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._center_panel()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        # A click on the scrim (outside the panel) dismisses.
        if not self._panel.geometry().contains(event.position().toPoint()):
            self.dismiss()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        scrim = QColor(ThemeManager.instance().color(ColorRole.SCRIM))
        scrim.setAlphaF(SCRIM_OPACITY * self._fade)
        painter.fillRect(self.rect(), scrim)


__all__ = ["SCRIM_OPACITY", "ModalOverlay"]
