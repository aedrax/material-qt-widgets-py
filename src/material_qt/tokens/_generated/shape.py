# GENERATED FROM tokens/versions/v0_192 — DO NOT EDIT
"""Shape corner radii (px). CORNER scalars + per-corner shorthands."""

CORNER: dict[str, float] = {
    "none": 0.0,
    "extra-small": 4.0,
    "small": 8.0,
    "medium": 12.0,
    "large": 16.0,
    "extra-large": 28.0,
    "full": 9999.0,
}

# Per-corner shorthands as (tl, tr, br, bl) tuples in px.
PER_CORNER: dict[str, tuple] = {
    "extra-large-top": (28.0, 28.0, 0.0, 0.0),
    "extra-small-top": (4.0, 4.0, 0.0, 0.0),
    "large-top": (16.0, 16.0, 0.0, 0.0),
    "large-start": (16.0, 0.0, 0.0, 16.0),
    "large-end": (0.0, 16.0, 16.0, 0.0),
}
