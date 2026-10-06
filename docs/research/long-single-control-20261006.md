# Longer, lower-ISO single versus a RAW bracket

The S22 control experiment supports a useful simpler capture choice. An approximately 80 ms RAW near ISO 282 looks less grainy than a 20 ms auto-metered RAW near ISO 1130, with similar brightness and clipping. A three-source bracket merge looks quieter still, but requires three original files and 31.25% more summed integration than that longer single.

Two delegated agents captured, processed and independently audited three fresh four-frame sequences on 2026-10-06. All twelve original DNGs passed capture checks. This is evidence for comparing capture strategies in the tested scene; it does not establish the best possible single exposure, calibrated SNR/dynamic range, Samsung superiority or S25 behavior.

## Matched capture

Each camera-0 session metered once and held focus and white balance across four requests. Frames 0–2 form the fixed-ISO -2/0/+2 bracket. Frame 3 uses the same long shutter as frame 2, with a lower ISO chosen to maintain approximately the middle frame's shutter×ISO product. Exposure and ISO requests were bounded by advertised capabilities, with plans and actual results retained.

| Quartet | Short / middle / long shutter | Actual bracket ISO | Actual longer-single ISO |
| --- | --- | --- | --- |
| 01 | 4.995662 / 19.982648 / 79.930592 ms | 1132 | 283 |
| 02 | Same | 1126 | 281 |
| 03 | Same | 1129 | 282 |

The actual candidate-to-middle shutter×ISO ratios are 1.000000, 0.998224 and 0.999114. All four files in each session have consistent focus, white-balance gains and reported AWB lock. Sensor image/result/start timestamps match, and TIFF exposure/ISO tags match Camera2. Every DNG contains a 4000 × 3000 GRBG mosaic; per-file black and white levels were checked rather than presumed equal across ISO.

The [conditions record](../../.scratch/shutrwise/assets/s22-ultra/long-single-control-20261006/conditions.json) distinguishes this new capture from the earlier garage tests. The view remains broadly comparable, but framing and objects differ. Earlier brightness values are excluded. Illumination, flicker and stability were not independently measured or freshly owner-confirmed; comparisons use the sources within each new quartet.

## Result and interpretation

The [primary shadow comparison](../../.scratch/shutrwise/assets/s22-ultra/long-single-control-20261006/comparison/control-01/crop-dark_lower_left.png) shows metered single, bracket merge and longer/lower-ISO single, left to right. All use the same shadow lift, white balance and display curve. The longer single shows less visible color grain than the metered middle; the merge appears quieter still. This is a qualitative research-render observation, not a measured SNR gain or owner preference result. Towel texture remains visible; no independent resolution metric was measured.

Quartet 01 is the primary qualitative example because independent source-only translation estimates stay below 0.10 raw pixel for all its sources, satisfying the predeclared registration caution. Selection is based on that diagnostic rather than a pleasing rendering. Candidate displacement in quartets 02/03 is approximately 1.64/1.55 raw pixels from the middle, limiting fine-detail conclusions. No alignment interpolation or deghosting was used in the primary outputs.

| Quartet | Middle RAW clipping | Longer/lower-ISO RAW clipping | Long/high-ISO RAW clipping | Short RAW clipping |
| --- | --- | --- | --- | --- |
| 01 | 0.05039% | 0.05239% | 7.98236% | 0% |
| 02 | 0.05236% | 0.05323% | 7.93496% | 0% |
| 03 | 0.05193% | 0.05396% | 7.95693% | 0% |

The candidate single has similar, slightly greater clipping than the metered RAW. Improved highlight headroom relative to that middle frame is not established. The bracket's shorter source supplies unsaturated samples at the small middle-clipped areas, subject to geometry and illumination caveats. Whole-mosaic percentages do not judge the photographic importance of those areas or prove accurate recovered detail.

The same-shutter high-ISO/low-ISO pair helps check the gain trade-off separately from shutter time. Its unsaturated source ratios approximately agree with nominal ISO scaling in the tested ranges. This is not an absolute analog-gain or photon-count calibration. Lower ISO alone does not collect more light; the longer shutter changes integration. The [independent audit](../../.scratch/shutrwise/assets/s22-ultra/long-single-control-20261006/audit/method-and-results.md) records the source ratios, per-CFA measurements and primary API references.

## Processing and costs

The deterministic bracket merge uses only frames 0–2, with black subtraction, exposure normalization and near-white rejection before Bayer-cell RGB construction. The longer single receives only the disclosed nominal shutter×ISO adjustment, at most 0.178%, rather than an image-fitted brightness correction. Signed float masters precede display operations. All paths share white balance, global gain and tone curve, with no learned processing, generated imagery, sharpening or denoising. Outputs are half-resolution white-balanced sensor RGB, not a calibrated camera-to-sRGB or Lightroom rendering.

The [source-cost record](../../.scratch/shutrwise/assets/s22-ultra/long-single-control-20261006/source-costs.json) records one DNG at 24,029,520 bytes versus a bracket at 72,088,560 bytes. The longer single integrates for 79.930592 ms versus the bracket's summed 104.908902 ms. The bracket therefore uses 3× original-file storage and 1.3125× integration. The four-frame experimental burst is a measurement procedure, not a proposed user capture workflow. These sums do not measure elapsed shutter latency.

Desktop decoding, processing, scientific-master writes and three-way rendering took 6.33, 5.81 and 5.79 seconds per quartet. This does not measure phone performance or battery use. Experimental float intermediates are not a proposed app storage format.

## Reproduction and evidence

The [artifact index](../../.scratch/shutrwise/assets/s22-ultra/long-single-control-20261006/README.md) links original captures, conditions, exact metadata, derived float masters, PNG comparisons, hashes and independent checks. Original and historical source files remain preserved.

Capture/comparison source is archived on `prototype/long-single-control`, commit `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`. Audit source is on `research/long-single-control-audit`, commit `a5b3c77e485dd425a8f4ad3fedfbe9075a815a2f`. Open these branches in separate worktrees. The capture branch's `comparison/README.md` gives pinned dependencies and exact commands:

```bash
python3 probe/build.py
python3 probe/run.py --action capture --camera-id 0 --mode control --output /path/to/new/captures/control-01
```

Repeat with new `control-02` and `control-03` directories and `--skip-install`, then run `comparison/compare.py` using the analysis virtual environment and a new output directory. The existing [development setup](../development-phone.md) supplies SDK/JDK and Python paths. The debug package remains `dev.shutrwise.probe`; no personal media was accessed.

The audit independently reconstructed all three paths. Float formula errors are below 1.2×10^-7 normalized signal; baseline, RGB mapping and matching PNG transfer checks passed. Saturated bracket samples have zero weight, no location exhausts all bracket weights, and outputs are finite. These are processing checks, not proof of calibrated color or artifact-free photographs.

The [final verification record](../../.scratch/shutrwise/assets/s22-ultra/long-single-control-20261006/verification.json) confirms original capture and generated-artifact hashes, archived processing source, float-master shapes/finiteness and the installed probe APK. Documentation links, whitespace and tracker checks passed.

## Implication for exploration

A longer, lower-ISO single is now a demonstrated useful baseline in this scene. A capture planner should compare it with bracketing when motion permits, rather than treating extra frames as the default route to better source information. The bracket still offers a distinct highlight source and a quieter-looking shadow rendering, with extra files and integration. Whether that trade-off is worthwhile needs broader scenes, available Samsung baselines and the photographer's judgment. The product direction and S25 evidence task remain open.
