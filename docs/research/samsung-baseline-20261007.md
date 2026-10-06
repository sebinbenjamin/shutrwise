# Samsung and custom RAW comparison — S22 Ultra, 2026-10-07

The four-way experiment completed with three repeats per strategy. It does not establish a custom-capture advantage over Samsung. Samsung Pro DNGs appear less grainy in the inspected lifted-shadow views than the custom metered RAW, longer single and bracket merge. Exposures, stored brightness and processing differ, so this is a bounded visual observation, not a calibrated noise or dynamic-range ranking.

The owner authorized execution after agreeing the core capture interaction. The connected SM-S908E was used with its current garage scene, rear main camera and fixed placement. No scene restriction or S25 conclusion follows. The owner did not reconfirm stable lighting during the sequential captures. Light level, flicker, focus equivalence and registration were not independently controlled. The custom batch's `normal` directory is an operational label, not a measured lighting classification.

## Captures and settings

| Path | Repeats | Exposure metadata | Preserved source |
| --- | --- | --- | --- |
| Samsung Photo, 1×, 12 MP | 3 | JPEG EXIF about 119.977 ms / ISO 1600 | Three delivered JPEGs; automatic night-shot indication visible |
| Samsung Pro, auto settings, main W | 3 | DNG and paired JPEG EXIF 1/7 second / ISO 1600 | Three DNG/JPEG pairs |
| Custom metered RAW | 3 | Actual 39.965296 ms / ISO 3196 | Middle file in each quartet |
| Custom longer single RAW | 3 | Actual 103.388880 ms / ISO 1235 | Fourth file in each quartet |
| Custom fixed-ISO bracket | 3 | Actual 9.991324 / 39.965296 / 103.388880 ms, all ISO 3196 | Nine separate DNGs plus deterministic merges |

An additional JPEG-only Pro smoke capture is preserved and excluded from the three-repeat comparisons. There are fifteen new DNGs overall: three Samsung and twelve custom. Samsung's original JPEG-only Pro preference was restored and confirmed in the settings UI. Samsung Photo's night behavior was retained as the ordinary-camera baseline. No HDR source-frame count was measured.

The custom auto-metered baseline reported ISO 12150, then the probe bounded its manual request to ISO 3200; actual results reported ISO 3196. The longer single preserves approximately the bounded middle's nominal shutter-times-ISO product, rather than the original auto-metered product. Thus this control is not an optimized exposure planner and must not be called the best achievable single RAW. All three quartets share the settings above. The long bracket is shutter-clamped, producing approximately +1.37 EV rather than the planned +2 EV.

Samsung's EXIF values describe saved files, not proven single-frame sensor integration, the number of computational frames or elapsed shutter-to-save latency. Pro's displayed metering values and saved-file EXIF differed during inspection; rely on the recorded source metadata for the table without treating it as a complete description of Samsung's capture pipeline.

## What RAW means in these files

Samsung Pro DNGs have TIFF PhotometricInterpretation 34892, three samples per pixel, 12 bits per sample, white level 4095 and no Bayer CFA pattern. Their stored image is 4000 × 3000 linear three-channel data. LibRaw reports `RawType.Stack` and represents it as four channels with an unused fourth plane. Encoded clipping calculations exclude that padding.

Custom Camera2 DNGs decode as a 4000 × 3000 Bayer mosaic, GRBG, white level 1023 and per-channel black level 64. These observed structures demonstrate that the two saved RAW paths differ. The linear Pro representation indicates processing beyond an un-demosaiced mosaic, but does not by itself establish multi-frame merging, denoising or every preceding ISP operation. Twelve-bit linear RGB versus a Bayer white code of 1023 does not directly rank captured dynamic range.

Encoded RGB clipping in the three Pro DNGs is approximately 0.07258%, 0.07291% and 0.07352%. Custom middle Bayer clipping is approximately 0.01521%, 0.01493% and 0.01498%; longer singles are approximately 0.01455%, 0.01441% and 0.01426%. These percentages count different domains and are not a cross-pipeline highlight-recovery score. No maximum-recovery RAW editing test has been performed.

## Development and visual findings

[First-repeat overview](../../.scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007/comparison/repeat-01-overview.png) and [lifted-shadow view](../../.scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007/comparison/repeat-01-lifted.png) show six paths: delivered Photo, delivered Pro JPEG, Pro DNG, custom middle, custom longer single and custom merge. [Third-repeat lifted view](../../.scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007/comparison/repeat-03-lifted.png) provides a second inspected repeat. [Second-repeat lifted view](../../.scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007/comparison/repeat-02-lifted.png) was also inspected; the same qualitative shadow-grain pattern is visible across the three repeats.

RAW single-file development uses LibRaw linear sRGB, fixed white balance from the first custom middle's recorded gains, no auto brightness and 16-bit output. Pro RGB is area-downsampled to 2000 × 1500; custom mosaics use half-size development. The custom merge uses the independently verified native float master, the same white-balance convention and its recorded Camera2 color transform. All are rotated identically for display.

For display only, RAW brightness is matched to the custom middle's green median over the reference's 0.03–0.3 signal mask. The common curve is `x / (1 + x)` followed by sRGB encoding, with gains 2 and 16. Delivered JPEGs retain Samsung's rendering, apart from resize and rotation, and are unchanged between the overview and lifted boards. They do not receive the RAW shadow lift.

Pro's display scale is approximately 0.120–0.121, compared with 1.0 for the custom middle, 1.017–1.020 for the longer single and 0.983–0.987 for the merge. This large cross-pipeline normalization reinforces that the stored values are not calibrated common scene radiance. It is a visual brightness adjustment, not a gain calibration or proof of exposure equivalence. The complete parameters and scales are in [method records](../../.scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007/comparison/method.json).

The inspected views suggest quieter Pro DNG shadows. The custom longer single and merge also look quieter than the custom middle. Samsung Photo supplies a brighter, processed result immediately. These observations leave learning/decision clarity as a possible source of value, while providing no demonstrated reason to replace Samsung for image quality. No blind preference test, calibrated SNR, independent detail score or deghosting evaluation was performed.

The comparison supports exposure-lift inspection of preserved sources. It does not measure a beginner's editing effort or preference. LibRaw's bounded single-file output and this display curve are not a complete highlight-recovery workflow. Color transformations, different metering, unaligned framing and possible light changes remain confounders.

## Costs, checks and next evidence

The custom bracket uses three DNGs instead of one, approximately 3× source storage, and about 1.483× the longer single's summed integration. That is not elapsed capture latency. Samsung Pro DNGs are about 39.3 MB each; custom single DNGs are about 24.0 MB each. Samsung Photo JPEGs are about 3.24–3.28 MB each. These source sizes exclude metadata, previews and derived float masters.

All custom quartet source audits and independent formula/master/render verifications passed. Samsung sources were copied by exact newly created filenames and checksummed. Existing captures were preserved. [Samsung source records](../../.scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007/samsung-source-record.md) retain compact metadata and hashes in Git. The [custom evidence index](../../evidence/indexes/s22-samsung-custom-control-20261007.json) records original hashes, controls and audit outcomes. Explicit source verification passed for the custom index and Samsung manifest. The local gate passes; full files remain covered by VM backups.

The maintained [rendering script](../../tools/raw-camera-experiment/analysis/samsung_baseline.py) records the method. Reproduce offline into a fresh output directory:

```bash
/home/t3agent/.local/share/shutrwise/raw-inspection/bin/python tools/raw-camera-experiment/analysis/samsung_baseline.py \
  .scratch/shutrwise/assets/s22-ultra/samsung-baseline-20261007 /path/to/new/comparison
```

Camera apps launched by this run were stopped and the owned agent-device session closed. Final diagnostics found both Samsung Camera and the probe process absent. Sleep was requested; display diagnostics included OFF and DOZE_SUSPEND, so this record does not claim every display remained completely OFF. The earlier lock-screen obstacle was resolved by waking and dismissing the keyguard; lock settings were unchanged. This does not bypass a secure authentication requirement.

A useful follow-up would match manual Samsung Pro and Camera2 exposure/ISO more closely within their shared range, then compare RAW development under independently checked transforms. That would reduce exposure and processing confounds. Target S25 capability and Samsung-baseline measurements still remain necessary. There is no new product direction or AI-model decision in this experiment.
