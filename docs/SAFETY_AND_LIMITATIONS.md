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

The app processes one image in memory and does not intentionally persist it.
Deployments must still document their hosting, logs, retention, analytics, and
network behavior. Do not collect faces without informed consent. Demo operators
should prefer local processing and close the browser session after use.

## Preview limitations

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

