# Architecture

## Pipeline

```text
camera snapshot / uploaded image / explicit demo fixture
                         |
                         v
              OpenCV decode + RGB normalization
                         |
                         v
           MediaPipe Face Landmarker
                         |
                         v
       selected 2D normalized landmarks
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
               user selects a style
                         |
                         v
     validated, descriptive robot-output JSON
```

## Components

- `vision.py` decodes camera/upload bytes with OpenCV, owns MediaPipe
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
- `robot_contract.py` creates and validates a JSON document. There is no socket,
  serial port, ROS publisher, motor driver, trajectory, or cutting code.

## Coordinate and measurement choices

The task returns normalized `(x, y, z)` landmarks. The MVP uses 2D Euclidean
distance for head-on portraits and divides dimensions by cheekbone width. This
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

## Extension points

Replace the placeholder renderer with licensed transparent PNGs by implementing
the same `render_preview(image, landmarks, style, ...) -> PIL.Image` interface.
Add or tune catalog entries without changing the ranking code. Future research
could calibrate heuristics on consented, diverse data, but the competition MVP
does not collect or train on faces.
