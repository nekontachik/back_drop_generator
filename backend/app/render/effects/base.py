"""Base effect abstract class (D-06).

All visual effects inherit from BaseEffect and implement render_frame.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class BaseEffect(ABC):
    """Abstract base class for all visual effects.

    Each effect renders a single frame given normalized time, dimensions,
    parameters, beat intensity, and a random number generator for
    reproducibility.
    """

    @abstractmethod
    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Render a single frame.

        Args:
            t: Normalized time in [0.0, 1.0) for seamless looping.
            width: Frame width in pixels.
            height: Frame height in pixels.
            params: Effect-specific parameters dict.
            beat_intensity: Beat envelope value at this frame [0.0, 1.0].
            rng: NumPy random generator for reproducibility.

        Returns:
            RGB frame as uint8 ndarray of shape (height, width, 3).
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique effect name used for registry lookup."""
