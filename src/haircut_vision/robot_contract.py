"""Validated, descriptive integration contract—not a robot command channel."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .types import Hairstyle

ROBOT_OUTPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.invalid/schemas/haircut-selection-v1.json",
    "title": "Selected hairstyle proposal",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "contract_type",
        "user_confirmed_selection",
        "style_id",
        "style_name",
        "top_length_mm",
        "side_length_mm",
        "back_length_mm",
        "fade_type",
        "fade_start_mm",
        "notes",
        "generated_at",
    ],
    "properties": {
        "schema_version": {"const": "1.0"},
        "contract_type": {"const": "descriptive_haircut_proposal"},
        "user_confirmed_selection": {"const": True},
        "style_id": {"type": "string", "pattern": "^[a-z0-9_]+$"},
        "style_name": {"type": "string", "minLength": 1},
        "top_length_mm": {"type": "number", "minimum": 0, "maximum": 300},
        "side_length_mm": {"type": "number", "minimum": 0, "maximum": 300},
        "back_length_mm": {"type": "number", "minimum": 0, "maximum": 300},
        "fade_type": {"enum": ["none", "taper", "low", "mid", "high", "skin"]},
        "fade_start_mm": {"type": ["number", "null"], "minimum": 0, "maximum": 120},
        "notes": {"type": "string", "maxLength": 1000},
        "generated_at": {"type": "string", "format": "date-time"},
    },
}


def build_robot_output(style: Hairstyle, *, user_confirmed: bool) -> dict[str, Any]:
    if not user_confirmed:
        raise ValueError("Explicit user selection is required before creating the contract")
    payload = {
        "schema_version": "1.0",
        "contract_type": "descriptive_haircut_proposal",
        "user_confirmed_selection": True,
        "style_id": style.id,
        "style_name": style.name,
        **deepcopy(style.robot_parameters),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    validate_robot_output(payload)
    return payload


def validate_robot_output(payload: dict[str, Any]) -> None:
    required = set(ROBOT_OUTPUT_SCHEMA["required"])
    missing = required - payload.keys()
    extra = payload.keys() - set(ROBOT_OUTPUT_SCHEMA["properties"])
    if missing:
        raise ValueError(f"Missing contract fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"Unexpected contract fields: {sorted(extra)}")
    if payload["schema_version"] != "1.0":
        raise ValueError("Unsupported schema version")
    if payload["contract_type"] != "descriptive_haircut_proposal":
        raise ValueError("Invalid contract type")
    if payload["user_confirmed_selection"] is not True:
        raise ValueError("Selection must be explicitly confirmed")
    if payload["fade_type"] not in {"none", "taper", "low", "mid", "high", "skin"}:
        raise ValueError("Unsupported fade type")
    for key in ("top_length_mm", "side_length_mm", "back_length_mm"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 300:
            raise ValueError(f"{key} must be a number from 0 to 300")
    fade_start = payload["fade_start_mm"]
    if fade_start is not None and (
        isinstance(fade_start, bool)
        or not isinstance(fade_start, (int, float))
        or not 0 <= fade_start <= 120
    ):
        raise ValueError("fade_start_mm must be null or a number from 0 to 120")
    if not isinstance(payload["notes"], str) or len(payload["notes"]) > 1000:
        raise ValueError("notes must be a string of at most 1000 characters")
    try:
        datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError("generated_at must be an ISO 8601 date-time") from exc
