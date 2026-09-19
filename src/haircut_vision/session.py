"""Four-view capture and versioned, non-executable TrimSync handoffs."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

from .handoff import validate_handoff

VIEWS = ("front", "left", "right", "rear")


def new_session():
    return {
        "session_id": f"session-{uuid4().hex[:12]}",
        "subject_id": f"subject-{uuid4().hex[:8]}",
        "captures": {},
        "preferences": None,
        "plan": None,
        "approval": None,
    }


def invalidate(session):
    session["plan"] = None
    session["approval"] = None


def save_capture(session, view, capture):
    if view not in (*VIEWS, "crown"):
        raise ValueError("Unknown capture view")
    if not capture.get("reviewed"):
        raise ValueError("Review this view before saving it")
    if capture.get("issues"):
        raise ValueError("Retake the photo to resolve quality issues before saving")
    if session["captures"] and any(
        c.get("synthetic", False) != capture.get("synthetic", False)
        for c in session["captures"].values()
    ):
        raise ValueError("Start a fresh session before switching between demo and real photos")
    if any(
        entry["digest"] == capture["digest"]
        for key, entry in session["captures"].items()
        if key != view
    ):
        raise ValueError("This image is already assigned to another view. Take a new photo.")
    session["captures"][view] = capture
    invalidate(session)


def scan_status(session):
    captures = session["captures"]
    coverage = {view: bool(captures.get(view, {}).get("reviewed")) for view in (*VIEWS, "crown")}
    front = captures.get("front", {})
    complete = all(coverage[v] for v in VIEWS) and bool(front.get("landmarks"))
    return {
        "session_id": session["session_id"],
        "subject_id": session["subject_id"],
        "scan_complete": complete,
        "coverage": coverage,
        "confidence": None,
        "head_frame_ready": False,
        "assessment": "four-view photo review; not calibrated 3D reconstruction",
        "synthetic": any(c.get("synthetic", False) for c in captures.values()),
    }


def update_preferences(session, preferences):
    if session["preferences"] != preferences:
        session["preferences"] = deepcopy(preferences)
        invalidate(session)


def create_plan(session, style, preview_settings):
    preview_settings = {
        "color": "#342c25",
        "scale": 1.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        **preview_settings,
    }
    if not scan_status(session)["scan_complete"] or session["preferences"] is None:
        raise ValueError("Complete the four-view scan and questionnaire first")
    fingerprint = {
        "session_id": session["session_id"],
        "style_id": style.id,
        "preferences": session["preferences"],
        "captures": {v: c["digest"] for v, c in sorted(session["captures"].items())},
        "preview": preview_settings,
    }
    digest = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()[:16]
    plan_id = f"plan-{digest}"
    if session["plan"] and session["plan"]["plan_id"] == plan_id:
        return session["plan"]
    session["approval"] = None
    prefs = session["preferences"]
    plan = {
        "session_id": session["session_id"],
        "subject_id": session["subject_id"],
        "plan_id": plan_id,
        "approved": False,
        "style": style.id,
        "preferences": deepcopy(prefs),
        "constraints": {"no_cut_regions": prefs["no_cut_regions"]},
        "proposal": {
            "top_length_mm": prefs["top_length_mm"] if prefs["cut_top"] else None,
            "side_length_mm": prefs["base_length_mm"],
            "back_length_mm": prefs["base_length_mm"],
            "fade_type": prefs["fade_height"],
        },
        "scan": scan_status(session),
        "preview": {
            "plan_id": plan_id,
            "kind": "illustrative_front_silhouette",
            "settings": deepcopy(preview_settings),
            "head_relative_map_ready": False,
        },
        "planning": {"plan_id": plan_id, "status": "awaiting_vision_and_ik", "executable": False},
    }
    session["plan"] = plan
    return plan


def approve_plan(session, plan_id):
    if not session["plan"] or session["plan"]["plan_id"] != plan_id:
        raise ValueError("The plan changed. Review the current preview before approving.")
    session["approval"] = {"plan_id": plan_id, "approved_at": datetime.now(UTC).isoformat()}
    session["plan"]["approved"] = True


def export_handoff(session):
    plan = session["plan"]
    if not plan or not session["approval"] or session["approval"]["plan_id"] != plan["plan_id"]:
        raise ValueError("Approve the current plan before exporting")
    payload = {
        "schema_version": "trimsync-app-draft-1",
        **deepcopy(plan),
        "approval": deepcopy(session["approval"]),
    }
    validate_handoff(payload)
    return payload
