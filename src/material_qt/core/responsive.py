"""Window size classes and responsive helpers per the Material breakpoints."""

from __future__ import annotations

from enum import Enum, auto

from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtWidgets import QWidget


class WindowSizeClass(Enum):
    """Material 3 window size classes, by width in logical px."""

    COMPACT = auto()       # < 600
    MEDIUM = auto()        # 600 - 839
    EXPANDED = auto()      # 840 - 1199
    LARGE = auto()         # 1200 - 1599
    EXTRA_LARGE = auto()   # >= 1600


def size_class_for(width: float) -> WindowSizeClass:
    """Return the :class:`WindowSizeClass` for a width in logical px."""
    if width < 600:
        return WindowSizeClass.COMPACT
    if width < 840:
        return WindowSizeClass.MEDIUM
    if width < 1200:
        return WindowSizeClass.EXPANDED
    if width < 1600:
        return WindowSizeClass.LARGE
    return WindowSizeClass.EXTRA_LARGE


def clamp_dialog_width(available: float) -> float:
    """Material dialog width: ``min(560, available - 48)`` in logical px."""
    return min(560.0, available - 48.0)


class ResponsiveHelper(QObject):
    """Watches a widget's resize events and emits :attr:`sizeClassChanged`.

    Emits with the new :class:`WindowSizeClass` only when the class actually
    changes (not on every resize).
    """

    sizeClassChanged = Signal(WindowSizeClass)

    def __init__(self, widget: QWidget) -> None:
        super().__init__(widget)
        self._widget = widget
        self._size_class = size_class_for(widget.width())
        widget.installEventFilter(self)

    @property
    def size_class(self) -> WindowSizeClass:
        return self._size_class

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._widget and event.type() == QEvent.Type.Resize:
            new_class = size_class_for(self._widget.width())
            if new_class is not self._size_class:
                self._size_class = new_class
                self.sizeClassChanged.emit(new_class)
        return False


__all__ = [
    "ResponsiveHelper",
    "WindowSizeClass",
    "clamp_dialog_width",
    "size_class_for",
]
