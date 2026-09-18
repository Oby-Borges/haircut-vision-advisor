"""Transparent, tuneable face-shape heuristic."""

from __future__ import annotations

from .types import FaceMeasurements, FaceShapeResult


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _near(value: float, target: float, tolerance: float) -> float:
    return _clamp(1.0 - abs(value - target) / tolerance)


def classify_face_shape(m: FaceMeasurements) -> FaceShapeResult:
    """Score six conventional labels using visible geometric relationships.

    The labels are intentionally approximate. Scores express heuristic fit, not
    probabilities and not attractiveness.
    """

    aspect = m.length_to_width
    forehead = m.forehead_to_cheek
    jaw = m.jaw_to_cheek

    scores = {
        "round": 0.55 * _near(aspect, 1.08, 0.30)
        + 0.25 * _near(jaw, 0.90, 0.20)
        + 0.20 * _near(forehead, 0.90, 0.22),
        "square": 0.45 * _near(aspect, 1.18, 0.30)
        + 0.35 * _near(jaw, 0.96, 0.16)
        + 0.20 * _near(forehead, 0.91, 0.22),
        "oblong": 0.65 * _clamp((aspect - 1.34) / 0.34)
        + 0.20 * _near(jaw, 0.86, 0.22)
        + 0.15 * _near(forehead, 0.90, 0.22),
        "heart": 0.45 * _clamp((forehead - jaw + 0.02) / 0.22)
        + 0.25 * _near(forehead, 0.96, 0.19)
        + 0.30 * _clamp((1.0 - jaw) / 0.25),
        "diamond": 0.55 * _clamp((1.0 - max(forehead, jaw)) / 0.25)
        + 0.25 * _near(aspect, 1.35, 0.32)
        + 0.20 * _near(forehead, jaw, 0.16),
        "oval": 0.55 * _near(aspect, 1.36, 0.30)
        + 0.25 * _near(jaw, 0.82, 0.19)
        + 0.20 * _near(forehead, 0.88, 0.20),
    }
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    (label, top), (runner_up, second) = ordered[:2]
    margin = top - second
    confidence = _clamp(0.45 + margin * 1.6)
    ambiguous = margin < 0.10

    reasons = [
        f"Face length is {aspect:.2f}× cheekbone width.",
        f"Forehead width is {forehead:.2f}× cheekbone width.",
        f"Jaw width is {jaw:.2f}× cheekbone width.",
    ]
    if aspect >= 1.48:
        reasons.append("The face appears distinctly longer than it is wide.")
    elif aspect <= 1.20:
        reasons.append("Face length and width are relatively similar.")
    if forehead - jaw >= 0.12:
        reasons.append("The forehead appears wider than the jaw.")
    if max(forehead, jaw) <= 0.82:
        reasons.append("The cheekbones appear to be the widest measured area.")
    if jaw >= 0.91:
        reasons.append("The jaw and cheekbone widths appear relatively close.")
    if ambiguous:
        reasons.append(f"The result is close to {runner_up}; treat both as useful options.")

    return FaceShapeResult(
        label=label,
        confidence=round(confidence, 3),
        runner_up=runner_up,
        ambiguous=ambiguous,
        scores={key: round(value, 3) for key, value in scores.items()},
        reasons=tuple(reasons),
    )
