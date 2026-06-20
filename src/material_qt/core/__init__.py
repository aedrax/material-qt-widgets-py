"""Core: shared interaction, painting and motion machinery (Qt-dependent)."""

from __future__ import annotations

from .elevation import ElevationPainter, apply_elevation
from .focus_ring import FocusRingController
from .focus_util import drop_focus_within
from .interaction_state import InteractionState
from .material_widget import MaterialWidget, MaterialWidgetMixin
from .motion import MOTION_ENABLED, animate, duration_ms, easing_curve
from .responsive import (
    ResponsiveHelper,
    WindowSizeClass,
    clamp_dialog_width,
    size_class_for,
)
from .ripple import RippleController
from .shape_util import dp, px, resolve_radius, rounded_path
from .state_layer import StateLayerPainter
from .typography_util import apply as apply_typography
from .typography_util import font_for, font_for_role

__all__ = [
    "MOTION_ENABLED",
    "ElevationPainter",
    "FocusRingController",
    "InteractionState",
    "MaterialWidget",
    "MaterialWidgetMixin",
    "ResponsiveHelper",
    "RippleController",
    "StateLayerPainter",
    "WindowSizeClass",
    "animate",
    "apply_elevation",
    "apply_typography",
    "clamp_dialog_width",
    "drop_focus_within",
    "dp",
    "duration_ms",
    "easing_curve",
    "font_for",
    "font_for_role",
    "px",
    "resolve_radius",
    "rounded_path",
    "size_class_for",
]
