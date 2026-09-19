# Hairstyle reference image set

Provider: Google Gemini Images, UI labeled **Nano Banana 2**.
Creation date: 2026-09-19. One individual generation per catalog style.
Exact prompts: `assets/hairstyle_image_prompts.json`; concatenate `base_prompt`
and the corresponding `styles[style_id]` value. Regeneration is not deterministic.

The images use fictional adults, a warm ivory background, soft studio lighting,
and a consistent head-and-shoulders composition. Longer hair uses a wider frame
to preserve the visible ends. Skin tones, hair textures and presentation vary;
the example model is not an eligibility rule for that haircut.

## Use in the app

Each `assets/hairstyle_images/<style_id>.jpg` is loaded locally by
`style_images.py`. The top recommendations, all-styles gallery and selected-style
reference use these files. There is no runtime Gemini connection, API key,
remote image hotlink, or upload of the user's scanned photos to Gemini.

References are illustrative style examples, not personalized try-ons, exact
millimeter specifications, actual customers, or objective attractiveness
claims. They do not replace the existing front-photo silhouette renderer or
change recommendation scores, safety checks, approvals, or robot contracts.
The image may depict grooming details not encoded in the catalog parameters.
No claim of exclusive copyright or guaranteed third-party rights clearance is
made for generated imagery; preserve the AI-generated disclosure when reused.

## Replacement and validation

To replace a style image, keep its exact catalog ID as the filename and retain
the original non-destructively until review. Use a square JPEG of at least
512×512 pixels and keep the entire hair silhouette visible. Update the prompt
record/provenance when changing the source. Tests verify every catalog entry
has a matching readable image and recorded prompt; unknown image IDs fail
safely without accessing files outside the asset directory.
