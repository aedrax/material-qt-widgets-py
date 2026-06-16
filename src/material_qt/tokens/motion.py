"""Motion durations and easings (pure Python, no Qt)."""

from __future__ import annotations

from enum import Enum

from ._generated.motion import DURATIONS_MS, EASINGS


class Duration(Enum):
    """Material 3 motion durations. Values are milliseconds (int)."""

    SHORT1 = DURATIONS_MS["short1"]
    SHORT2 = DURATIONS_MS["short2"]
    SHORT3 = DURATIONS_MS["short3"]
    SHORT4 = DURATIONS_MS["short4"]
    MEDIUM1 = DURATIONS_MS["medium1"]
    MEDIUM2 = DURATIONS_MS["medium2"]
    MEDIUM3 = DURATIONS_MS["medium3"]
    MEDIUM4 = DURATIONS_MS["medium4"]
    LONG1 = DURATIONS_MS["long1"]
    LONG2 = DURATIONS_MS["long2"]
    LONG3 = DURATIONS_MS["long3"]
    LONG4 = DURATIONS_MS["long4"]
    EXTRA_LONG1 = DURATIONS_MS["extra-long1"]
    EXTRA_LONG2 = DURATIONS_MS["extra-long2"]
    EXTRA_LONG3 = DURATIONS_MS["extra-long3"]
    EXTRA_LONG4 = DURATIONS_MS["extra-long4"]

    @property
    def ms(self) -> int:
        return int(self.value)


class Easing(Enum):
    """Material 3 easing curves as ((x1, y1), (x2, y2)) cubic-bezier control points."""

    STANDARD = EASINGS["standard"]
    STANDARD_ACCELERATE = EASINGS["standard-accelerate"]
    STANDARD_DECELERATE = EASINGS["standard-decelerate"]
    EMPHASIZED = EASINGS["emphasized"]
    EMPHASIZED_ACCELERATE = EASINGS["emphasized-accelerate"]
    EMPHASIZED_DECELERATE = EASINGS["emphasized-decelerate"]
    LEGACY = EASINGS["legacy"]
    LEGACY_ACCELERATE = EASINGS["legacy-accelerate"]
    LEGACY_DECELERATE = EASINGS["legacy-decelerate"]
    LINEAR = EASINGS["linear"]

    @property
    def control_points(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return self.value


__all__ = ["DURATIONS_MS", "EASINGS", "Duration", "Easing"]
