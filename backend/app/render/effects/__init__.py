"""Effect registry for visual effects."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.render.effects.base import BaseEffect

EFFECT_REGISTRY: dict[str, type[BaseEffect]] = {}


def register(cls: type[BaseEffect]) -> type[BaseEffect]:
    """Register an effect class by its name property."""
    instance = cls()
    EFFECT_REGISTRY[instance.name] = cls
    return cls
