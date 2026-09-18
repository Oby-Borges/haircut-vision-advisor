# Development log

## 2026-09-18 — Scope and safety boundary

- Established an MVP pipeline from browser image capture to explainable
  recommendations and a programmatic silhouette preview.
- Deliberately excluded actuator, trajectory, blade, motor, force, and physical
  safety-control code.
- Chose a data-only JSON contract gated by explicit user selection.
- Chose Python 3.11/3.12 because the local default Python 3.14 is newer than the
  supported MediaPipe wheel range used by this project.

## 2026-09-18 — Design decisions

- Selected MediaPipe Tasks Face Landmarker instead of the legacy Face Mesh
  Solutions API.
- Used normalized distances and transparent rules rather than training a custom
  classifier on an unverified face-shape dataset.
- Put styles in JSON so competition teams can tune content without code edits.
- Designed the preview from generated vector-like shapes to avoid asset license
  ambiguity.

## Validation record

### Python 3.12 full environment

- Provisioned a project-local Python 3.12.14 environment because the host's
  Python 3.14 is outside the MediaPipe support range selected by the project.
- Installed the complete editable project, including MediaPipe 0.10.35 and
  OpenCV.
- Downloaded Google's official 3,758,596-byte Face Landmarker task model. The
  observed SHA-256 was
  `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`.
- Exercised the real adapter on a bundled local test portrait: 478 landmarks
  returned, with a low-confidence/approximate shape result as expected.
- Ran `pytest --cov=haircut_vision --cov-report=term-missing`: 21 passed, 84%
  line coverage. The model smoke test is recorded separately and intentionally
  does not commit the third-party portrait.
- Ran `ruff check .`: all checks passed.

### Browser walkthrough and fixes

- Launched Streamlit and completed the demo-fixture flow through measurement,
  ranking, preview, explicit selection, JSON generation, and schema download.
- The first visual pass exposed light-background/dark-theme contrast problems;
  added an explicit light theme.
- Added `?demo=1` as a presentation-safe path that bypasses camera permission
  prompts while clearly labeling the synthetic input.
- Replaced Streamlit's removed `use_container_width` argument with the current
  `width="stretch"` API after the server emitted deprecation warnings.
