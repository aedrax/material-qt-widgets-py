# GENERATED FROM tokens/versions/v0_192 — DO NOT EDIT
"""Elevation: level -> dp, plus dual key/ambient shadow tuples.

Shadow tuples are (dx, dy, blur, spread) in px. Key (umbra) shadows use
opacity 0.3; ambient (penumbra) shadows use opacity 0.15. These are
hand-transcribed from elevation/internal/_elevation.scss (computed there
via clamp() rather than a flat map).
"""

LEVEL_DP: dict[int, int] = {
    0: 0,
    1: 1,
    2: 3,
    3: 6,
    4: 8,
    5: 12,
}

KEY_SHADOW_OPACITY = 0.3
AMBIENT_SHADOW_OPACITY = 0.15

# (dx, dy, blur, spread) px
KEY_SHADOWS: dict[int, tuple] = {
    0: (0, 0, 0, 0),
    1: (0, 1, 2, 0),
    2: (0, 1, 2, 0),
    3: (0, 1, 3, 0),
    4: (0, 2, 3, 0),
    5: (0, 4, 4, 0),
}

AMBIENT_SHADOWS: dict[int, tuple] = {
    0: (0, 0, 0, 0),
    1: (0, 1, 3, 1),
    2: (0, 2, 6, 2),
    3: (0, 4, 8, 3),
    4: (0, 6, 10, 4),
    5: (0, 8, 12, 6),
}
