"""Material Design 3 design tokens (pure Python, zero Qt imports).

Single source of truth for color, typography, shape, elevation, motion and
state values, transcribed from ``tokens/versions/v0_192/*.scss``. Everything in
this subpackage is headless-testable and must never import Qt.
"""

from __future__ import annotations

from .color import ColorRole, hex_for_tone, resolve_hex, tone_key
from .elevation import ElevationLevel, ShadowSpec, ambient_shadow, key_shadow
from .motion import Duration, Easing
from .shape import CornerRadii, ShapeScale
from .state import StateLayer
from .typography import TypescaleRole, TypescaleSpec, spec_for

__all__ = [
    "ColorRole",
    "CornerRadii",
    "Duration",
    "Easing",
    "ElevationLevel",
    "ShadowSpec",
    "ShapeScale",
    "StateLayer",
    "TypescaleRole",
    "TypescaleSpec",
    "ambient_shadow",
    "hex_for_tone",
    "key_shadow",
    "resolve_hex",
    "spec_for",
    "tone_key",
]
