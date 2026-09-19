# Safety and limitations

## Recommendation, not judgment

Hairstyles are subjective and culturally situated. The ranking is a design aid,
not an objective assessment of attractiveness, gender, professionalism, or
identity. The UI says this plainly and lets the user override every suggestion.

## Vision uncertainty

Measurements can shift with camera angle, lens distortion, expression,
distance, hats, glasses, facial hair, bangs, occlusion, background clutter, and
uneven lighting. A single image cannot reliably recover true 3D skull geometry.
The app therefore presents approximate labels, ratios, and ambiguity rather
than a diagnosis. It rejects obvious pose asymmetry but does not guarantee a
valid capture.

## Bias and inclusion

Face landmark systems may perform differently across skin tones, ages, facial
features, hair textures, disabilities, and presentation. Face-shape categories
also simplify a continuous and diverse range of appearances. The rule-based
catalog cannot encode every personal, religious, cultural, accessibility, or
hair-health consideration. Users should be able to choose any style regardless
of the ranking.

## Privacy

The app processes four images (optionally five) in server session memory and
does not intentionally persist them. Exported metadata excludes the photos and
landmarks. User-entered notes or issue logs can still contain personal data.
Deployments must still document their hosting, logs, retention, analytics, and
network behavior. Do not collect faces without informed consent. Demo operators
should prefer local processing and close the browser session after use.

## Preview limitations

Nano Banana 2 reference portraits are AI-generated examples on fictional adults,
not photographs of customers or predictions on the scanned person. No scan
photos were provided to Gemini when producing the catalog. The runtime app
loads those images locally; it does not generate personalized Gemini images.
The example model's characteristics must not be used to restrict style choice.

The overlay is an illustrative silhouette, not a photorealistic prediction. It
does not model current hair, curls, density, scalp, hairline, growth direction,
color blending, styling products, or how a cut will grow out. Replace it only
with properly licensed assets and keep the same caveat visible.

## Hard separation from physical cutting

The exported JSON is a proposal for a separate subsystem and is generated only
after the user explicitly selects a style. It must never be interpreted as an
actuation command. It contains no coordinates, toolpaths, timing, speed, force,
blade state, or safety-interlock control.

Any physical robot requires an independent hazard analysis, guarded tools,
collision detection, redundant emergency stops, verified perception, motion
limits, human supervision, informed consent, and applicable regulatory and
professional review. This repository does not claim to make robotic haircutting
safe.

## Four-view and integration boundaries

Four photos do not establish a calibrated 3D head model. Side/rear orientation
and same-subject claims rely on operator confirmation. Basic brightness and
sharpness tests cannot detect all blur, occlusion, poor framing, or misleading
images. Only the front view drives automatic face-shape scoring; other views
support human review. No hair density, scalp condition, health, or identity
inference is made. Millimeter values are requested lengths, not vision-derived
physical measurements.

The UI separates synthetic demo captures from real sessions, reports no live
tracking/controller connection, and always marks the draft non-executable.
Approval is tied to the current plan and invalidates when its inputs change.
It approves a style proposal only, not physical robot operation. Manual
readiness checkboxes and the supplied runbook do not implement hardware tests,
safety interlocks, or a validated robot path. See [Integration](INTEGRATION.md).
