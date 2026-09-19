# Shared TrimSync API Contract

Base URL for the MAIN ARM CONTROLLER:

```text
http://<main-trimsync-ip>
```

Fallback during development:

```text
http://192.168.4.1
```

## 1. Main controller status

```http
GET /api/status
```

Used by all teams to confirm:
- controller online
- E-stop state
- armed state
- current mode
- head tracking freshness
- plan availability
- joint state

## 2. Head tracking

```http
POST /api/vision/head
Content-Type: application/json
```

Example:

```json
{
  "subject": "client-001",
  "seq": 1842,
  "confidence": 0.96,
  "translation_mm": [315.2, -42.0, 611.8],
  "rotation_rpy_deg": [2.1, -5.6, 13.4]
}
```

Send continuously while the head is being tracked.

## 3. Haircut plan

```http
POST /api/vision/plan
```

Example:

```json
{
  "session_id": "session-001",
  "plan_id": "low-fade-session-001",
  "style": "low_fade",
  "guard": "#1",
  "points": [
    {
      "region": "left_side",
      "x": -62,
      "y": 18,
      "z": -30,
      "pitch": 0,
      "yaw": 15,
      "roll": 90,
      "speed": 0.30
    }
  ]
}
```

Coordinates are head-relative. The app/vision layer should not use servo angles here.

## 4. AR overlay

```http
POST /api/vision/overlay
```

Example:

```json
{
  "plan_id": "low-fade-session-001",
  "head_seq": 1842,
  "frame_id": 920,
  "shapes": [
    {
      "kind": "path",
      "name": "left_fade_pass_1",
      "points": [
        [0.36, 0.70],
        [0.37, 0.63],
        [0.39, 0.56],
        [0.42, 0.49]
      ]
    }
  ],
  "target": [0.39, 0.56]
}
```

Overlay coordinates are normalized image coordinates:
- `[0,0]` = top-left
- `[1,1]` = bottom-right

## 5. Validated robot path

```http
POST /api/auto/path
```

Only the calibrated planning/IK layer should produce this.

Example:

```json
{
  "plan_id": "low-fade-session-001",
  "source": "vision-ik-bridge-v1",
  "points": [
    {"joints_deg": [90, 78, 108, 93, 88]},
    {"joints_deg": [92, 80, 110, 94, 89]}
  ]
}
```

The Main controller still checks joint limits.

## 6. Auto controls

```http
POST /api/auto/arm
POST /api/auto/start
POST /api/auto/stop
```

`/api/auto/start` must never be used as a replacement for local operator approval.

## 7. Emergency stop

```http
POST /api/stop
```

## Camera-node API

The separate CAMERA NODE should expose:

```http
GET /health
GET /camera.jpg
```

Optional:

```http
GET /camera/status
POST /camera/resolution
```

The camera node does not directly command arm servos.

---

## Local app extension note (2026-09-19; not part of the supplied v1 wire API)

The TrimSync UI exports a separate `trimsync-app-draft-1` envelope for review.
It is not compatible with any controller POST above and must not be sent as an
execution request. See [local integration contract](../INTEGRATION.md) and the
downloadable schema in Integration → Contracts. Vision mapping and validated
IK/path outputs remain unimplemented; plan IDs only link the app's selection,
preview, approval and non-executable planning placeholder. Shared wire changes
require agreement with the consuming teams.
