"""State layer opacities (pure Python, no Qt)."""

from __future__ import annotations

from enum import Enum

from ._generated.state import STATE_OPACITY


class StateLayer(Enum):
    """State-layer overlay opacities for interaction states."""

    HOVER = STATE_OPACITY["hover"]
    FOCUS = STATE_OPACITY["focus"]
    PRESSED = STATE_OPACITY["pressed"]
    DRAGGED = STATE_OPACITY["dragged"]

    @property
    def opacity(self) -> float:
        return float(self.value)


__all__ = ["STATE_OPACITY", "StateLayer"]
