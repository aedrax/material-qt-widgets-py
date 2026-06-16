"""Shape scale and corner radii (pure Python, no Qt)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ._generated.shape import CORNER, PER_CORNER

FULL_SENTINEL = CORNER["full"]
"""The sentinel radius (9999) meaning "fully rounded"; resolve per-rect later."""


class ShapeScale(StrEnum):
    """Material 3 shape scale steps."""

    NONE = "none"
    EXTRA_SMALL = "extra-small"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra-large"
    FULL = "full"


@dataclass(frozen=True)
class CornerRadii:
    """Per-corner radii in px, ordered top-left, top-right, bottom-right, bottom-left."""

    tl: float
    tr: float
    br: float
    bl: float

    @classmethod
    def uniform(cls, radius: float) -> CornerRadii:
        return cls(radius, radius, radius, radius)

    @classmethod
    def from_scale(cls, scale: ShapeScale | str) -> CornerRadii:
        """Build uniform radii from a shape scale step."""
        return cls.uniform(CORNER[str(scale)])

    @classmethod
    def from_shorthand(cls, key: str) -> CornerRadii:
        """Build radii from a per-corner shorthand key (e.g. ``large-top``)."""
        tl, tr, br, bl = PER_CORNER[key]
        return cls(tl, tr, br, bl)

    @property
    def is_full(self) -> bool:
        """True if all corners are the "full" sentinel radius."""
        return all(c >= FULL_SENTINEL for c in (self.tl, self.tr, self.br, self.bl))

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.tl, self.tr, self.br, self.bl)


__all__ = [
    "CORNER",
    "FULL_SENTINEL",
    "PER_CORNER",
    "CornerRadii",
    "ShapeScale",
]
