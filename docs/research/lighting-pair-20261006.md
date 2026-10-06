# New-scene dark and normal-lighting comparison

The owner changed the scene and designated the current lighting as the dark condition. Three fresh S22 Ultra camera-0 control sequences per lighting condition produced twenty-four DNGs. The owner added lights and reported ready for the brighter repeat. Both sets are captured, rendered and checked. This new scene cannot serve as a matched lighting repeat of the earlier garage experiment.

## Dark capture

All three sequences returned the same actual settings. The bracket sources are 9.991324, 39.965296 and 103.388880 ms at ISO 3196. The candidate single is 103.388880 ms at ISO 1235. Its nominal shutter-times-ISO product is 0.999657 of the middle RAW's product.

The automatic preview reported 39.965296 ms at ISO 12150. The probe bounds its manual ISO to the advertised maximum 3200. Thus the middle RAW uses the metered shutter with an ISO cap; it does not reproduce the full automatic exposure. The reported auto/manual ISO difference does not establish calibrated gain or Samsung proprietary processing. Both long requests hit the exposed 103.388880 ms shutter limit. The bracket is consequently -2 / 0 / approximately +1.37 EV relative to the middle, rather than a full -2 / 0 / +2 bracket.

The [lifted shadow comparison](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/dark/comparison/control-01/crop-dark_lower_left.png) shows the middle RAW, bracket merge and longer/lower-ISO single from left to right. Both alternatives look less grainy than the middle. The merge looks quieter in parts of the crop. This is a visual observation under a common display transform, not calibrated SNR or a measured detail score. The [full comparison](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/dark/comparison/control-01/comparison.png) retains the deliberately dark common rendering.

Single-file size is 24,029,520 bytes; the bracket uses 72,088,560 bytes. The bracket integrates for a summed 153.345500 ms versus 103.388880 ms for the longer single, approximately 48.32% more. These are integration sums, not measured independent capture latency.

## Checks and limitations

The [source audit](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/dark/source-audit.json) verifies timestamps, TIFF exposure/ISO tags, focus consistency, locked/consistent white balance, common shape/CFA and constant bracket ISO across all twelve captures. Each DNG is a 4000 by 3000 mosaic. Source-only translation estimates are below 0.05 raw pixel per axis in these sequences. No registration, local-motion check or illumination/flicker measurement was applied.

Middle-source clipping is approximately 0.0172% and candidate-single clipping approximately 0.0164–0.0167% of mosaic samples. Between 107 and 110 samples per bracket exhaust all near-white-rejection weights. The merge falls back to the shortest source at these locations; no recovered detail is claimed where every source clips or approaches clipping. These counts include near-white rejection and need not equal the exact-white clipping count.

The [pipeline verification](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/dark/pipeline-verification.json) reconstructs the formulas from originals and checks all nine float masters, RGB mapping and preview transfer. Maximum mosaic reconstruction error is below 1.2e-7. Saturated source samples receive zero positive merge weight. The earlier verifier assumed no exhausted weights; for this scene that assumption was removed while retaining formula verification of the shortest-source fallback. Verification reused separately authored audit code; no fresh independent agent review was performed.

Processing follows the archived earlier experiment with signed black-subtracted float data, nominal exposure normalization, exposure-weighted bracket merging and the same white balance/display curve for each alternative. There is no denoising, sharpening, learned processing or deghosting. This is half-resolution sensor RGB, not calibrated sRGB. Nominal shutter-times-ISO normalization does not calibrate gain. The longer single's smoothed normalized green ratio to the middle is roughly 0.978, illustrating a small response difference despite matching nominal products.

For this new scene, processing ROIs use geometric names and fixed coordinates rather than earlier object names. The inherited source-audit ROI names still refer only to their recorded coordinates; they do not establish the presence of those objects. Primary comparison 01 is the first sequence, not a quality-selected example.

## Brighter repeat and comparison

The brighter set uses the same capture source and three new four-frame sequences. The full views show broadly corresponding scene objects and framing. Illumination changed substantially, and autofocus and white balance were metered independently per session. This is a controlled intention with visual correspondence, not a calibrated lighting experiment or verified exact pixel registration between conditions.

| Condition | Middle RAW shutter / actual ISO | Longer single shutter / actual ISO | Bracket summed integration | Bracket cost versus longer single |
| --- | --- | --- | --- | --- |
| Dark, all sequences | 39.965296 ms / 3196 | 103.388880 ms / 1235 | 153.345500 ms | 48.32% more integration, 3× source storage |
| More lights, sequence 01 | 19.982648 ms / 1170 | 79.930592 ms / 292 | 104.908902 ms | 31.25% more integration, 3× source storage |
| More lights, sequence 02 | 19.982648 ms / 1146 | 79.930592 ms / 285 | 104.908902 ms | 31.25% more integration, 3× source storage |
| More lights, sequence 03 | 19.982648 ms / 1175 | 79.930592 ms / 293 | 104.908902 ms | 31.25% more integration, 3× source storage |

The normal-lighting preview metered ISO 1171, 1148 and 1175. None of the brighter set's requests needed ISO or shutter clamping. Its bracket has the full -2 / 0 / +2 shutter spacing. Actual nominal longer-single/middle products differ by at most 0.524%; processing uses the actual values. The smoothed normalized green ratios of longer single to middle are about 1.008–1.015, illustrating a small uncorrected RAW response difference.

In the [normal-lighting shadow crop](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/normal/comparison/control-01/crop-dark_lower_left.png), the longer single again looks less grainy than the middle RAW. The merge appears quieter still in parts of the crop. Differences are less visually striking than in the dark crop. The [two-condition panel](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/lighting-shadow-comparison.png) places the first sequence from each condition together, using the same display gain and transfer. Individual RAW exposure normalization and per-session white balance remain different; this panel does not measure a noise-reduction ratio between lighting conditions.

The brighter middle clips 0.0603–0.0634% of mosaic samples; the longer/lower-ISO single clips 0.0587–0.0633%. The long/high-ISO bracket source clips 6.34–6.51%, while the short source clips 0.00969–0.01102%. The bracket provides less-clipped source samples in highlight areas, but it cannot recover every highlight: 1312–1480 samples exhaust all near-white weights and use the recorded shortest-source fallback. Whole-image counts do not measure the photographic importance or recovered detail of those areas.

All twelve brighter captures pass the [source checks](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/normal/source-audit.json). Focus, locked white balance, timestamps, DNG tags and bracket ISO are consistent within each quartet. Source-only translation estimates stay below 0.034 raw pixel per axis. All nine brighter float masters and previews pass [formula/render verification](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/normal/pipeline-verification.json), with maximum mosaic error below 1.2e-7. These diagnostics do not prove absence of local movement or lighting flicker. Verification reused the separately authored audit scripts, without a fresh delegated review.

Both conditions support keeping a longer single as a useful baseline before paying for extra bracket files, when motion allows it. The merge can still look quieter and supply additional highlight samples. In the dark condition, API limits constrain both strategies. This result does not determine whether HDR brackets outperform an equal-exposure RAW stack, Samsung Photo/Pro/Expert RAW, or a calibrated best single exposure. Those alternatives have not been captured here. This remains S22 evidence; S25 behavior and the product direction remain open.

## Evidence and reproduction

The [artifact index](../../.scratch/shutrwise/assets/s22-ultra/lighting-pair-20261006/README.md) links originals, conditions, archived scripts, checks and the file manifest. Capture source is unchanged on `prototype/long-single-control`, commit `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`. Processing source derives from that commit; audit source derives from `research/long-single-control-audit`, commit `a5b3c77e485dd425a8f4ad3fedfbe9075a815a2f`.

Use the existing development Python environment and the archived `code/compare.py` with `--source <captures> --output <new-directory>`. Each capture directory contains `control-01`, `control-02` and `control-03`. The source and formula verifiers accept the source directory followed by output JSON, or source, comparison directory and output JSON respectively. Full capture commands remain in the earlier [report](long-single-control-20261006.md).

The archived `code/summarize_pair.py <evidence-root>` rebuilds the settings/cost summary, assembles the two-condition shadow panel from existing renders, and updates evidence hashes. Its panel adds labels and stacks rows; it does not alter the rendered image pixels.
