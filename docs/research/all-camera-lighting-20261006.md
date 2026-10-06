# Every listed RAW camera under normal and dark lighting

All four directly listed Camera2 RAW/manual paths on the S22 Ultra — back main (ID 0, 6.4 mm), front (ID 1, 3.8 mm), back ultrawide (ID 2, 2.2 mm) and front (ID 3, 3.8 mm) — each produced three verified four-frame control quartets under owner-fixed normal lighting, and again after the owner dimmed the lights with the phone and scene untouched. That is 96 original DNGs (987,280,128 bytes per condition), every quartet passing its focus/white-balance/timestamp/TIFF control checks and independent formula verification. Physical camera IDs 5, 6 and 7 again refused direct open in both conditions.

This is device-behavior evidence on one phone. It does not measure Samsung-pipeline parity, calibrated noise or dynamic range, scene quality, S25 behavior, or any product choice.

## Coverage

| Camera ID | Facing | Focal | RAW mosaic | CFA layout | Quartets per condition |
| --- | --- | --- | --- | --- | --- |
| 0 | back | 6.4 mm | 3000 × 4000 | GRBG | 3 + 3 |
| 1 | front | 3.8 mm | 2736 × 3648 | GRBG | 3 + 3 |
| 2 | back | 2.2 mm | 3000 × 4000 | RGGB | 3 + 3 |
| 3 | front | 3.8 mm | 2208 × 3216 | GRBG | 3 + 3 |

Two Bayer layouts coexist on one device: the ultrawide (ID 2) reports `RGGB` while the other three report `GRBG`. The two front paths share focal length and facing but remain distinct API paths; this table does not prove four distinct sensors. IDs 1 and 3 returned identical shutter/ISO behavior in the dark condition.

## Capture behavior and limits

Shutter ceilings bind differently per path. The intended single is 4× the middle shutter with ISO reduced to hold the nominal shutter×ISO product. The front paths (1, 3) reach 159.861 ms and realize that ratio exactly in the dark. The back paths cap at 103.389 ms: in the dark the main camera's requested 159.861 ms clamps to 103.389 ms, and the ultrawide clamps in both conditions (119.977 ms requested under normal light). The single's ISO compensates, holding the actual long-to-middle nominal product between 0.998 and 1.000 everywhere.

Per-frame black-level calibration differs within a quartet in the dark. Under normal light all frames on all paths report black level 64. With lights dimmed, the main camera stays uniform at 64, while the front paths and ultrawide report black 65 on their bracket frames and 64 on the longer/lower-ISO single. The first dark analysis pass correctly refused these quartets under its uniform-metadata assumption; the analysis was then corrected to normalize each frame by its own black level (as its arithmetic already did) and to record the levels explicitly. Each frame's black level comes from the DNG itself; dynamic black-level behavior is recorded per frame in the source audits.

Exposure ranges shift as expected between conditions. The main camera meters near ISO 1214 (normal) and 3196 (dark); the front paths near ISO 196–200 and 2281. Long-bracket-frame clipping collapses from 4.1–7.7% of the mosaic under normal light to at most 0.08% in the dark, so this dark scene offers no meaningful highlight-recovery regime — a property of the scene, not of the cameras.

The gated candidate-to-middle ratio checks sit near nominal in the light and drift in the dark. Under normal light the main camera's single-vs-middle ratio has a median of 1.002 with p10–p90 of 0.86–1.17 over 5.7 million gated samples; in the dark the median drops to 0.937, the spread widens to 0.63–1.24, and only 1.3 million samples still pass the signal gates. Photon-starved samples and unmeasured flicker plausibly contribute; the audits record the distributions without claiming which.

Physical IDs 5 (6.4 mm), 6 (7.9 mm) and 7 (27.2 mm) failed separate direct-access attempts with `CAMERA_DISCONNECTED` in both conditions. This records that direct opening is unavailable through this path; it does not prove the sensors are unreachable, since logical-camera OutputConfiguration routing was not implemented.

## Conditions, tooling and corrections

Both conditions used the same fixed phone and scene, with the owner dimming the lights between capture passes; the runner recorded `no lux or flicker measurement` in each [conditions record](../../.scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006/). Normal was captured 2026-10-06 ~09:29 UTC and dark ~10:54 UTC the same day, each as a fresh capability map plus sequential per-camera capture.

The reusable [batch tooling](../../tools/raw-camera-experiment/README.md) landed on `develop` for S25 reuse (commits `6ddd53b`, `79bdb4a`, `5f0669d`), with capture source unchanged from `prototype/long-single-control` at `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`. A two-axis code review preceded the landing; its findings were fixed, and one reviewer claim about the capability gate was rejected after checking against the probe's symbolic constants and on-device behavior. Two mid-experiment corrections are part of this record: the ultrawide's `RGGB` layout required deriving green-plane positions from each sensor's advertised pattern rather than assuming one layout, and the dark black-level split required per-frame normalization. Every corrected analysis was validated against previously recorded outputs — merge masters, TIFFs and previews bit-identical; audit and verification JSONs exactly equal — before replacing any evidence.

## Reproduction and evidence

With the phone unlocked and fixed, per the [batch README](../../tools/raw-camera-experiment/README.md):

```bash
python3 tools/raw-camera-experiment/batch.py --stage capture --lighting normal \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006
python3 tools/raw-camera-experiment/batch.py --stage capture --lighting dark \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006
python3 tools/raw-camera-experiment/batch.py --stage analyze --lighting dark \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006 \
  --analysis-python /path/to/raw-inspection/bin/python
```

Evidence lives in `.scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006/{normal,dark}/`, each condition holding originals, capability records, per-camera comparisons, source audits, pipeline verification, logs and a whole-tree sha256 [manifest](../../.scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006/normal/manifest.json); `analysis-status.json` records every camera as verified. Originals are never modified by analysis. Desktop processing time is not phone capture latency. The evidence task remains open pending S25 measurement and product-direction decisions; nothing here selects a capture strategy for the product.

## Recorded capture facts

<!-- BEGIN GENERATED CAMERA FACTS -->

| Lighting | Camera / facing | RAW / CFA | Middle ms / ISO | Longer single ms / ISO | Bracket / single integration | RAW storage |
| --- | --- | --- | --- | --- | --- | --- |
| dark control-01 | 0 / back | 4000 × 3000 / GRBG | 39.965 / 3196 | 103.389 / 1235 | 1.4832× | 3.00× |
| dark control-02 | 0 / back | 4000 × 3000 / GRBG | 39.965 / 3196 | 103.389 / 1235 | 1.4832× | 3.00× |
| dark control-03 | 0 / back | 4000 × 3000 / GRBG | 39.965 / 3196 | 103.389 / 1235 | 1.4832× | 3.00× |
| dark control-01 | 1 / front | 3648 × 2736 / GRBG | 39.965 / 2281 | 159.861 / 570 | 1.3125× | 3.00× |
| dark control-02 | 1 / front | 3648 × 2736 / GRBG | 39.965 / 2281 | 159.861 / 570 | 1.3125× | 3.00× |
| dark control-03 | 1 / front | 3648 × 2736 / GRBG | 39.965 / 2281 | 159.861 / 570 | 1.3125× | 3.00× |
| dark control-01 | 2 / back | 4000 × 3000 / RGGB | 39.965 / 1601 | 103.389 / 618 | 1.4832× | 3.00× |
| dark control-02 | 2 / back | 4000 × 3000 / RGGB | 39.965 / 1601 | 103.389 / 618 | 1.4832× | 3.00× |
| dark control-03 | 2 / back | 4000 × 3000 / RGGB | 39.965 / 1601 | 103.389 / 618 | 1.4832× | 3.00× |
| dark control-01 | 3 / front | 3216 × 2208 / GRBG | 39.965 / 2281 | 159.861 / 570 | 1.3125× | 3.00× |
| dark control-02 | 3 / front | 3216 × 2208 / GRBG | 39.965 / 2281 | 159.861 / 570 | 1.3125× | 3.00× |
| dark control-03 | 3 / front | 3216 × 2208 / GRBG | 39.965 / 2281 | 159.861 / 570 | 1.3125× | 3.00× |
| normal control-01 | 0 / back | 4000 × 3000 / GRBG | 19.983 / 1214 | 79.931 / 303 | 1.3125× | 3.00× |
| normal control-02 | 0 / back | 4000 × 3000 / GRBG | 19.983 / 1210 | 79.931 / 302 | 1.3125× | 3.00× |
| normal control-03 | 0 / back | 4000 × 3000 / GRBG | 19.983 / 1210 | 79.931 / 302 | 1.3125× | 3.00× |
| normal control-01 | 1 / front | 3648 × 2736 / GRBG | 29.994 / 200 | 119.977 / 50 | 1.3125× | 3.00× |
| normal control-02 | 1 / front | 3648 × 2736 / GRBG | 29.994 / 191 | 119.977 / 50 | 1.3125× | 3.00× |
| normal control-03 | 1 / front | 3648 × 2736 / GRBG | 29.994 / 197 | 119.977 / 50 | 1.3125× | 3.00× |
| normal control-01 | 2 / back | 4000 × 3000 / RGGB | 29.994 / 621 | 103.389 / 180 | 1.3626× | 3.00× |
| normal control-02 | 2 / back | 4000 × 3000 / RGGB | 29.994 / 621 | 103.389 / 180 | 1.3626× | 3.00× |
| normal control-03 | 2 / back | 4000 × 3000 / RGGB | 29.994 / 625 | 103.389 / 181 | 1.3626× | 3.00× |
| normal control-01 | 3 / front | 3216 × 2208 / GRBG | 29.994 / 196 | 119.977 / 50 | 1.3125× | 3.00× |
| normal control-02 | 3 / front | 3216 × 2208 / GRBG | 29.994 / 200 | 119.977 / 50 | 1.3125× | 3.00× |
| normal control-03 | 3 / front | 3216 × 2208 / GRBG | 29.994 / 207 | 119.977 / 51 | 1.3125× | 3.00× |

Integration is summed sensor exposure, not elapsed capture latency. Paths without four recorded frames are excluded from this table.

dark: physical direct-access failures: 5, 6, 7.
normal: physical direct-access failures: 5, 6, 7.

| Lighting / camera / run | Auto ISO → middle ISO | Black bracket → single | Middle / single clipping % | Long shutter clamped | Single / middle nominal product |
| --- | --- | --- | --- | --- | --- |
| dark / 0 / control-01 | 12150 → 3196 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.01523 / 0.01471 | True | 0.999657 |
| dark / 0 / control-02 | 12150 → 3196 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.01529 / 0.01468 | True | 0.999657 |
| dark / 0 / control-03 | 12150 → 3196 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.01524 / 0.01453 | True | 0.999657 |
| dark / 1 / control-01 | 2284 → 2281 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00001 / 0.00001 | False | 0.999562 |
| dark / 1 / control-02 | 2284 → 2281 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00001 / 0.00001 | False | 0.999562 |
| dark / 1 / control-03 | 2284 → 2281 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00002 / 0.00001 | False | 0.999562 |
| dark / 2 / control-01 | 1603 → 1601 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00220 / 0.00224 | True | 0.998592 |
| dark / 2 / control-02 | 1603 → 1601 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00237 / 0.00230 | True | 0.998592 |
| dark / 2 / control-03 | 1603 → 1601 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00222 / 0.00221 | True | 0.998592 |
| dark / 3 / control-01 | 2284 → 2281 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00001 / 0.00001 | False | 0.999562 |
| dark / 3 / control-02 | 2284 → 2281 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00001 / 0.00001 | False | 0.999562 |
| dark / 3 / control-03 | 2284 → 2281 | [65, 65, 65, 65] → [64, 64, 64, 64] | 0.00001 / 0.00001 | False | 0.999562 |
| normal / 0 / control-01 | 1215 → 1214 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.06335 / 0.06352 | False | 0.998353 |
| normal / 0 / control-02 | 1212 → 1210 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.06344 / 0.06276 | False | 0.998347 |
| normal / 0 / control-03 | 1212 → 1210 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.06310 / 0.06297 | False | 0.998347 |
| normal / 1 / control-01 | 200 → 200 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.01080 / 0.01115 | False | 1.000000 |
| normal / 1 / control-02 | 192 → 191 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.00000 / 0.00000 | False | 1.047120 |
| normal / 1 / control-03 | 198 → 197 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.01034 / 0.01078 | False | 1.015228 |
| normal / 2 / control-01 | 623 → 621 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.44865 / 0.46330 | True | 0.999118 |
| normal / 2 / control-02 | 623 → 621 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.44857 / 0.47241 | True | 0.999118 |
| normal / 2 / control-03 | 626 → 625 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.46089 / 0.47200 | True | 0.998239 |
| normal / 3 / control-01 | 197 → 196 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.00000 / 0.00000 | False | 1.020408 |
| normal / 3 / control-02 | 200 → 200 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.00779 / 0.00796 | False | 1.000000 |
| normal / 3 / control-03 | 208 → 207 | [64, 64, 64, 64] → [64, 64, 64, 64] | 0.00000 / 0.00000 | False | 0.985507 |

| Lighting / camera / run | Focal lengths mm | Auto shutter ms | Actual bracket EV relative to middle |
| --- | --- | --- | --- |
| dark / 0 / control-01 | [6.4] | 39.965296 | -2.000 / +0.000 / +1.371 |
| dark / 0 / control-02 | [6.4] | 39.965296 | -2.000 / +0.000 / +1.371 |
| dark / 0 / control-03 | [6.4] | 39.965296 | -2.000 / +0.000 / +1.371 |
| dark / 1 / control-01 | [3.8] | 39.965296 | -2.000 / +0.000 / +2.000 |
| dark / 1 / control-02 | [3.8] | 39.965296 | -2.000 / +0.000 / +2.000 |
| dark / 1 / control-03 | [3.8] | 39.965296 | -2.000 / +0.000 / +2.000 |
| dark / 2 / control-01 | [2.2] | 39.965296 | -2.000 / +0.000 / +1.371 |
| dark / 2 / control-02 | [2.2] | 39.965296 | -2.000 / +0.000 / +1.371 |
| dark / 2 / control-03 | [2.2] | 39.965296 | -2.000 / +0.000 / +1.371 |
| dark / 3 / control-01 | [3.8] | 39.965296 | -2.000 / +0.000 / +2.000 |
| dark / 3 / control-02 | [3.8] | 39.965296 | -2.000 / +0.000 / +2.000 |
| dark / 3 / control-03 | [3.8] | 39.965296 | -2.000 / +0.000 / +2.000 |
| normal / 0 / control-01 | [6.4] | 19.982648 | -2.000 / +0.000 / +2.000 |
| normal / 0 / control-02 | [6.4] | 19.982648 | -2.000 / +0.000 / +2.000 |
| normal / 0 / control-03 | [6.4] | 19.982648 | -2.000 / +0.000 / +2.000 |
| normal / 1 / control-01 | [3.8] | 29.994234 | -2.000 / +0.000 / +2.000 |
| normal / 1 / control-02 | [3.8] | 29.994234 | -2.000 / +0.000 / +2.000 |
| normal / 1 / control-03 | [3.8] | 29.994234 | -2.000 / +0.000 / +2.000 |
| normal / 2 / control-01 | [2.2] | 29.994234 | -2.000 / +0.000 / +1.785 |
| normal / 2 / control-02 | [2.2] | 29.994234 | -2.000 / +0.000 / +1.785 |
| normal / 2 / control-03 | [2.2] | 29.994234 | -2.000 / +0.000 / +1.785 |
| normal / 3 / control-01 | [3.8] | 29.994234 | -2.000 / +0.000 / +2.000 |
| normal / 3 / control-02 | [3.8] | 29.994234 | -2.000 / +0.000 / +2.000 |
| normal / 3 / control-03 | [3.8] | 29.994234 | -2.000 / +0.000 / +2.000 |

<!-- END GENERATED CAMERA FACTS -->
