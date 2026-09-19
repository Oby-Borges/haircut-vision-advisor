"""TrimSync capture, style review, and integration workspace."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from haircut_vision.catalog import load_catalog  # noqa: E402
from haircut_vision.face_shape import classify_face_shape  # noqa: E402
from haircut_vision.handoff import HANDOFF_SCHEMA  # noqa: E402
from haircut_vision.preview import render_preview  # noqa: E402
from haircut_vision.recommend import rank_hairstyles  # noqa: E402
from haircut_vision.scan import assess_capture, demo_view, load_capture  # noqa: E402
from haircut_vision.session import (  # noqa: E402
    VIEWS,
    approve_plan,
    create_plan,
    export_handoff,
    invalidate,
    new_session,
    save_capture,
    scan_status,
    update_preferences,
)
from haircut_vision.style_images import style_image_path  # noqa: E402
from haircut_vision.types import Preferences  # noqa: E402

st.set_page_config(page_title="TrimSync · Your next cut", page_icon="✂", layout="wide")
st.markdown((ROOT / "assets" / "theme.css").read_text(encoding="utf-8"), unsafe_allow_html=True)
if "trim_session" not in st.session_state:
    st.session_state.trim_session = new_session()
session = st.session_state.trim_session
status = scan_status(session)
# Explicitly preserve widget state while navigating between workspace screens.
for saved_key in list(st.session_state):
    if (
        saved_key.startswith(("pref_", "preview_", "check_", "issue_"))
        or saved_key == "selected_style"
    ):
        st.session_state[saved_key] = st.session_state[saved_key]


def go(page):
    st.session_state.page = page


def title(kicker, heading, description):
    st.markdown(f'<div class="kicker">{kicker}</div><h1>{heading}</h1>', unsafe_allow_html=True)
    st.write(description)


with st.sidebar:
    st.markdown(
        '<div class="brand">trim<span>sync</span><i> / studio</i></div>', unsafe_allow_html=True
    )
    st.caption("A LITTLE VISION. A BETTER CUT.")
    page = st.radio(
        "Workspace",
        ["01  Capture", "02  Your preferences", "03  Style studio", "04  Integration"],
        key="page",
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("CURRENT SESSION")
    st.code(session["session_id"], language=None)
    st.caption(f"{sum(status['coverage'][v] for v in VIEWS)} of 4 views reviewed")
    st.progress(sum(status["coverage"][v] for v in VIEWS) / 4)
    if status["synthetic"]:
        st.info("Demo session · synthetic images")
    st.caption(
        "Photos stay in this session’s server memory. Handoff downloads contain metadata only."
    )
    if st.button("Start a fresh session", width="stretch"):
        for key in list(st.session_state):
            del st.session_state[key]
        st.rerun()

st.markdown(
    '<div class="topline">TRIMSYNC / PERSONAL STYLE LAB <span>VTHACKS · 2026</span></div>',
    unsafe_allow_html=True,
)

if page == "01  Capture":
    title(
        "01 / GET THE WHOLE PICTURE",
        "Every angle. Your next look.",
        "Capture four views, tell us what you like, and explore a cut that feels like you.",
    )
    left, right = st.columns([1.65, 1], gap="large")
    with right:
        st.markdown(
            '<div class="editorial"><div class="orb">✂</div>'
            "<span>MADE AROUND YOU</span><h2>A fresh perspective.<br>A considered cut.</h2>"
            "<p>Four angles. Fifteen starting points.<br>One choice that is yours.</p></div>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown("**Your capture checklist**")
            for view in VIEWS:
                st.write(f"{'✓' if status['coverage'][view] else '○'}  {view.title()}")
            st.caption(
                "Use even light, keep the entire head in frame, and use the same person throughout."
            )
    with left:
        mode = st.radio(
            "Image source",
            ["Upload photos", "Camera snapshots", "Demo"],
            index=2 if st.query_params.get("demo") == "1" else 0,
            horizontal=True,
        )
        if mode == "Demo":
            st.info("Original illustrations demonstrate the workflow. No real face is analyzed.")
            if st.button("Load four-view demo", type="primary", width="stretch"):
                session["captures"] = {}
                for view in VIEWS:
                    record = assess_capture(demo_view(view), view, synthetic=True)
                    record["reviewed"] = True
                    save_capture(session, view, record)
                st.rerun()
        else:
            view = st.selectbox("View to capture", [*VIEWS, "crown"], format_func=str.title)
            guidance = {
                "front": "Look straight at the camera with your forehead and chin visible.",
                "left": "Show the subject’s left side, including the ear and hairline.",
                "right": "Show the subject’s right side, including the ear and hairline.",
                "rear": "Show the back of the head and neckline. A helper can take this photo.",
                "crown": "Optional: photograph the top of the head for the Vision Team.",
            }
            st.info(guidance[view])
            if mode == "Camera snapshots":
                source = st.camera_input(f"Capture {view}", key=f"camera_{view}")
            else:
                source = st.file_uploader(
                    f"Upload {view} photo", type=["jpg", "jpeg", "png"], key=f"upload_{view}"
                )
            if source is not None:
                try:
                    candidate = load_capture(source.getvalue())
                    st.image(candidate, width=340)
                    reviewed = st.checkbox(
                        f"I confirm this shows the {view} view of the same person.",
                        key=f"review_{view}_{source.file_id}",
                    )
                    if st.button("Check & save this view", type="primary", disabled=not reviewed):
                        with st.spinner("Checking photo quality…"):
                            record = assess_capture(candidate, view)
                        if record["issues"]:
                            for issue in record["issues"]:
                                st.error(issue)
                        else:
                            record["reviewed"] = True
                            save_capture(session, view, record)
                            st.rerun()
                except (ValueError, RuntimeError, OSError) as exc:
                    st.error(str(exc))
        st.caption(
            "Front: landmark analysis. Other angles: quality checks + your visual confirmation. "
            "Orientation and identity are not automatically verified."
        )
    if session["captures"]:
        for col, view in zip(st.columns(4), VIEWS, strict=True):
            with col:
                if view in session["captures"]:
                    st.image(
                        session["captures"][view]["image"],
                        caption=f"✓ {view.title()}",
                        width="stretch",
                    )
                    if st.button("Retake", key=f"retake_{view}"):
                        del session["captures"][view]
                        invalidate(session)
                        st.rerun()
                else:
                    st.info(f"{view.title()} · waiting")
    st.button(
        "Continue to preferences →",
        type="primary",
        disabled=not status["scan_complete"],
        on_click=go,
        args=("02  Your preferences",),
    )

elif page == "02  Your preferences":
    title(
        "02 / MAKE IT PERSONAL",
        "What’s your kind of cut?",
        "A few details help us narrow the options. Review the sides and back as you answer.",
    )
    if not status["scan_complete"]:
        st.info("Review all four views, including a usable front scan, to continue.")
        st.stop()
    with st.expander("Review your four angles"):
        for col, view in zip(st.columns(4), VIEWS, strict=True):
            col.image(session["captures"][view]["image"], caption=view.title(), width="stretch")
    with st.form("questionnaire"):
        a, b, c = st.columns(3)
        length = a.selectbox(
            "Desired length", ["any", "very_short", "short", "medium", "long"], key="pref_length"
        )
        maintenance = b.selectbox(
            "Daily maintenance", ["any", "low", "medium", "high"], key="pref_maintenance"
        )
        texture = c.selectbox(
            "Your hair texture", ["any", "straight", "wavy", "curly", "coily"], key="pref_texture"
        )
        a, b, c = st.columns(3)
        category = a.selectbox(
            "Style direction",
            ["any", "classic", "modern", "natural", "relaxed", "statement"],
            key="pref_category",
        )
        fade = b.selectbox("Fade preference", ["any", "yes", "no"], key="pref_fade")
        fade_height = c.selectbox(
            "Fade height / transition",
            ["none", "taper", "low", "mid", "high"],
            key="pref_transition",
        )
        st.markdown("#### Lengths & finishing touches")
        a, b, c = st.columns(3)
        base = a.number_input("Shortest side / back length (mm)", 0, 100, 9, key="pref_base")
        blend = b.selectbox("Blend preference", ["soft", "standard", "sharp"], key="pref_blend")
        blend_guard = c.selectbox(
            "Blend guard", ["unspecified", "#1", "#2", "#3", "#4"], key="pref_guard"
        )
        a, b, c = st.columns(3)
        cut_top = a.checkbox("Trim the top", value=False, key="pref_cut_top")
        top_length = a.number_input("Top length if trimmed (mm)", 1, 300, 50, key="pref_top_length")
        sideburn = b.selectbox(
            "Sideburns", ["natural", "short", "keep current"], key="pref_sideburn"
        )
        neckline = c.selectbox("Neckline", ["natural", "rounded", "square"], key="pref_neckline")
        regions = st.multiselect(
            "Areas to avoid",
            ["front", "left_side", "right_side", "rear", "crown", "ears", "neck"],
            key="pref_regions",
        )
        preserve = st.text_input(
            "Anything to preserve?",
            max_chars=500,
            key="pref_preserve",
            placeholder="A longer fringe, a part, a curl pattern…",
        )
        observations = st.text_area(
            "Notes from your side & rear photos",
            max_chars=1000,
            key="pref_notes",
            placeholder="Example: keep more length behind my left ear.",
        )
        if st.form_submit_button("Save preferences & find styles →", type="primary"):
            if (fade == "no" and fade_height != "none") or (
                fade == "yes" and fade_height == "none"
            ):
                st.error("Match the fade preference and transition before saving.")
            else:
                update_preferences(
                    session,
                    {
                        "desired_length": length,
                        "maintenance": maintenance,
                        "texture": texture,
                        "category": category,
                        "fade": fade,
                        "fade_height": fade_height,
                        "base_length_mm": base,
                        "base_guard": f"{base} mm",
                        "blend_guard": blend_guard,
                        "blend": blend,
                        "cut_top": cut_top,
                        "top_length_mm": top_length,
                        "sideburn": sideburn,
                        "neckline": neckline,
                        "no_cut_regions": regions,
                        "preserve": preserve,
                        "view_observations": observations,
                    },
                )
                st.success("Preferences saved. Open Style studio to compare your results.")
    st.button(
        "Open Style studio →",
        disabled=session["preferences"] is None,
        on_click=go,
        args=("03  Style studio",),
    )

elif page == "03  Style studio":
    title(
        "03 / YOUR STYLE EDIT",
        "A few good directions.",
        "Compare suggestions, choose a look, and review your handoff. Style is personal.",
    )
    if not status["scan_complete"] or session["preferences"] is None:
        st.info("Finish the four-view scan and save your preferences first.")
        st.stop()
    front = session["captures"]["front"]
    shape = classify_face_shape(front["measurements"])
    prefs = session["preferences"]
    ranked = rank_hairstyles(
        load_catalog(),
        shape,
        Preferences(
            **{
                k: prefs[k]
                for k in ("desired_length", "maintenance", "fade", "texture", "category")
            }
        ),
    )
    a, b, c = st.columns(3)
    a.metric("Approximate face shape", shape.label.title())
    b.metric("Reviewed views", "4 / 4")
    c.metric("Styles to explore", str(len(ranked)))
    if shape.ambiguous:
        st.caption(f"Your proportions are also close to {shape.runner_up}.")
    with st.expander("Why these suggestions?"):
        st.write(
            "Front-view proportions drive the estimate. Other views inform your review notes, "
            "which go to the next team; they do not provide 3D measurements or change scores."
        )
        st.write(list(shape.reasons))
    available_references = sum(style_image_path(rec.style.id) is not None for rec in ranked)
    if available_references < len(ranked):
        st.warning(
            f"{available_references} of {len(ranked)} reference images are available locally. "
            "The remaining image assets still need to be saved. Recommendations remain usable."
        )
    for col, rec in zip(st.columns(3), ranked[:3], strict=True):
        with col, st.container(border=True):
            reference = style_image_path(rec.style.id)
            if reference:
                st.image(str(reference), caption=rec.style.name, width="stretch")
            st.caption(f"STYLE FIT · {rec.score:.0f} / 100")
            st.subheader(rec.style.name)
            st.write(rec.style.description)
            for reason in rec.reasons:
                st.caption(f"✓ {reason}")
            with st.expander("Score breakdown"):
                st.json(rec.breakdown)
    st.caption(
        "Hairstyle reference images generated with Google Nano Banana 2. "
        "Fictional models; examples of styles, not predictions of your appearance."
    )
    with st.expander(f"Explore all {len(ranked)} hairstyle references"):
        for start in range(0, len(ranked), 3):
            for col, rec in zip(st.columns(3), ranked[start : start + 3], strict=False):
                with col:
                    reference = style_image_path(rec.style.id)
                    if reference:
                        st.image(str(reference), caption=rec.style.name, width="stretch")
                    st.markdown(f"**{rec.style.name}**")
                    st.caption(rec.style.description)
    by_id = {r.style.id: r.style for r in ranked}
    selected_id = st.selectbox(
        "Choose any style",
        list(by_id),
        format_func=lambda value: by_id[value].name,
        key="selected_style",
    )
    style = by_id[selected_id]
    reference = style_image_path(style.id)
    if reference:
        with st.expander(f"Selected style reference · {style.name}", expanded=True):
            st.image(str(reference), width=420)
            st.caption(
                "Nano Banana 2 generated reference. Your photo-based silhouette below is a "
                "separate illustrative preview; neither specifies a robot cutting path."
            )
    controls, picture = st.columns([1, 1.6], gap="large")
    with controls:
        st.subheader("Your photo-based preview")
        st.caption(
            "Illustrative front overlay. Existing hair is not removed; "
            "this is not a calibrated AR map."
        )
        color = st.color_picker("Hair color", "#342c25", key="preview_color")
        scale = st.slider("Silhouette size", 0.75, 1.35, 1.0, 0.05, key="preview_scale")
        x = st.slider("Horizontal position", -0.1, 0.1, 0.0, 0.01, key="preview_x")
        y = st.slider("Vertical position", -0.1, 0.1, 0.0, 0.01, key="preview_y")
        settings = {"color": color, "scale": scale, "x_offset": x, "y_offset": y}
        plan = create_plan(session, style, settings)
        st.markdown("**Your selected lengths**")
        st.write(f"Sides / back: {prefs['base_length_mm']} mm · Transition: {prefs['fade_height']}")
        st.write(
            f"Top: {prefs['top_length_mm']} mm" if prefs["cut_top"] else "Top: keep current length"
        )
        st.caption(
            "Questionnaire lengths override catalog defaults. "
            "The silhouette shows the style family."
        )
    with picture:
        preview = render_preview(front["image"], front["landmarks"], style, **settings)
        st.image(preview, caption=style.name, width="stretch")
        buffer = io.BytesIO()
        preview.save(buffer, format="PNG")
        st.download_button(
            "Save preview", buffer.getvalue(), f"{plan['plan_id']}-preview.png", "image/png"
        )
    with st.container(border=True):
        st.subheader("Ready to hand this over?")
        st.caption(f"Plan {plan['plan_id']} · Vision mapping and IK validation are still pending.")
        st.write(
            "Approval records your style choice for the team. "
            "Hardware execution is a separate step."
        )
        if st.button(
            "Approve this style & preview", type="primary", key=f"approve_{plan['plan_id']}"
        ):
            approve_plan(session, plan["plan_id"])
        if session["approval"]:
            st.success("Selection approved. Your handoff uses the same plan ID as this preview.")
            payload = export_handoff(session)
            st.download_button(
                "Download team handoff",
                json.dumps(payload, indent=2),
                f"{plan['plan_id']}.json",
                "application/json",
            )
            with st.expander("Inspect handoff"):
                st.json(payload)

else:
    title(
        "04 / INTEGRATION DESK",
        "One team. One plan.",
        "Your demo sequence, end-to-end checks, handoff matrix, and issue template in one place.",
    )
    a, b, c = st.columns(3)
    a.metric("Scan coverage", f"{sum(status['coverage'][v] for v in VIEWS)} / 4")
    b.metric("User selection", "Approved" if session["approval"] else "Pending")
    c.metric("Robot / live tracking", "Not connected")
    if session["plan"]:
        st.code(session["plan"]["plan_id"])
    tabs = st.tabs(["Readiness", "Demo runbook", "Team handoffs", "Issue report", "Contracts"])
    docs = ROOT / "docs" / "team_package"
    with tabs[0]:
        st.caption(
            "Manual team sign-offs. Checking a box records your observation; "
            "it does not verify hardware."
        )
        checks = {}
        revision = session["plan"]["plan_id"] if session["plan"] else session["session_id"]
        for line in (docs / "END_TO_END_TEST.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                st.markdown(f"#### {line[3:]}")
            elif line.startswith("- "):
                checks[line[2:]] = st.checkbox(line[2:], key=f"check_{revision}_{len(checks)}")
            elif line.strip() and not line.startswith("# "):
                st.markdown(line)
        report = {
            "session_id": session["session_id"],
            "plan_id": session["plan"]["plan_id"] if session["plan"] else None,
            "verification_method": "manual_operator_report",
            "checks": checks,
        }
        st.download_button(
            "Export readiness report",
            json.dumps(report, indent=2),
            "readiness.json",
            "application/json",
        )
    with tabs[1]:
        st.markdown((docs / "DEMO_SEQUENCE.md").read_text(encoding="utf-8"))
    with tabs[2]:
        st.markdown((docs / "TEAM_HANDOFF_MATRIX.md").read_text(encoding="utf-8"))
    with tabs[3]:
        fields = {
            "Problem": st.text_input("Problem", key="issue_problem"),
            "Team / component": st.selectbox(
                "Component",
                ["App", "Camera node", "Vision", "IK/planning", "Main controller", "Hardware"],
                key="issue_component",
            ),
        }
        for name in [
            "Expected",
            "Actual",
            "Network addresses",
            "Reproduction steps",
            "Relevant logs",
            "Exact payload sent",
            "Exact response received",
        ]:
            fields[name] = st.text_area(name, key=f"issue_{name}")
        fields["Safety impact"] = st.selectbox(
            "Safety impact",
            ["none", "motion blocked", "incorrect target", "unexpected motion", "E-stop required"],
            key="issue_safety",
        )
        fields["session_id / plan_id"] = (
            session["session_id"]
            + " / "
            + (session["plan"]["plan_id"] if session["plan"] else "pending")
        )
        report = "# Integration issue\n\n" + "\n\n".join(f"## {k}\n{v}" for k, v in fields.items())
        st.download_button("Download issue report", report, "integration-issue.md", "text/markdown")
        with st.expander("Original issue template"):
            st.markdown((docs / "ISSUE_TEMPLATE.md").read_text(encoding="utf-8"))
    with tabs[4]:
        st.info(
            "Local handoffs are draft app records. Live pose, head mapping, and validated paths "
            "must come from Vision / Planning. No controller commands are sent by this app."
        )
        st.json(status)
        st.download_button(
            "Download app handoff schema",
            json.dumps(HANDOFF_SCHEMA, indent=2),
            "trimsync-app-draft-1.schema.json",
            "application/schema+json",
        )
        with st.expander("Shared API contract · package v1"):
            st.markdown((docs / "API_CONTRACT.md").read_text(encoding="utf-8"))

st.divider()
st.caption(
    "TRIMSYNC · Designed around you. "
    "Recommendations are stylistic suggestions, not objective judgments."
)
