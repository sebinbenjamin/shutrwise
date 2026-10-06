# One RAW versus a bracket merge on the S22 Ultra

Two delegated agents ran and independently assessed a deterministic merge of the three standardized S22 brackets on 2026-10-06. The merged rendering looks less grainy in a shadow-lifted crop. Longer exposures supply more unsaturated shadow signal, while shorter exposures retain samples at coordinates where the middle RAW clips.

This is a bounded positive result for extra exposure support in this indoor scene. It does not establish that bracketing beats an optimized single exposure or Samsung Camera, or that an intelligent planner is needed. S25 behavior remains unmeasured.

## What was compared

Each sequence's middle DNG is its one-RAW baseline. Its three source exposures are 4.995662, 19.982648 and 79.930592 ms, at the same actual ISO within that sequence. Sources are the nine files from the [owner-standardized garage repeat](../../.scratch/shutrwise/assets/s22-ultra/camera2-probe-controlled-20261006/conditions.json). Earlier varying-light captures were excluded. No additional phone captures were needed.

The merge agent processed all three sequences. The independent audit agent fixed source regions and measurement gates before inspecting the merges, examined radiometric consistency and translation, and reconstructed the output formula from original DNGs. The [audit](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/audit/method-and-results.md) records detailed results, primary API references and limits.

## Measured results

| Repeat | Middle RAW saturated samples | Short RAW saturated samples | Median dark-region signal, middle → long |
| --- | --- | --- | --- |
| 01 | 9484, 0.07903% | 0 | 33 → 135 codes |
| 02 | 9463, 0.07886% | 0 | 33 → 134 codes |
| 03 | 9485, 0.07904% | 0 | 33 → 133 codes |

Signal codes are black-subtracted source values at fixed ISO, before white balance or display adjustments. Their increase is consistent with the longer exposure collecting more light. It is not a measured SNR improvement. Every middle-saturated sensor coordinate has an unsaturated short-source sample. The small saturated fraction and alignment uncertainty prevent treating that as accurately recovered important detail everywhere.

The long exposure stays below the conservative near-white threshold throughout the preselected dark region, but clips about 30% of the preselected bright-wall region. This is the useful exposure trade-off the experiment illustrates. All four original audit regions have zero middle-frame clipping. A separate highlight crop is exploratory: it uses the fixed source-only tile with most middle clipping in repeat 01, rather than a region selected for a pleasing merge result.

The [repeat 02 comparison](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/merge/main-bracket-02/comparison.png) uses matching rendering. The [lifted dark crop](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/merge/main-bracket-02/crop-dark_lower_left.png) applies the same gain 16 to both images. Its merged side looks less grainy. That is a qualitative observation of this research rendering, with no owner preference result or independent noise/texture separation.

## Processing and alignment

The scientific merge subtracts each CFA channel's black level, normalizes by the white-to-black range and actual exposure, then takes an exposure-weighted average. Weights taper near saturation and reach zero at 98% of the usable signal range. Negative noise samples remain in float masters. Saturated contributions are excluded before color rendering. There is no generated imagery, learned denoising, sharpening or automatic brightness fitting.

Both paths use the middle frame's white balance and the same half-resolution Bayer-cell RGB construction, global tone curve and display gain. The images are white-balanced sensor RGB, with no calibrated camera-to-sRGB conversion or DNG lens corrections. They support a controlled comparison rather than a claim about natural color or a finished Lightroom edit.

The independent audit found translations up to roughly two raw pixels in some pairs. OIS was enabled, but these data do not establish the cause of movement. Two canonical variants are preserved:

- [Unaligned results and parameters](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/merge/summary.json) preserve native CFA coordinates. Small shifts can create edge artifacts.
- [Aligned control](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/merge-aligned/summary.json) applies the estimated global translation separately within each CFA plane, with conservative saturation and boundary rejection. It never mixes Bayer colors. Bilinear interpolation can itself smooth grain; global translation is not deghosting or a validated local registration solution.

Source ratios also vary spatially. Lighting flicker, motion, noise and HAL processing remain possible contributors. Alignment is a diagnostic control, not proof the finished merge is artifact-free. The audit verifies the output arithmetic and bounds what the visual difference can establish.

## Costs

The [independent source-cost record](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/source-costs.json) records 24,029,520 bytes for one DNG and 72,088,560 bytes for a bracket, exactly three times the source storage. Total sensor integration is 104.908902 ms versus 19.982648 ms, or 5.25 times the budget. This is not elapsed shutter latency.

On this Debian host, canonical unaligned processing took 3.86–4.11 seconds per sequence; the aligned control took 4.99–5.97 seconds. These include decoding, analysis, large float-master writes and PNG rendering. They do not measure on-phone performance, battery cost or capture delay. Stored float arrays/TIFFs are experimental intermediates, not a proposed app storage format.

## Sources, reproduction and integrity

Original DNGs and capture metadata remain unchanged. The [artifact index](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/README.md) links conditions, sources, output manifests, numerical results and review images.

The [final verification record](../../.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/verification.json) confirms original source hashes, canonical output/audit hashes, float-master shapes and finiteness, and matching archived processing source. Local documentation links, whitespace and tracker validation passed.

Merge source is archived on `prototype/raw-bracket-comparison`, commit `7410de66dd4aa33bdb0c23fb9b25730de0143216`, with `comparison/compare.py`, pinned requirements and a reproduction README. Audit source is archived on `research/raw-comparison-audit`, commit `3a6766db4ff5355a16a6fb96f1c7307a43a69961`, with verification commands recorded in the audit. Both are isolated from product code. The canonical merge summaries identify the archived processing script SHA-256. `merge-first-diagnostic` preserves the initial exploratory output and is excluded from the final comparison.

Open the merge branch in a separate checkout, install its requirements in an analysis virtual environment, then run:

```bash
python comparison/compare.py --source /path/to/camera2-probe-controlled-20261006 --output /path/to/new/results
```

For the aligned control, add `--shifts-json /path/to/raw-bracket-comparison-20261006/alignment-shifts.json`. The source README describes the precise formula, transforms, masks and limitations. Each output directory must be new.

## Next worthwhile control

The middle baseline was automatically metered near ISO 1160 at 20 ms. It is not the best single exposure established for this supported static scene. A concrete next comparison is a longer, lower-ISO single exposure, for example approximately 80 ms near ISO 290, captured alongside brackets with fixed focus, white balance and framing. This could collect more light at similar nominal brightness, but actual gain and clipping behavior need measurement. The current long same-ISO frame alone is another useful control, with its highlight-clipping cost visible in the sources.

Test that simpler stability-aware single-exposure choice before attributing value to adaptive bracketing or adding a model. The owner has selected the camera-led starting interaction; output workflow, delay tolerance and detailed controls remain open. This experiment does not resolve those human decisions or the target S25 evidence task.

That next control was subsequently performed with fresh matched sources. See [Longer, lower-ISO single versus a RAW bracket](long-single-control-20261006.md). It demonstrates a stronger single-RAW baseline and bounds the bracket's remaining trade-off. The original experiment and its source conditions remain preserved.
