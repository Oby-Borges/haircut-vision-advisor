"""Draft app envelope, deliberately distinct from controller API payloads."""

from jsonschema import Draft202012Validator, FormatChecker


def object_schema(properties):
    return {
        "type": "object",
        "required": list(properties),
        "additionalProperties": False,
        "properties": properties,
    }


IDENTIFIER = {"type": "string", "minLength": 1}
LENGTH = {"type": "number", "minimum": 0, "maximum": 300}
HANDOFF_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TrimSync approved app draft — never an execution command",
    **object_schema(
        {
            "schema_version": {"const": "trimsync-app-draft-1"},
            "session_id": IDENTIFIER,
            "subject_id": IDENTIFIER,
            "plan_id": IDENTIFIER,
            "approved": {"const": True},
            "style": IDENTIFIER,
            "preferences": {
                "type": "object",
                "required": ["cut_top", "no_cut_regions"],
                "properties": {
                    "cut_top": {"type": "boolean"},
                    "no_cut_regions": {"type": "array", "items": {"type": "string"}},
                },
            },
            "constraints": object_schema(
                {"no_cut_regions": {"type": "array", "items": {"type": "string"}}}
            ),
            "proposal": object_schema(
                {
                    "top_length_mm": {**LENGTH, "type": ["number", "null"]},
                    "side_length_mm": LENGTH,
                    "back_length_mm": LENGTH,
                    "fade_type": {"enum": ["none", "taper", "low", "mid", "high"]},
                }
            ),
            "scan": object_schema(
                {
                    "session_id": IDENTIFIER,
                    "subject_id": IDENTIFIER,
                    "scan_complete": {"const": True},
                    "coverage": object_schema(
                        {
                            **{v: {"const": True} for v in ("front", "left", "right", "rear")},
                            "crown": {"type": "boolean"},
                        }
                    ),
                    "confidence": {"type": "null"},
                    "head_frame_ready": {"const": False},
                    "assessment": {"type": "string"},
                    "synthetic": {"type": "boolean"},
                }
            ),
            "preview": object_schema(
                {
                    "plan_id": IDENTIFIER,
                    "kind": {"const": "illustrative_front_silhouette"},
                    "settings": object_schema(
                        {
                            "color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                            "scale": {"type": "number", "minimum": 0.75, "maximum": 1.35},
                            "x_offset": {"type": "number", "minimum": -0.1, "maximum": 0.1},
                            "y_offset": {"type": "number", "minimum": -0.1, "maximum": 0.1},
                        }
                    ),
                    "head_relative_map_ready": {"const": False},
                }
            ),
            "planning": object_schema(
                {
                    "plan_id": IDENTIFIER,
                    "status": {"const": "awaiting_vision_and_ik"},
                    "executable": {"const": False},
                }
            ),
            "approval": object_schema(
                {
                    "plan_id": IDENTIFIER,
                    "approved_at": {"type": "string", "format": "date-time"},
                }
            ),
        }
    ),
}


def validate_handoff(payload):
    Draft202012Validator(HANDOFF_SCHEMA, format_checker=FormatChecker()).validate(payload)
    if any(
        payload[key]["plan_id"] != payload["plan_id"] for key in ("preview", "planning", "approval")
    ):
        raise ValueError("Preview, planning placeholder, and approval must use the same plan ID")
    for key in ("session_id", "subject_id"):
        if payload["scan"][key] != payload[key]:
            raise ValueError("Scan belongs to a different session or subject")
    if payload["constraints"]["no_cut_regions"] != payload["preferences"]["no_cut_regions"]:
        raise ValueError("No-cut constraints differ from the approved preferences")
    if (payload["proposal"]["top_length_mm"] is not None) != payload["preferences"]["cut_top"]:
        raise ValueError("Keep-top choices must export a null top length")
