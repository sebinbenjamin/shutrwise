# Every listed RAW camera under normal and dark lighting

All four directly listed Camera2 RAW/manual paths on the S22 Ultra — back main (ID 0, 6.4 mm), front (ID 1, 3.8 mm), back ultrawide (ID 2, 2.2 mm) and front (ID 3, 3.8 mm) — each produced three verified four-frame control quartets under owner-fixed normal lighting, and again after the owner dimmed the lights with the phone and scene untouched. That is 96 original DNGs (987,280,128 bytes per condition), every quartet passing its focus/white-balance/timestamp/TIFF control checks and independent formula verification. Physical camera IDs 5, 6 and 7 again refused direct open in both conditions.

This is device-behavior evidence on one phone. It does not measure Samsung-pipeline parity, calibrated noise or dynamic range, scene quality, S25 behavior, or any product choice.

## Coverage

| Camera ID | Facing | Focal | RAW mosaic | CFA layout | Quartets per condition |
| --- | --- | --- | --- | --- | --- |
| 0 | back | 6.4 mm | 3000 × 4000 | GBRG | 3 + 3 |
| 1 | front | 3.8 mm | 2736 × 3648 | GBRG | 3 + 3 |
| 2 | back | 2.2 mm | 3000 × 4000 | RGGB | 3 + 3 |
| 3 | front | 3.8 mm | 2208 × 3216 | GBRG | 3 + 3 |

Two Bayer layouts coexist on one device: the ultrawide (ID 2) reports `RGGB` while the other three report `GBRG`. The two front paths share focal length and facing but remain distinct API paths; this table does not prove four distinct sensors. IDs 1 and 3 returned identical shutter/ISO behavior in the dark condition.

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
