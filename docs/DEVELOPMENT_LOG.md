# Development log

## 2026-09-19 — Nano Banana hairstyle reference library

- Used the user's requested Google Nano Banana 2 through the signed-in Gemini
  Images browser interface. Generated one square 1024×1024 portrait for each of
  the 15 catalog styles; no scanned/user face photos were uploaded.
- Kept framing, studio lighting, ivory background and green clothing consistent.
  Inspected every downloaded image for the intended hairstyle and complete hair
  framing. Stored individual JPEGs locally, not remote image links.
- Browser downloads initially remained pending because Edge asked Open/Save As.
  The user completed the save choices; no browser security settings were changed.
- Added images to top recommendation cards, a full ranked gallery, and selected
  style references. Retained the independent photo-based silhouette and unchanged
  approval/robot safety contract. Added clear fictional/AI-generated labeling.
- Recorded exact prompts and provider in `assets/hairstyle_image_prompts.json`;
  added asset documentation, catalog completeness checks, safe path handling,
  and rendered image assertions in the app walkthrough.
- A test initially queried Streamlit's protobuf field `imgs` as the element
  type; corrected it to `image` after inspecting the actual AppTest tree.
- Validation: 36 tests passed, 86% package line coverage, Ruff passed, and
  `git diff --check` passed. The live Edge demo rendered all 15 gallery images,
  three recommendation images, the selected reference, and the photo overlay
  with successful image loads and nonzero dimensions. Browser screenshot capture
  timed out; individual source images were visually reviewed locally instead.
- Left the local Streamlit app running and the full reference gallery open.

## 2026-09-19 — TrimSync integration workspace and four-view workflow

- Reviewed the supplied Integration Team files plus shared API, App Team
  questionnaire/output/mapping, and Vision output notes. Imported five reference
  documents without modifying the originals in Documents/VTHacks.
- Replaced the single-page demo with Capture, Preferences, Style studio, and
  Integration screens and a cream/forest-green responsive visual theme.
- Added four distinct reviewed photo slots (front/left/right/rear), optional
  crown, camera/upload choices, brightness/detail/size checks, duplicate checks,
  and original synthetic diagrams. Front uses real MediaPipe for real photos;
  other orientations require manual confirmation. No fictitious 3D model.
- Fixed rectangular-image ratio distortion by converting normalized landmarks
  to pixel coordinates before measurement; added a regression test.
- Added plan fingerprints, approval invalidation and schema-validated draft
  handoffs. Keep-top exports null; head-frame and mapping readiness remain false;
  planning remains non-executable. Legacy descriptive contract API retained.
- Turned team readiness checks into plan-scoped manual reports, added issue
  downloads and source runbook/ownership/API tabs. No controller requests.
- Preserved form and preview widget state across navigation; tested that an
  approved unchanged plan stays approved and changes invalidate it.
- Validation: 30 tests passed; 86% package line coverage; Ruff passed.
  A new rectangular fixture initially failed the quality gate because it was
  blank; replaced it with deterministic image detail for the geometry test.
- Browser review found CSS for editorial labels also shrinking nested heading
  text; narrowed the selector to direct children.
- Browser walkthrough completed the four-view demo, saved preferences, ranked
  results, silhouette, explicit approval and Integration desk. Found Windows'
  default text encoding garbling source-document em dashes; specified UTF-8
  when reading documents and added an assertion for the rendered headings.
- Re-ran the real MediaPipe capture pipeline on Matplotlib's installed local
  Grace Hopper sample (not copied into this repository): 478 landmarks on a
  512×600 image, no capture-quality issues, aspect-correct length ratio 1.1211.
  Optional library font-cache/telemetry warnings did not prevent inference.
  Live webcam permissions and a real person's complete four-angle session were
  not exercised. Local Streamlit health endpoint returned `ok`.

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
