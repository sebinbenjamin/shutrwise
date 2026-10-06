# S22 Ultra Camera2 measurements

On 2026-10-06, a throwaway native Android probe saved independently decodable RAW/DNG files from all four listed Camera2 paths on the connected SM-S908E. The main camera also saved separate -2/0/+2 EV exposures in one burst, including three repeats after the owner standardized the garage lighting and fixed the phone in place.

This establishes a workable development platform for controlled RAW capture. Capture-quality benefits, Samsung pipeline comparisons and target S25 behavior remain unmeasured.

## Device and source

The [software inventory](../../.scratch/shutrwise/assets/s22-ultra/device-record.md) records Android 16 / API 36, build `BP2A.250605.031.A3.S908EXXSEGZH4`, security patch 2026-08-05 and Samsung Camera 16.0.00.66. Each finding here applies to that phone and build.

Probe source is archived on local branch `prototype/s22-camera-probe`, commit `eeaf02f24cba56590990e3bcd2ec0666a0984441`. The native prototype and its `probe/README.md` describe the build, capture state and inspection method. It is research code, with no ML or adaptive planner. Open it in its own checkout with `git worktree add /path/to/new/probe-checkout prototype/s22-camera-probe`. The existing checkout is `/tmp/shutrwise-camera-probe`; the committed branch survives removal of that temporary directory.

The APK used for the final capability dump and successful corrected captures has SHA-256 `e5a99ae5b7e8e14b4b64cc20c80eeaa18dfd2a2ffed121f012847b577e7c7495`. Collection records identify the APK and on-device run. Unique device serials are omitted.

## Camera capability map

Source: [final capability JSON](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-20261006/capabilities-final/capabilities.json). RAW and MANUAL_SENSOR are advertised on all four listed IDs. Their sensitivity ranges are ISO 50-3200. The probe successfully captured a DNG through each listed ID.

| Listed ID | Reported path | Hardware level | Regular RAW dimensions | Advertised exposure range | Saved DNG |
| --- | --- | --- | --- | --- | --- |
| 0 | Rear logical, 6.4 mm baseline | LEVEL_3 | 4000 × 3000 | 0.081680-103.388880 ms | Main single and brackets |
| 1 | Front, 3.8 mm | FULL | 3648 × 2736 | 0.091672-170.289000 ms | Single |
| 2 | Rear, 2.2 mm ultrawide | LIMITED | 4000 × 3000 | 0.041660-103.388880 ms | Single |
| 3 | Front, 3.8 mm | FULL | 3216 × 2208 | 0.091672-323.883000 ms | Single |

Logical camera 0 names physical IDs 2, 5, 6 and 7. Additional readable characteristics report ID 5 at 6.4 mm with 4000 × 3000 RAW, and IDs 6 and 7 at 7.9 mm and 27.2 mm with 3648 × 2736 RAW. Captured main-camera results identify active physical ID 5. Physical output routing for IDs 6 and 7 was not tested. Reading their characteristics does not prove reliable telephoto RAW capture. Two front IDs do not establish two separate physical front sensors.

The main logical path advertises a maximum exposure near 1/9.7 second. That is a constraint of this exposed API path, not a measured physical sensor limit or a limit of Samsung Pro mode. No high-resolution RAW sizes were reported for the listed main path. The dump includes JPEG/YUV sizes, stream timing, locks, lens controls and available request/result keys for further investigation. Some complex characteristic objects are retained as Java type and string representation rather than fully decoded structures.

## Original smoke tests

The [initial dataset](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-20261006/conditions.json) contains 11 DNGs across seven capture runs. The owner later explained that lighting had varied. These files establish output and controls; their between-run brightness, clipping or noise differences cannot establish a quality improvement.

Seven DNGs have explicit TIFF Orientation 1, preserving sensor axes. Four earlier diagnostic files in `main-single` and `main-bracket` retain Orientation 9 from the initial export. LibRaw decoded them, but their orientation tag is invalid. The exporter was corrected and main-camera single/bracket tests repeated. These diagnostic originals remain preserved and are excluded from valid-output counts. A rational-number JSON serialization issue was also corrected before collecting the usable reports.

## Standardized repeat

The owner confirmed garage closed, lights on and fixed phone placement, then said "Try now". Three main-camera brackets were collected from 05:31:21 to 05:31:57 UTC. [Conditions and protocol](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-controlled-20261006/conditions.json) record this as owner-standardized indoor capture. Light flicker, physical stability and subject motion were not independently measured.

Each run metered automatically, then held that ISO and manually requested the three shutter times below. All nine actual exposures matched their requests, without range clamping. Each run returned a constant ISO, focus distance and white-balance gains across its three frames; AWB lock was reported true. ISO returned by the camera was one or two units lower than requested, so analysis uses the actual values.

| Run | Actual ISO | -2 EV shutter | 0 EV shutter | +2 EV shutter | Focus within bracket |
| --- | --- | --- | --- | --- | --- |
| main-bracket-01 | 1170 | 4.995662 ms | 19.982648 ms | 79.930592 ms | 3.7037036 diopters |
| main-bracket-02 | 1162 | 4.995662 ms | 19.982648 ms | 79.930592 ms | 4.0 diopters |
| main-bracket-03 | 1159 | 4.995662 ms | 19.982648 ms | 79.930592 ms | 4.1666665 diopters |

The shutter ratio is exactly 1:4:16. New runs meter and focus again, which accounts for setting differences between repeats; they are not globally locked comparisons. Each bracket's middle file is the single-RAW baseline for comparing source information within that same sequence. This does not compare single-capture latency against bracket latency.

Raw sample percentages at or above the reported white level were:

| Run | -2 EV | 0 EV | +2 EV |
| --- | --- | --- | --- |
| 01 | 0% | 0.07903% | 7.94437% |
| 02 | 0% | 0.07886% | 7.85339% |
| 03 | 0% | 0.07904% | 7.81814% |

These are whole-frame mosaic statistics, with no selection of important highlights. They show the exposure trade-off in this scene. They do not measure recoverable dynamic range, shadow SNR or a better final photograph. No alignment, HDR merge or controlled RAW-editing comparison was performed.

## Independent file checks

The [repeat inspection JSON](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-controlled-20261006/dng-inspection.json) records LibRaw/rawpy decoding and TIFF checks. All nine repeat DNGs decoded, contain 4000 × 3000 RAW, have valid Orientation 1, and match Camera2 exposure/ISO metadata. RAW image/result/start timestamps matched, and no expected files were missing in these three repeats.

The [final verification record](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-verification-20261006.json) also confirms artifact hashes and that the installed APK matches the recorded build. Across both datasets, 20 DNGs decode; 16 have valid orientation, with four preserved diagnostic originals excluded from valid-output counts. Repository link, whitespace and tracker checks passed.

The main RAW path reports white level 1023 and black levels 64, with a GRBG mosaic stored in a 16-bit container. These observations do not establish sensor ADC precision or measured dynamic range. They also do not establish untouched full-resolution sensor data. LibRaw reports a 3984 × 2984 crop within the 4000 × 3000 raw image.

[Derived contact sheet](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-controlled-20261006/main-bracket-contact-sheet.jpg) shows run 01 using camera white balance, no automatic brightness normalization and matching preview parameters. It is a demosaiced review image; original DNGs remain beside their capture metadata. The [initial inspection JSON](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-20261006/dng-inspection.json) retains the variable-light and diagnostic checks separately.

DNG writes occur serially on the probe's camera callback handler. Reported sensor start gaps and write times do not establish maximum RAW burst rate or end-to-end user shutter latency. Nine successful repeat files are a smoke test, not sustained reliability evidence.

## Reproduce and continue

The [development setup](../development-phone.md) records tool paths. In the prototype checkout, build with `python3 probe/build.py`; collect a new capability or capture directory with `python3 probe/run.py`. The source README provides the exact commands and override flags. Inspect using the RAW-inspection virtual environment and `probe/inspect_dng.py`; select a repeat with `--contact-sheet-run main-bracket-01`.

Both datasets contain an `artifact-manifest.json` listing relative paths, file sizes and SHA-256 values. It covers original DNGs, metadata and derived previews, excluding the manifest itself. Captures remain in the probe's own phone storage as well as this repository's local evidence directories. No personal media was read or changed.

The next value experiment should compare an identically developed middle RAW against a documented merge of its bracket, then compare available Samsung baselines under matching conditions. Assess useful shadow detail, protected highlights and practical costs. Those results can guide whether adaptive capture is worthwhile. The product decision and the S25 evidence task remain open.

That RAW-versus-bracket experiment was subsequently run with delegated merge and audit agents. See [One RAW versus a bracket merge](raw-bracket-comparison-20261006.md) for the bounded findings, matching renders and controls still needed. The original probe evidence and conditions above remain unchanged.
