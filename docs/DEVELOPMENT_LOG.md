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

This section is updated after each local validation pass with exact commands,
results, and any fixes.

