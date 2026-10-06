# Independent audit: longer exposure at lower ISO versus a RAW bracket

The new control supports a useful practical result for this S22 scene: an approximately 80 ms lower-ISO single RAW keeps broadly the middle exposure's brightness and clipping while showing less visible color grain than the approximately 20 ms auto-metered RAW. The three-source merge looks quieter still and preserves a separate shorter exposure for clipped highlights. That establishes a trade-off worth exploring, not a universally best capture strategy or a measured sensor SNR improvement.

## Protocol and valid capture controls

The [protocol](protocol.md) was fixed before viewing new processing results. An independently developed fresh middle-frame preview then confirmed the four fixed scene rectangles remained semantically appropriate before numerical measurements. Historical captures are excluded from brightness comparisons. Current illumination and phone stability were not independently measured or freshly owner-confirmed. Results apply only within these new quartets.

The [independent source metrics](source-metrics.json) inspect all twelve DNGs and actual TotalCaptureResults. Every file's TIFF exposure and ISO matches the result. RAW-image, result and capture-start timestamps agree; frame numbers and timestamps are unique within each quartet. All requested shutter times executed exactly. Focus and white-balance gains are constant across all four sources in each quartet; AWB lock is true. Actual sensitivity differs slightly from requested sensitivity, so calculations use actual values. Bracket ISO is constant and both long exposures have identical actual shutters. All eligibility checks for the intended control pass.

| Quartet | Actual ISO: frames 0–2 / frame 3 | Short / middle / long shutter | Lower-ISO single nominal shutter×ISO relative to middle |
| --- | --- | --- | --- |
| 01 | 1132 / 283 | 4.995662 / 19.982648 / 79.930592 ms | 1.000000 |
| 02 | 1126 / 281 | Same | 0.998224 |
| 03 | 1129 / 282 | Same | 0.999114 |

Each source has a 4000×3000 GRBG mosaic, metadata black level 64 for all CFA channels and white level 1023. These values were read separately from every DNG and checked against dynamic Camera2 values, rather than presumed constant across ISO. Per-CFA code distributions and source hashes are retained. Rawpy documents the [raw arrays, color indexes and black/white-level API](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html).

## Brightness and ISO/gain control

Frame 3 versus frame 1 changes both shutter and sensitivity. Their gated same-CFA nominal-normalized radiance medians are 1.0000, 1.0018 and 1.0009. Source dark-region median codes remain 16 in both paths; towel codes are approximately 30 versus 30–31. Consequently the longer/lower-ISO source does not have four times the recorded code signal of the middle source, although its integration lasts four times as long.

Frame 2 versus frame 3 keeps shutter identical while changing ISO approximately fourfold. Gated nominal-normalized medians are 0.9929, 0.9982 and 0.9924. This agrees approximately with the nominal ISO signal-scaling model over the tested unsaturated samples. It does not calibrate absolute analog gain, collected photon count, full-well capacity or noise mechanisms. Android describes [SENSOR_SENSITIVITY as an ISO sensitivity/gain control](https://developer.android.com/reference/android/hardware/camera2/CaptureResult#SENSOR_SENSITIVITY); reducing ISO alone is not treated here as increased light collection. The longer shutter changes integration; unknown illumination and pipeline behavior remain relevant.

All three displayed paths use identical white balance and transformation. The implementation divides each source by its actual shutter×ISO product relative to the middle exposure. For frame 3 that applies only a metadata-derived 0–0.178% scale adjustment; it does not fit image brightness empirically. Independent source statistics before that adjustment remain available. Same-render green-region medians differ modestly: the longer single is about 2.4–2.6% higher in the dark ROI, and approximately -1.1% to +1.3% in the towel ROI. The nearly black right strip is quantized/noisy and is not a strong radiometric control.

The short-exposure dark-region gated ratios are particularly vulnerable to the minimum-signal selection threshold; noise, quantization and selection bias can inflate them. They do not isolate illumination flicker or prove nonlinearity. Scene spatial variance is never presented as temporal noise or SNR.

## Clipping and registration

Whole-mosaic saturation at each file's reported white level is:

| Quartet | Middle RAW | Longer/lower-ISO RAW | Long/high-ISO RAW | Short/high-ISO RAW |
| --- | ---: | ---: | ---: | ---: |
| 01 | 0.050392% | 0.052392% | 7.982358% | 0% |
| 02 | 0.052358% | 0.053225% | 7.934958% | 0% |
| 03 | 0.051925% | 0.053958% | 7.956925% | 0% |

The candidate single has similar, slightly greater clipping than the middle RAW; improved highlight headroom relative to the middle is not established. The same-shutter high-ISO source clips much more. All 6047/6283/6231 middle-saturated coordinates have unsaturated samples in the short source, subject to alignment and illumination caveats. Photographic importance or accurate recovery at every such coordinate is not proven.

The primary qualitative comparison uses quartet 01 because source-only diagnostics satisfy the predeclared registration caution: every source-to-middle estimated displacement is below 0.10 raw pixel. Selection is based on that criterion, not which rendering looks nicest. Quartet 02/03 lower-ISO sources show estimated horizontal displacement of approximately 1.64/1.55 raw pixels from the middle, exceeding the one-pixel caution. Their short sources show about two raw pixels of diagonal displacement. The same-shutter frame 2/frame 3 pair is closer, with shifts below 0.06 raw pixel in all quartets, making it the better ISO/gain diagnostic.

These phase-only estimates are not geometry ground truth, and passing the caution threshold does not certify local alignment. OIS remained enabled. There is no interpolation in the primary merge, so apparent grain reduction is not an alignment-resampling effect. The merge agent's later source-selected clipped-highlight crop is explicitly exploratory, separate from the originally fixed ROIs.

## Processing verification and visual result

The [independent pipeline verification](pipeline-verification.json) reconstructs middle, lower-ISO and merged masters from immutable sources. All are finite. Middle masters match exactly; longer-single and merge formula errors are below 1.2×10^-7 normalized signal. Saturated bracket samples receive zero merge weight, and no coordinate exhausts all bracket weights. Saved float RGB files match the same white balance and Bayer-cell mapping exactly; all saved preview PNGs reproduce the identical display transfer exactly. This verifies processing consistency, not calibrated color accuracy.

Source inspection and a matched lifted-shadow view of quartet 01 show less visible color grain in the longer/lower-ISO single than the metered middle RAW. The merge appears quieter still. Towel texture remains visible in all three; no independent resolution or detail-recovery metric was collected. Half-resolution sensor RGB and fixed channelwise tone mapping are research displays, not a calibrated sRGB conversion or a Lightroom editing comparison. No photographer preference assessment has yet been made.

## Costs and bounded conclusion

Each single original uses 24,029,520 bytes; the bracket uses 72,088,560 bytes. The longer single integrates for 79.930592 ms versus the bracket's summed 104.908902 ms, so the bracket uses 31.25% more summed integration and three times the source storage. The middle integrates for 19.982648 ms. The experimental quartet captures all four controls; it does not measure future one-shot workflow latency, phone merge performance or battery use. Summed integration is not wall-clock shutter latency.

A stability-aware exposure strategy is therefore a credible simpler baseline before attributing value to more sophisticated bracketing. In this scene the longer/lower-ISO single obtains much of the visible shadow benefit while preserving a similar clipping trade-off with one source file. The bracket retains a distinct shorter source for the small clipped areas and appears quieter under this rendering. Neither establishes the best possible single exposure, adaptive-bracketing superiority, an AI requirement, Samsung superiority or S25 behavior.

## Provenance and reproduction

Capture/comparison source is archived on `prototype/long-single-control`, commit `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`; comparison script SHA-256 `2b61bd13d2ee65b1583921ce032e052663ee34ae18a2ee6f43b19fb13fe4e4fe` matches the inspected source and output summary.

Independent audit source is archived on `research/long-single-control-audit`, commit `a5b3c77e485dd425a8f4ad3fedfbe9075a815a2f`; checkout `/tmp/shutrwise-long-control-audit`. `audit/long_control_audit.py SOURCE OUTPUT_JSON` reproduces source checks, using the earlier archived `source_audit.py` helpers. `audit/verify_long_control.py SOURCE COMPARISON OUTPUT_JSON` verifies masters and previews. Use `/home/t3agent/.local/share/shutrwise/raw-inspection/bin/python` and new output paths for reproduction. Original DNG hashes are recorded independently in both metric files.
