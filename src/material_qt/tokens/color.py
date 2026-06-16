"""Color roles and resolution helpers (pure Python, no Qt).

Resolution chain: ``ColorRole`` -> tone-key (light or dark) -> hex string.
"""

from __future__ import annotations

from enum import StrEnum

from ._generated.color_roles import DARK_ROLES, LIGHT_ROLES
from ._generated.palette import REF_PALETTE


class ColorRole(StrEnum):
    """Material 3 system color roles.

    Values are the canonical kebab-case role names used in the token maps.
    """

    BACKGROUND = "background"
    ERROR = "error"
    ERROR_CONTAINER = "error-container"
    INVERSE_ON_SURFACE = "inverse-on-surface"
    INVERSE_PRIMARY = "inverse-primary"
    INVERSE_SURFACE = "inverse-surface"
    ON_BACKGROUND = "on-background"
    ON_ERROR = "on-error"
    ON_ERROR_CONTAINER = "on-error-container"
    ON_PRIMARY = "on-primary"
    ON_PRIMARY_CONTAINER = "on-primary-container"
    ON_PRIMARY_FIXED = "on-primary-fixed"
    ON_PRIMARY_FIXED_VARIANT = "on-primary-fixed-variant"
    ON_SECONDARY = "on-secondary"
    ON_SECONDARY_CONTAINER = "on-secondary-container"
    ON_SECONDARY_FIXED = "on-secondary-fixed"
    ON_SECONDARY_FIXED_VARIANT = "on-secondary-fixed-variant"
    ON_SURFACE = "on-surface"
    ON_SURFACE_VARIANT = "on-surface-variant"
    ON_TERTIARY = "on-tertiary"
    ON_TERTIARY_CONTAINER = "on-tertiary-container"
    ON_TERTIARY_FIXED = "on-tertiary-fixed"
    ON_TERTIARY_FIXED_VARIANT = "on-tertiary-fixed-variant"
    OUTLINE = "outline"
    OUTLINE_VARIANT = "outline-variant"
    PRIMARY = "primary"
    PRIMARY_CONTAINER = "primary-container"
    PRIMARY_FIXED = "primary-fixed"
    PRIMARY_FIXED_DIM = "primary-fixed-dim"
    SCRIM = "scrim"
    SECONDARY = "secondary"
    SECONDARY_CONTAINER = "secondary-container"
    SECONDARY_FIXED = "secondary-fixed"
    SECONDARY_FIXED_DIM = "secondary-fixed-dim"
    SHADOW = "shadow"
    SURFACE = "surface"
    SURFACE_BRIGHT = "surface-bright"
    SURFACE_CONTAINER = "surface-container"
    SURFACE_CONTAINER_HIGH = "surface-container-high"
    SURFACE_CONTAINER_HIGHEST = "surface-container-highest"
    SURFACE_CONTAINER_LOW = "surface-container-low"
    SURFACE_CONTAINER_LOWEST = "surface-container-lowest"
    SURFACE_DIM = "surface-dim"
    SURFACE_TINT = "surface-tint"
    SURFACE_VARIANT = "surface-variant"
    TERTIARY = "tertiary"
    TERTIARY_CONTAINER = "tertiary-container"
    TERTIARY_FIXED = "tertiary-fixed"
    TERTIARY_FIXED_DIM = "tertiary-fixed-dim"


def tone_key(role: ColorRole | str, *, dark: bool = False) -> str:
    """Return the palette tone-key for ``role`` in the given scheme."""
    roles = DARK_ROLES if dark else LIGHT_ROLES
    return roles[str(role)]


def hex_for_tone(tone: str) -> str:
    """Return the hex string for a palette tone-key (e.g. ``primary40``)."""
    return REF_PALETTE[tone]


def resolve_hex(role: ColorRole | str, *, dark: bool = False) -> str:
    """Resolve a color role to its hex string for light or dark scheme."""
    return hex_for_tone(tone_key(role, dark=dark))


__all__ = [
    "ColorRole",
    "DARK_ROLES",
    "LIGHT_ROLES",
    "REF_PALETTE",
    "hex_for_tone",
    "resolve_hex",
    "tone_key",
]
