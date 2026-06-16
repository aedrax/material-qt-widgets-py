"""Pure-data tests: generated token values match the SCSS source values."""

from __future__ import annotations

from material_qt.tokens.color import (
    ColorRole,
    hex_for_tone,
    resolve_hex,
    tone_key,
)
from material_qt.tokens.elevation import (
    ElevationLevel,
    ambient_shadow,
    key_shadow,
)
from material_qt.tokens.motion import Duration, Easing
from material_qt.tokens.shape import CORNER, CornerRadii, ShapeScale
from material_qt.tokens.state import StateLayer
from material_qt.tokens.typography import TypescaleRole, spec_for
from material_qt.tokens._generated.palette import REF_PALETTE


def test_palette_count_and_known_values():
    # 89 numeric tones across the color families + black + white
    assert len(REF_PALETTE) == 91
    assert REF_PALETTE["primary40"] == "#6750a4"
    assert REF_PALETTE["neutral6"] == "#141218"
    assert REF_PALETTE["error40"] == "#b3261e"
    assert REF_PALETTE["white"] == "#ffffff"


def test_color_role_resolution_light_dark():
    # primary -> primary40 (light) / primary80 (dark)
    assert tone_key(ColorRole.PRIMARY, dark=False) == "primary40"
    assert tone_key(ColorRole.PRIMARY, dark=True) == "primary80"
    assert resolve_hex(ColorRole.PRIMARY, dark=False) == "#6750a4"
    assert resolve_hex(ColorRole.PRIMARY, dark=True) == "#d0bcff"
    # surface differs between schemes
    assert resolve_hex(ColorRole.SURFACE, dark=False) == "#fef7ff"
    assert resolve_hex(ColorRole.SURFACE, dark=True) == "#141218"
    assert hex_for_tone("secondary40") == "#625b71"


def test_every_role_resolves():
    for role in ColorRole:
        assert resolve_hex(role, dark=False).startswith("#")
        assert resolve_hex(role, dark=True).startswith("#")


def test_typescale_values():
    body_large = spec_for(TypescaleRole.BODY_LARGE)
    assert body_large.family == "Roboto"
    assert body_large.size_rem == 1.0
    assert body_large.line_height_rem == 1.5
    assert body_large.weight == 400
    assert body_large.tracking_rem == 0.03125
    assert body_large.size_px == 16.0

    label_large = spec_for(TypescaleRole.LABEL_LARGE)
    assert label_large.weight == 500

    display_large = spec_for(TypescaleRole.DISPLAY_LARGE)
    assert display_large.size_rem == 3.5625
    assert display_large.tracking_rem == -0.015625


def test_typescale_has_15_roles():
    assert len(list(TypescaleRole)) == 15


def test_shape_corner_values():
    assert CORNER["none"] == 0
    assert CORNER["extra-small"] == 4
    assert CORNER["small"] == 8
    assert CORNER["medium"] == 12
    assert CORNER["large"] == 16
    assert CORNER["extra-large"] == 28
    assert CORNER["full"] == 9999


def test_corner_radii_from_scale_and_shorthand():
    r = CornerRadii.from_scale(ShapeScale.MEDIUM)
    assert r.as_tuple() == (12, 12, 12, 12)
    top = CornerRadii.from_shorthand("large-top")
    assert top.as_tuple() == (16, 16, 0, 0)
    assert CornerRadii.from_scale(ShapeScale.FULL).is_full


def test_elevation_dp():
    assert [ElevationLevel(i).dp for i in range(6)] == [0, 1, 3, 6, 8, 12]


def test_elevation_shadow_tuples():
    assert key_shadow(1).dy == 1
    assert key_shadow(1).opacity == 0.3
    assert key_shadow(5) == type(key_shadow(5))(0, 4, 4, 0, 0.3)
    assert ambient_shadow(1) == type(ambient_shadow(1))(0, 1, 3, 1, 0.15)
    assert ambient_shadow(5).blur == 12
    assert ambient_shadow(0).opacity == 0.15


def test_motion_durations():
    assert Duration.SHORT1.ms == 50
    assert Duration.MEDIUM2.ms == 300
    assert Duration.LONG1.ms == 450
    assert Duration.LONG4.ms == 600
    assert Duration.EXTRA_LONG4.ms == 1000


def test_motion_easings():
    assert Easing.STANDARD.control_points == ((0.2, 0.0), (0.0, 1.0))
    assert Easing.EMPHASIZED.control_points == ((0.2, 0.0), (0.0, 1.0))
    assert Easing.LINEAR.control_points == ((0.0, 0.0), (1.0, 1.0))
    assert Easing.EMPHASIZED_DECELERATE.control_points == ((0.05, 0.7), (0.1, 1.0))
    assert Easing.LEGACY.control_points == ((0.4, 0.0), (0.2, 1.0))


def test_state_opacities():
    assert StateLayer.HOVER.opacity == 0.08
    assert StateLayer.FOCUS.opacity == 0.12
    assert StateLayer.PRESSED.opacity == 0.12
    assert StateLayer.DRAGGED.opacity == 0.16
