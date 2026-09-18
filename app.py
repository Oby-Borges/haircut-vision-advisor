"""Streamlit competition demo for Haircut Vision Advisor."""

from __future__ import annotations

import hashlib
import io
import json
import sys
from pathlib import Path

import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from haircut_vision.catalog import load_catalog  # noqa: E402
from haircut_vision.demo_fixture import demo_portrait, synthetic_landmarks  # noqa: E402
from haircut_vision.face_shape import classify_face_shape  # noqa: E402
from haircut_vision.measurements import extract_measurements  # noqa: E402
from haircut_vision.preview import render_preview  # noqa: E402
from haircut_vision.recommend import rank_hairstyles  # noqa: E402
from haircut_vision.robot_contract import (  # noqa: E402
    ROBOT_OUTPUT_SCHEMA,
    build_robot_output,
)
from haircut_vision.types import Preferences  # noqa: E402
from haircut_vision.vision import VisionUnavailableError, detect_landmarks  # noqa: E402

st.set_page_config(page_title="Haircut Vision Advisor", page_icon="✂️", layout="wide")
st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(145deg, #f6f2ea 0%, #eef3f6 55%, #e8edf3 100%); }
      .hero { padding: 2.1rem 2.3rem; border-radius: 24px; color: white;
        background: linear-gradient(120deg, #17212b, #304b5f 65%, #416879);
        box-shadow: 0 15px 40px rgba(25,40,55,.18); margin-bottom: 1.2rem; }
      .hero h1 { font-size: clamp(2rem, 4vw, 3.4rem); margin: 0 0 .35rem; letter-spacing: -.04em; }
      .hero p { color: #dce8ed; max-width: 800px; margin: 0; font-size: 1.06rem; }
      .eyebrow { color: #eebd70; text-transform: uppercase; font-size: .78rem;
        font-weight: 800; letter-spacing: .16em; margin-bottom: .5rem; }
      .notice { border-left: 5px solid #d6923e; background: #fff8e9; color: #45341e;
        border-radius: 8px; padding: .8rem 1rem; margin: .7rem 0 1rem; }
      .score { font-size: 2rem; font-weight: 800; color: #274b5b; line-height: 1; }
      [data-testid="stMetricValue"] { color: #274b5b; }
      div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,.72); border-radius: 14px; }
      .footer-note { color: #60717a; font-size: .84rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Competition prototype · explainable vision</div>
      <h1>Find a haircut direction that feels like you.</h1>
      <p>Analyze approximate face proportions, add your preferences, compare transparent
      recommendations, and preview original silhouette overlays—without sending any command
      to cutting hardware.</p>
    </div>
    <div class="notice"><strong>Style, not judgment.</strong> Recommendations are subjective
    starting points—not attractiveness ratings, guarantees, or professional advice. You can
    choose any style regardless of rank.</div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def catalog():
    return load_catalog()


def image_from_input():
    st.subheader("1 · Choose an image")
    mode = st.radio(
        "Image source",
        ["Camera snapshot", "Upload image", "Demo fixture"],
        horizontal=True,
        help="Images are processed in memory; this app does not intentionally save them.",
    )
    if mode == "Camera snapshot":
        source = st.camera_input("Center your face, look forward, and use even lighting")
    elif mode == "Upload image":
        source = st.file_uploader("Upload a centered JPG or PNG", type=["jpg", "jpeg", "png"])
    else:
        st.caption(
            "The demo fixture is an original illustration with synthetic landmarks—"
            "not a real face scan."
        )
        return demo_portrait(), "demo", True
    if source is None:
        return None, None, False
    raw = source.getvalue()
    return Image.open(io.BytesIO(raw)).convert("RGB"), hashlib.sha256(raw).hexdigest(), False


image, image_key, is_demo = image_from_input()
if image is None:
    st.info("Choose a camera snapshot, upload, or demo fixture to begin.")
    st.stop()

left, right = st.columns([1, 1], gap="large")
with left:
    st.image(image, caption="Input image", use_container_width=True)
with right:
    st.subheader("2 · Analyze proportions")
    st.write("A near-frontal pose works best. No identity recognition is performed.")
    analyze = st.button("Analyze face", type="primary", use_container_width=True)

if analyze or st.session_state.get("image_key") == image_key:
    try:
        if st.session_state.get("image_key") != image_key:
            landmarks = synthetic_landmarks() if is_demo else detect_landmarks(image)
            measurements = extract_measurements(landmarks)
            result = classify_face_shape(measurements)
            st.session_state.update(
                image_key=image_key,
                source_image=image,
                landmarks=landmarks,
                measurements=measurements,
                shape_result=result,
            )
    except (VisionUnavailableError, ValueError) as exc:
        st.error(str(exc))
        st.stop()
else:
    st.stop()

measurements = st.session_state.measurements
shape_result = st.session_state.shape_result
landmarks = st.session_state.landmarks

st.divider()
st.subheader("Your approximate geometry")
metric_columns = st.columns(4)
metric_columns[0].metric("Estimated shape", shape_result.label.title())
metric_columns[1].metric("Length ÷ width", f"{measurements.length_to_width:.2f}")
metric_columns[2].metric("Forehead ÷ cheeks", f"{measurements.forehead_to_cheek:.2f}")
metric_columns[3].metric("Jaw ÷ cheeks", f"{measurements.jaw_to_cheek:.2f}")

if measurements.yaw_asymmetry > 0.14:
    st.warning("The pose appears turned. Retake facing forward for more stable proportions.")
elif shape_result.ambiguous:
    st.info(f"This is a close call between {shape_result.label} and {shape_result.runner_up}.")

with st.expander("How the estimate was made"):
    st.write(
        "These deterministic rules use distances between selected landmarks; "
        "scores are heuristic fit, not probability."
    )
    st.bar_chart(shape_result.scores, horizontal=True)
    for reason in shape_result.reasons:
        st.write(f"• {reason}")

st.divider()
st.subheader("3 · Tell us what you want")
with st.form("preferences"):
    cols = st.columns(5)
    desired_length = cols[0].selectbox(
        "Length",
        ["any", "very_short", "short", "medium", "long"],
        format_func=lambda x: x.replace("_", " ").title(),
    )
    maintenance = cols[1].selectbox(
        "Maintenance", ["any", "low", "medium", "high"], format_func=str.title
    )
    fade = cols[2].selectbox("Fade", ["any", "yes", "no"], format_func=str.title)
    texture = cols[3].selectbox(
        "Texture", ["any", "straight", "wavy", "curly", "coily"], format_func=str.title
    )
    category = cols[4].selectbox(
        "Category",
        ["any", "classic", "modern", "natural", "relaxed", "statement"],
        format_func=str.title,
    )
    rank_now = st.form_submit_button("Rank styles", type="primary", use_container_width=True)

preferences = Preferences(desired_length, maintenance, fade, texture, category)
recommendations = rank_hairstyles(catalog(), shape_result, preferences)
if rank_now or "recommendations" not in st.session_state:
    st.session_state.recommendations = recommendations
else:
    # Streamlit reruns preserve widget values, so keep ranking responsive.
    st.session_state.recommendations = recommendations

top = st.session_state.recommendations[:5]
st.subheader("4 · Compare explainable recommendations")
recommendation_columns = st.columns(3)
for index, recommendation in enumerate(top[:3]):
    with recommendation_columns[index]:
        with st.container(border=True):
            st.markdown(
                f"<div class='score'>{recommendation.score:.0f}</div>", unsafe_allow_html=True
            )
            st.markdown(f"### {recommendation.style.name}")
            st.write(recommendation.style.description)
            st.caption(
                " · ".join(
                    (
                        recommendation.style.length.replace("_", " "),
                        recommendation.style.maintenance + " maintenance",
                        recommendation.style.fade + " fade",
                    )
                )
            )
            for reason in recommendation.reasons[:3]:
                st.write(f"✓ {reason}")

with st.expander("See ranks 4–5 and full score breakdowns"):
    for position, recommendation in enumerate(top, 1):
        st.markdown(f"**{position}. {recommendation.style.name} — {recommendation.score:.0f}/100**")
        st.caption(
            " + ".join(
                f"{key.replace('_', ' ')} {value:g}"
                for key, value in recommendation.breakdown.items()
            )
        )

selected_name = st.radio(
    "Select a style to preview",
    [recommendation.style.name for recommendation in top],
    horizontal=True,
)
selected = next(
    recommendation.style for recommendation in top if recommendation.style.name == selected_name
)

st.divider()
st.subheader("5 · Preview the direction")
control_col, preview_col = st.columns([1, 2], gap="large")
with control_col:
    st.caption("This is a stylized silhouette, not a prediction of the final haircut.")
    hair_color = st.color_picker("Overlay color", "#2a1a12")
    opacity = st.slider("Opacity", 80, 255, 205)
    scale = st.slider("Scale", 0.75, 1.35, 1.0, 0.05)
    x_offset = st.slider("Move left / right", -0.10, 0.10, 0.0, 0.01)
    y_offset = st.slider("Move up / down", -0.10, 0.10, 0.0, 0.01)
with preview_col:
    preview = render_preview(
        image,
        landmarks,
        selected,
        color=hair_color,
        opacity=opacity,
        scale=scale,
        x_offset=x_offset,
        y_offset=y_offset,
    )
    st.image(preview, caption=f"Illustrative preview: {selected.name}", use_container_width=True)

st.divider()
st.subheader("6 · Export a reviewed software contract")
st.warning(
    "This JSON is descriptive metadata only. It is not a safe actuator command, "
    "toolpath, or authorization to cut hair."
)
confirmed = st.checkbox(
    f"I explicitly select {selected.name} and want to generate its descriptive JSON proposal."
)
if confirmed:
    payload = build_robot_output(selected, user_confirmed=True)
    st.json(payload)
    download_columns = st.columns(2)
    download_columns[0].download_button(
        "Download selected-style JSON",
        json.dumps(payload, indent=2),
        file_name=f"{selected.id}_proposal.json",
        mime="application/json",
        use_container_width=True,
    )
    download_columns[1].download_button(
        "Download JSON Schema",
        json.dumps(ROBOT_OUTPUT_SCHEMA, indent=2),
        file_name="haircut_selection_schema.json",
        mime="application/schema+json",
        use_container_width=True,
    )

st.markdown(
    "<p class='footer-note'>No face identity, attractiveness score, actuator output, "
    "or cutting path is produced.</p>",
    unsafe_allow_html=True,
)
