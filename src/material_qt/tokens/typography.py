"""Typescale roles and specs (pure Python, no Qt)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ._generated.typescale import TYPESCALE

REM_PX = 16.0
"""Pixels per CSS rem, matching the web default root font size."""


class TypescaleRole(StrEnum):
    """Material 3 typescale roles (display/headline/title/body/label x L/M/S)."""

    DISPLAY_LARGE = "display-large"
    DISPLAY_MEDIUM = "display-medium"
    DISPLAY_SMALL = "display-small"
    HEADLINE_LARGE = "headline-large"
    HEADLINE_MEDIUM = "headline-medium"
    HEADLINE_SMALL = "headline-small"
    TITLE_LARGE = "title-large"
    TITLE_MEDIUM = "title-medium"
    TITLE_SMALL = "title-small"
    BODY_LARGE = "body-large"
    BODY_MEDIUM = "body-medium"
    BODY_SMALL = "body-small"
    LABEL_LARGE = "label-large"
    LABEL_MEDIUM = "label-medium"
    LABEL_SMALL = "label-small"


@dataclass(frozen=True)
class TypescaleSpec:
    """A resolved typescale specification.

    Sizes are stored in rem (CSS) with px convenience accessors at 16px/rem.
    """

    role: str
    family: str
    size_rem: float
    line_height_rem: float
    weight: int
    tracking_rem: float

    @property
    def size_px(self) -> float:
        return self.size_rem * REM_PX

    @property
    def line_height_px(self) -> float:
        return self.line_height_rem * REM_PX

    @property
    def tracking_px(self) -> float:
        return self.tracking_rem * REM_PX


def spec_for(role: TypescaleRole | str) -> TypescaleSpec:
    """Return the :class:`TypescaleSpec` for a typescale role."""
    data = TYPESCALE[str(role)]
    return TypescaleSpec(role=str(role), **data)


__all__ = ["REM_PX", "TYPESCALE", "TypescaleRole", "TypescaleSpec", "spec_for"]
