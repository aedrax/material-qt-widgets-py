"""Elevation levels and shadow specs (pure Python, no Qt)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from ._generated.elevation import (
    AMBIENT_SHADOW_OPACITY,
    AMBIENT_SHADOWS,
    KEY_SHADOW_OPACITY,
    KEY_SHADOWS,
    LEVEL_DP,
)


class ElevationLevel(IntEnum):
    """Material 3 elevation levels (0..5)."""

    LEVEL0 = 0
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3
    LEVEL4 = 4
    LEVEL5 = 5

    @property
    def dp(self) -> int:
        return LEVEL_DP[int(self)]


@dataclass(frozen=True)
class ShadowSpec:
    """A single drop shadow: offset (dx, dy), blur radius, spread, opacity (all px / 0..1)."""

    dx: float
    dy: float
    blur: float
    spread: float
    opacity: float


def key_shadow(level: ElevationLevel | int) -> ShadowSpec:
    """Return the key (umbra) shadow spec for an elevation level."""
    dx, dy, blur, spread = KEY_SHADOWS[int(level)]
    return ShadowSpec(dx, dy, blur, spread, KEY_SHADOW_OPACITY)


def ambient_shadow(level: ElevationLevel | int) -> ShadowSpec:
    """Return the ambient (penumbra) shadow spec for an elevation level."""
    dx, dy, blur, spread = AMBIENT_SHADOWS[int(level)]
    return ShadowSpec(dx, dy, blur, spread, AMBIENT_SHADOW_OPACITY)


__all__ = [
    "AMBIENT_SHADOWS",
    "AMBIENT_SHADOW_OPACITY",
    "KEY_SHADOWS",
    "KEY_SHADOW_OPACITY",
    "LEVEL_DP",
    "ElevationLevel",
    "ShadowSpec",
    "ambient_shadow",
    "key_shadow",
]
