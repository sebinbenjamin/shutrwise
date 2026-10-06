# RAW camera lighting batch

This experiment captures three four-frame sequences per directly exposed camera with RAW and manual-sensor capability. It uses the existing research probe, then checks and renders the files separately. Capture is sequential because the phone shares camera resources. Desktop processing can happen after the lighting changes.

The script verifies that the installed probe matches the local APK, gets a fresh capability map, preserves originals, and continues to other cameras if one fails. It refuses existing capture or analysis outputs. Failures and API exposure limits remain in the evidence. Physical IDs that are readable but not directly listed get one separate single-frame direct-access attempt, rather than being silently counted as tested lenses.

The S22 directly lists camera IDs 0, 1, 2 and 3. IDs 0 and 2 correspond to the main and ultrawide paths in the capability record; IDs 1 and 3 are front paths with the same advertised focal length. These are API paths, not proof of four distinct sensors. Additional physical IDs 5, 6 and 7 advertise main and telephoto focal lengths. A failed direct-open attempt does not prove that logical-camera routing cannot access the physical sensor. This script does not implement physical OutputConfiguration routing.

## Commands

From the repository root, with the development phone unlocked and fixed in place:

```bash
python3 tools/raw-camera-experiment/batch.py \
  --stage capture --lighting normal \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006
```

When capture reports complete, dim the lights, keep the phone and objects fixed, and run:

```bash
python3 tools/raw-camera-experiment/batch.py \
  --stage capture --lighting dark \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006
```

Analyze each saved condition independently:

```bash
python3 tools/raw-camera-experiment/batch.py \
  --stage analyze --lighting normal \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006
python3 tools/raw-camera-experiment/batch.py \
  --stage analyze --lighting dark \
  --output .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006
```

Use a new output root for another experiment. `--camera-ids 0 2` selects a listed subset; `--skip-physical-check` omits the physical direct-access attempts. `--device` selects one authorized phone when more than one is connected. Its serial is omitted from the saved records and redacted from runner logs. `--analysis-python` selects a Python environment containing the dependencies listed in [requirements.txt](analysis/requirements.txt).

## Running on another device

The batch is device-agnostic: the capability map, listed camera IDs, sensor Bayer layouts and shutter/ISO limits are discovered from the connected phone at run time, and the S22 interpretation above is one device's record, not an assumption. To run against a new phone such as the S25 Ultra, authorize ADB, rebuild the probe APK on that machine with `python3 probe/build.py`, and pass a fresh output root such as `.scratch/shutrwise/assets/s25-ultra/all-camera-lighting-<date>`. Keep each device's evidence in its own output roots; cross-device conclusions need separately captured conditions on both phones.

## Probe setup and provenance

The existing installed APK is verified against `probe/build/probe.apk`, which is a local ignored build artifact. On a fresh checkout, build with `python3 tools/raw-camera-experiment/probe/build.py` using the SDK/JDK setup in [development-phone.md](../../docs/development-phone.md). Install the intended APK before capture. The batch deliberately refuses a different installed build.

The Android capture source is copied unchanged from `prototype/long-single-control`, commit `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`. The host-side Python (device selection, batch orchestration) is maintained here and shares ADB device selection with the other device tools through `tools/adb_select.py`.

Analysis code originates from the archived lighting-pair experiment, consolidated as follows after the 2026-10-06 review:

- Shared RAW-plane helpers live in `analysis/raw_common.py`: one geometric ROI table, one rounding-consistent ROI slicer, quartile stats, Bayer-pattern-aware green extraction, and the phase-only shift diagnostic. The old `source_audit.py` helper module was removed; its archived original remains on the `research/*` branches.
- ROI keys are geometric everywhere (`center_detail`, `dark_lower_left`, `upper_left`, `right_edge`). The archived scene names mapped to the same coordinates: `towel` → `center_detail`, `bright_wall` → `upper_left`, `right_metal` → `right_edge`. The `normal` lighting evidence predates this rename and still carries the scene names.
- ROI pixel bounds use `round()` in every script. `compare.py` previously truncated with `int()`, so its ROI edges could differ by one pixel from the reported bounds; unified metrics may differ from the `normal` evidence within that one-pixel edge.
- The unused `--shifts-json` global-translation path was removed from `compare.py` along with its scipy dependency. This pipeline never aligns frames; the metrics key `alignment` is now the constant `{"method": "none"}`, `alignment_rejected_fraction` is gone, and `aligned_middle_clipped_short_usable_sample_count` is renamed to `weighted_middle_clipped_short_usable_sample_count` (it was always weight-based, never alignment-based).
- `verify_long_control.py` deliberately shares no helpers with the pipeline it verifies.

## Interpretation

Each sequence contains a short/middle/long fixed-ISO bracket and a longer/lower-ISO single. Actual results determine the analysis. Shutter and ISO limits can prevent the intended spacing or the metered brightness. The merge uses the first three files; the single uses the fourth. Equal nominal shutter-times-ISO is not calibrated gain.

Compare strategies within each camera and lighting condition first. Different lenses and front cameras see different scenes; the geometric crops need inspection before judging photographic detail. The analysis assumes common RAW layout/calibration within a sequence and reports a failure when its assumptions or metadata checks fail. It does not establish calibrated noise, dynamic range, light levels, flicker, or color, and does not align or deghost frames. Fresh capability mapping, directly captured path coverage, and physical access attempts are reported separately from image-quality observations.
