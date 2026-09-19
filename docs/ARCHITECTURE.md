# Architecture

## Pipeline

```text
session -> front / left / right / rear photos (optional crown)
                         |
                         v
           guarded decode + EXIF + quality checks + manual view confirmation
                         |
                         v
           front MediaPipe Face Landmarker
                         |
                         v
       selected 2D landmarks converted to pixel coordinates
                         |
                         v
   face length + forehead/cheek/jaw widths
                         |
                         v
 transparent face-shape heuristic + ambiguity
                         |
                         +-----------------------+
                         |                       |
                         v                       v
                preference form          preview anchor
                         |                       |
                         v                       v
        weighted catalog scoring   programmatic silhouette
                         |
                         v
               user selects a style -> plan ID -> explicit approval
                         |
                         v
     validated, non-executable TrimSync draft JSON
```

## Components

- `scan.py` decodes and normalizes images, checks size/lighting/detail, and
  creates reviewable capture records with pixel digests. `vision.py` owns MediaPipe
  initialization, and converts its output to a plain tuple list. Native vision
  dependencies are imported lazily so catalog and heuristic tests remain fast.
- `measurements.py` contains landmark indices and rotation-tolerant Euclidean
  measurements normalized by cheekbone width.
- `face_shape.py` scores all six labels rather than hiding the decision behind
  a model. It returns the top label, confidence, runner-up, and human-readable
  evidence. This is a style convenience label, not biometric identity data.
- `recommend.py` weights shape compatibility and explicit preferences. The
  catalog is data in `assets/hairstyles.json`, not hard-coded UI logic.
- `preview.py` draws original, deliberately stylized silhouettes aligned to the
  detected facial bounds. It does not synthesize realistic hair.
- `session.py` gates four-view completeness and tracks preferences, plan IDs,
  and explicit approval. `handoff.py` validates the draft app JSON schema and
  cross-record identifiers. `robot_contract.py` retains the legacy v1
  descriptive contract for existing consumers. There is no socket,
  serial port, ROS publisher, motor driver, trajectory, or cutting code.

## Coordinate and measurement choices

The task returns normalized `(x, y, z)` landmarks. The capture pipeline multiplies
x by image width and y by image height before measuring 2D Euclidean distances
for head-on portraits, then divides dimensions by cheekbone width. This
makes ratios independent of image resolution. Strong head rotation invalidates
the geometric assumptions; the UI reports an approximate yaw asymmetry check
and asks the user for a centered retake when it is large.

Selected MediaPipe landmark indices:

| Purpose | Indices |
| --- | --- |
| face top to chin | 10, 152 |
| forehead width | 103, 332 |
| cheekbone width | 234, 454 |
| jaw width | 172, 397 |
| nose center / facial symmetry | 1, 234, 454 |

These anchors are pragmatic approximations, not anatomical measurements.

## Multi-view state and approval

The four required views are front, left, right, rear. Crown is optional.
Side/rear/crown orientation and same-person status require manual confirmation;
there is no automatic orientation or identity verification. Identical decoded
photos cannot fill multiple slots. Transformed duplicates are not detected.
Other views support review notes, not automatic 3D reconstruction or scores.

Plan IDs hash the session, style, saved preferences, capture digests, and preview
settings. Identical inputs preserve approval across navigation. A removed or
replaced photo, changed saved preferences, style, or preview clears approval.
The preview, planning placeholder and approval share one plan ID. The planning
placeholder is always awaiting Vision/IK and non-executable.

The Integration desk exposes the supplied team's checklist, runbook, handoff
matrix, issue template, and shared contract. Readiness boxes are manual reports
scoped to plan ID (or session before a plan), not hardware verification.
Session data is held in memory, not persisted to a database. Downloaded handoffs
do not contain photos or landmarks. See [Integration](INTEGRATION.md).

## Extension points

Replace the placeholder renderer with licensed transparent PNGs by implementing
the same `render_preview(image, landmarks, style, ...) -> PIL.Image` interface.
Add or tune catalog entries without changing the ranking code. Future research
could calibrate heuristics on consented, diverse data, but the competition MVP
does not collect or train on faces.
