"""Explainable hairstyle scoring."""

from __future__ import annotations

from .types import FaceShapeResult, Hairstyle, Preferences, Recommendation

LENGTH_ORDER = ("shaved", "very_short", "short", "medium", "long")
MAINTENANCE_ORDER = ("low", "medium", "high")


def _ordered_match(value: str, desired: str, order: tuple[str, ...], maximum: float) -> float:
    if desired == "any":
        return maximum * 0.67
    gap = abs(order.index(value) - order.index(desired))
    return maximum if gap == 0 else maximum * 0.55 if gap == 1 else maximum * 0.12


def score_hairstyle(
    style: Hairstyle,
    shape: FaceShapeResult,
    preferences: Preferences,
) -> Recommendation:
    breakdown: dict[str, float] = {}
    reasons: list[str] = []

    if shape.label in style.face_shapes:
        breakdown["face_shape"] = 38.0
        reasons.append(f"Cataloged as a strong option for {shape.label} face shapes")
    elif shape.ambiguous and shape.runner_up in style.face_shapes:
        breakdown["face_shape"] = 26.0
        reasons.append(f"Fits the close runner-up shape ({shape.runner_up})")
    else:
        breakdown["face_shape"] = 8.0

    breakdown["length"] = _ordered_match(
        style.length, preferences.desired_length, LENGTH_ORDER, 18.0
    )
    if preferences.desired_length == style.length:
        reasons.append(f"Matches the requested {style.length.replace('_', ' ')} length")

    breakdown["maintenance"] = _ordered_match(
        style.maintenance, preferences.maintenance, MAINTENANCE_ORDER, 12.0
    )
    if preferences.maintenance == style.maintenance:
        reasons.append(f"Matches the requested {style.maintenance} maintenance level")

    has_fade = style.fade != "none"
    if preferences.fade == "any":
        breakdown["fade"] = 6.0
    elif (preferences.fade == "yes" and has_fade) or (preferences.fade == "no" and not has_fade):
        breakdown["fade"] = 10.0
        reasons.append("Matches the fade preference")
    else:
        breakdown["fade"] = 0.0

    if preferences.texture == "any":
        breakdown["texture"] = 8.0
    elif preferences.texture in style.textures or "all" in style.textures:
        breakdown["texture"] = 12.0
        reasons.append(f"Works with {preferences.texture} texture")
    else:
        breakdown["texture"] = 2.0

    if preferences.category == "any":
        breakdown["category"] = 6.0
    elif preferences.category == style.category:
        breakdown["category"] = 10.0
        reasons.append(f"Matches the {style.category} style category")
    else:
        breakdown["category"] = 1.0

    score = round(sum(breakdown.values()), 1)
    return Recommendation(style=style, score=score, reasons=tuple(reasons), breakdown=breakdown)


def rank_hairstyles(
    styles: list[Hairstyle],
    shape: FaceShapeResult,
    preferences: Preferences,
) -> list[Recommendation]:
    return sorted(
        (score_hairstyle(style, shape, preferences) for style in styles),
        key=lambda recommendation: (-recommendation.score, recommendation.style.name),
    )
