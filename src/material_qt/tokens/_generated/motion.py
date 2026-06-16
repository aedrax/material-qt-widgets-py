# GENERATED FROM tokens/versions/v0_192 — DO NOT EDIT
"""Motion durations (ms) and easing control points ((x1,y1),(x2,y2))."""

DURATIONS_MS: dict[str, int] = {
    "extra-long1": 700,
    "extra-long2": 800,
    "extra-long3": 900,
    "extra-long4": 1000,
    "long1": 450,
    "long2": 500,
    "long3": 550,
    "long4": 600,
    "medium1": 250,
    "medium2": 300,
    "medium3": 350,
    "medium4": 400,
    "short1": 50,
    "short2": 100,
    "short3": 150,
    "short4": 200,
}

EASINGS: dict[str, tuple] = {
    "emphasized": ((0.2, 0.0), (0.0, 1.0)),
    "emphasized-accelerate": ((0.3, 0.0), (0.8, 0.15)),
    "emphasized-decelerate": ((0.05, 0.7), (0.1, 1.0)),
    "legacy": ((0.4, 0.0), (0.2, 1.0)),
    "legacy-accelerate": ((0.4, 0.0), (1.0, 1.0)),
    "legacy-decelerate": ((0.0, 0.0), (0.2, 1.0)),
    "linear": ((0.0, 0.0), (1.0, 1.0)),
    "standard": ((0.2, 0.0), (0.0, 1.0)),
    "standard-accelerate": ((0.3, 0.0), (1.0, 1.0)),
    "standard-decelerate": ((0.0, 0.0), (0.0, 1.0)),
}
