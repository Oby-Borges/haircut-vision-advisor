# TrimSync Software Integration Team

## Package incorporated

The user supplied `Documents/VTHacks/TrimSync_Master_Team_Package_v1`.
`docs/team_package/` contains a snapshot of the four `05_INTEGRATION_TEAM`
documents and `01_SHARED/API_CONTRACT.md`. Original source files were not edited.
The app turns the end-to-end test into manual checkboxes and JSON download,
renders the demo sequence and ownership matrix, and makes the issue template
fillable with current session/plan identifiers. No live endpoint is called.
Questionnaire and scan fields follow the App Team's shared design notes.

## Draft app handoff: `trimsync-app-draft-1`

This is an additive **local application envelope**, not a payload to POST to
`/api/vision/plan`, `/api/vision/overlay`, or `/api/auto/path`. Team agreement and
an adapter are required before any shared service consumes it. The schema is
`HANDOFF_SCHEMA` in `src/haircut_vision/handoff.py` and is downloadable from
Integration → Contracts. Export validates the schema and identifier consistency.

| Field | Meaning |
| --- | --- |
| session_id / subject_id | Random, session-local identifiers; not identity verification |
| plan_id | Fingerprint of captured photos, preferences, style and preview settings |
| style | Selected catalog ID; user may override the top-ranked suggestion |
| preferences | Questionnaire, guards, fade, finishing and side/rear review notes |
| constraints.no_cut_regions | User-requested avoidance regions, not geometric masks |
| proposal | Desired top/side/back mm and fade type; preferences override catalog defaults |
| scan | Four-view completeness, optional crown coverage, synthetic flag |
| preview | Matching plan ID, illustrative silhouette settings, mapping unavailable |
| planning | Matching plan ID, awaiting_vision_and_ik, executable=false |
| approval | Matching plan ID and UTC approval time, not a robot arm/start consent |

`top_length_mm=null` means **keep the current top**, never zero-length cutting.
`scan.confidence=null`, `head_frame_ready=false` and
`head_relative_map_ready=false` are intentional unknown/not-ready values.
No pose, head-relative points, joint values, arm/start commands, or live
tracking status are fabricated. Synthetic sessions retain `scan.synthetic=true`.
Physical consumers must reject synthetic inputs and require their independent
validation; this app does not implement such a consumer.

## Team responsibilities still outstanding

| Owner | Required downstream work |
| --- | --- |
| Camera / Vision | Current camera frames, calibrated head coordinates, pose/confidence/loss, actual scan coverage and mapped overlay |
| Vision / Planning | Convert approved preferences into head-relative map and preserve the plan ID |
| Planning / IK | Reachability, clearance, safe trajectories, independent validation |
| Firmware / Hardware | Calibration, interlocks, stopping, supervised execution controls |
| Integration | Verify shared payload versions, same-plan consistency and staged dry-run/mannequin tests |

The supplied physical demo steps are reference instructions for the responsible
teams, not implemented actions or certified safety procedures. Readiness
checkboxes do not prove any step passed. No readiness action enables motion.
Do not test on a person based on this app's approval or a completed checklist.

## Local data lifecycle

Captures, approvals, readiness entries and report drafts live only in the active
Streamlit session. Refreshing/restarting can lose them. Download records if
needed. Start a fresh session to clear active application data; server/framework
memory cleanup is not a secure-erasure guarantee. Downloaded reports can
contain operator-entered personal/network information; review before sharing.
