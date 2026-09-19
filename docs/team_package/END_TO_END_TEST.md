# End-to-End Integration Test

Run this in order.

## Stage 1 — Networks
- Main controller online.
- Camera node online.
- App computer can reach both.
- Vision computer can reach both.

## Stage 2 — Main robot
- PCA detected.
- Outputs enabled only intentionally.
- Manual sliders move correct joints.
- Calibration values load.
- Safe Home works.
- E-stop works.
- Gyro works.

## Stage 3 — Camera node
- `/health` returns camera ready.
- `/camera.jpg` returns valid current JPEG.
- Stable image over repeated requests.

## Stage 4 — Vision
- Head detected.
- Head pose updates.
- Confidence reasonable.
- Lost tracking is detectable.
- Main controller receives `/api/vision/head`.

## Stage 5 — App
- Creates session.
- Questionnaire completed.
- Scan status shown.
- Haircut chosen.
- Plan ID generated.
- AR preview displayed.
- User approval stored.

## Stage 6 — Plan consistency
Confirm one plan ID is used by:
- haircut plan
- AR overlay
- validated robot path

## Stage 7 — Dry-run robot path
NO person in workspace.

- Send path.
- Arm Auto.
- Start.
- Verify correct trajectory.
- Test stop.
- Test tracking loss.

## Stage 8 — Mannequin
Only after all previous stages pass.

Validate:
- reachability
- clearance
- tool orientation
- replanning
- camera occlusion
- E-stop
- head-motion simulation

Human-contact automation should not be the first physical Auto test.
