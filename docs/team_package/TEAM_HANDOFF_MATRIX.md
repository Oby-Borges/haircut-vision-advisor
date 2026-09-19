# Team Handoff Matrix

| Output | Owner | Consumer |
|---|---|---|
| session_id / subject_id | Software/App | Vision, Integration |
| haircut preferences | Software/App | Vision |
| camera frames | Camera Node | Vision |
| scan completeness | Vision | Software/App |
| head pose | Vision | Main Controller |
| head-relative haircut map | Vision + App | Planning/IK |
| AR overlay | Vision | App/Main UI |
| plan approval | Software/App | Integration/Planning |
| validated joint path | Planning/IK | Main Controller |
| joint calibration | Robot Team | Main Controller |
| motion + safety | Main Controller | Physical robot |
| execution status | Main Controller | App/Integration |

## Rule
If a team changes a shared payload, update `01_SHARED/API_CONTRACT.md` before integration.
