"""Small dependency-free domain models used across the application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

FACE_SHAPES = ("oval", "round", "square", "oblong", "heart", "diamond")


@dataclass(frozen=True)
class FaceMeasurements:
    """Resolution-independent ratios derived from a near-frontal portrait."""

    face_length: float
    forehead_width: float
    cheekbone_width: float
    jaw_width: float
    length_to_width: float
    forehead_to_cheek: float
    jaw_to_cheek: float
    yaw_asymmetry: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {name: round(float(value), 4) for name, value in vars(self).items()}


@dataclass(frozen=True)
class FaceShapeResult:
    label: str
    confidence: float
    runner_up: str
    ambiguous: bool
    scores: dict[str, float]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Preferences:
    desired_length: str = "any"
    maintenance: str = "any"
    fade: str = "any"
    texture: str = "any"
    category: str = "any"


@dataclass(frozen=True)
class Hairstyle:
    id: str
    name: str
    description: str
    face_shapes: tuple[str, ...]
    length: str
    fade: str
    textures: tuple[str, ...]
    maintenance: str
    category: str
    silhouette: str
    robot_parameters: dict[str, Any]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Hairstyle:
        return cls(
            id=value["id"],
            name=value["name"],
            description=value["description"],
            face_shapes=tuple(value["face_shapes"]),
            length=value["length"],
            fade=value["fade"],
            textures=tuple(value["textures"]),
            maintenance=value["maintenance"],
            category=value["category"],
            silhouette=value["silhouette"],
            robot_parameters=dict(value["robot_parameters"]),
        )


@dataclass(frozen=True)
class Recommendation:
    style: Hairstyle
    score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)
    breakdown: dict[str, float] = field(default_factory=dict)
