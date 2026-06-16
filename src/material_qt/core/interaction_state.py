"""Tracks interaction flags and resolves the active state layer by precedence."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ..tokens.state import StateLayer


class InteractionState(QObject):
    """Holds enabled/hover/press/focus/drag flags and emits :attr:`changed`.

    The active state layer follows Material precedence:
    pressed > dragged > focus (keyboard) > hover. A disabled state has no
    active layer.
    """

    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._enabled = True
        self._hovered = False
        self._pressed = False
        self._focused = False
        self._dragged = False

    def _set(self, attr: str, value: bool) -> None:
        value = bool(value)
        if getattr(self, attr) == value:
            return
        setattr(self, attr, value)
        self.changed.emit()

    # -- flags -------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set("_enabled", value)

    @property
    def hovered(self) -> bool:
        return self._hovered

    @hovered.setter
    def hovered(self, value: bool) -> None:
        self._set("_hovered", value)

    @property
    def pressed(self) -> bool:
        return self._pressed

    @pressed.setter
    def pressed(self, value: bool) -> None:
        self._set("_pressed", value)

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        self._set("_focused", value)

    @property
    def dragged(self) -> bool:
        return self._dragged

    @dragged.setter
    def dragged(self, value: bool) -> None:
        self._set("_dragged", value)

    # -- resolution --------------------------------------------------------

    def active_layer(self) -> StateLayer | None:
        """Return the highest-precedence active state layer, or None."""
        if not self._enabled:
            return None
        if self._pressed:
            return StateLayer.PRESSED
        if self._dragged:
            return StateLayer.DRAGGED
        if self._focused:
            return StateLayer.FOCUS
        if self._hovered:
            return StateLayer.HOVER
        return None

    def active_opacity(self) -> float:
        """Return the opacity of the active layer, or 0.0 when none is active."""
        layer = self.active_layer()
        return layer.opacity if layer is not None else 0.0


__all__ = ["InteractionState"]
