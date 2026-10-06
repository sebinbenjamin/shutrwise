# Independent audit of one RAW versus a bracket merge

The nine standardized S22 source files support a narrower positive finding: a longer exposure supplies more unsaturated shadow signal, while a shorter exposure supplies samples where the middle exposure clips. A deterministic merge demonstrates that trade-off with preserved originals. The current data do not establish that bracketing beats the best single exposure, improves sensor dynamic range by a measured number of stops, or produces a preferred photograph.

## Method fixed before viewing merge results

[Protocol](protocol.md) records preselected regions and gates. Regions were chosen from the existing source contact sheet before independent pixel measurements. The alignment and radiometric caution rules were then fixed from source-only diagnostics before inspecting merge renders; this timing is explicit. No regions were moved to make the merge look better. Each middle exposure is compared to its own bracket; repeats are not pooled as globally identical exposures.

The independent script reads full 4000×3000 mosaic coordinates, subtracts per-channel metadata black levels, uses actual shutter×ISO normalization and compares identical CFA sites. Overall percentages deliberately match the probe's full-mosaic convention; they are not an active-area crop or a count of independent RGB pixels. Rawpy documents channel black levels, visible/full raw arrays, Bayer color indexes and metadata saturation levels in its [primary API](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html). The script estimates translation from phase-only correlation of log green-cell means and a parabolic peak; it does not register or resample sources. A synthetic two-green-cell down/right translation recovered the expected opposite shift to within 0.001 raw pixel, validating sign and implementation on an artificial translation, not real-scene subpixel accuracy.

Source scripts are archived on branch `research/raw-comparison-audit`, commit `3a6766db4ff5355a16a6fb96f1c7307a43a69961`, in `audit/source_audit.py` and `audit/verify_merge.py`. No production source was merged into develop. The existing checkout is `/tmp/shutrwise-raw-audit`.

## Independent source results

[Machine-readable source metrics](source-metrics.json) contain all ROI distributions, metadata, source SHA-256 hashes and tiled ratio diagnostics.

| Run | Middle saturated samples | Short saturated samples | Dark ROI median codes: middle → long | Towel median codes: middle → long |
| --- | ---: | ---: | ---: | ---: |
| 01 | 9484 (0.079033%) | 0 | 33 →135 | 39 →155 |
| 02 | 9463 (0.078858%) | 0 | 33 →134 | 38 →154 |
| 03 | 9485 (0.079042%) | 0 | 33 →133 | 39 →154 |

Every middle-saturated sensor coordinate has an unsaturated short-exposure sample. That is exposure support under a same-coordinate assumption, not proof every clipped scene highlight has been accurately recovered. These samples occupy a tiny part of the frame, and their photographic importance has not been judged. None of the four preselected regions contains middle-frame saturation. Thus the preselected ROIs cannot independently establish a visible highlight improvement; the whole-frame source mask supplies the limited clipping evidence.

The long exposure remains below 98% saturation in 100% of the dark ROI and 99.69–99.73% of the towel ROI. It clips 29.78–31.44% of the bright-wall ROI. This documents the shadow/highlight trade-off. The right-metal region chosen from the preview actually samples a very dark strip: median signal 4 codes in the middle and 16 in the long exposure. Its gated ratio sample counts are too small and selected to interpret as broad radiometric validation. It was retained rather than retargeted.

Long/middle gated whole-frame normalized medians are 1.000,1.003,1.000. Short/middle medians are 1.008,0.958,0.966; tile medians and some ROI medians differ further. Example bright-wall short/middle medians are 1.065,0.935,0.954. Noise, selection, spatial misalignment, lighting flicker and HAL processing are possible causes; these data do not isolate one. Constant focus/white balance within a bracket is helpful but does not resolve those causes.

| Run | Estimated short-to-middle translation (dy, dx), raw pixels | Estimated long-to-middle translation (dy, dx), raw pixels |
| --- | --- | --- |
| 01 | (-1.966,+1.937) | (-1.350,+1.274) |
| 02 | (-1.104,+1.128) | (+0.021,-0.004) |
| 03 | (-0.625,+0.538) | (+0.094,-0.086) |

Runs 01 and 02 exceed the conservative one-raw-pixel alignment caution rule. These are diagnostic estimates, not calibrated registration ground truth. The merge implementation's coarse 16-pixel phase check reporting zero shift cannot rule out these smaller movements. OIS was enabled in all source results. No causal attribution to OIS, camera motion or subject movement is made.

## Merge correctness and qualitative rendering

The independent [verification record](merge-verification.json) reconstructed the unaligned merge directly from sources. The single-RAW baseline equals its source formula exactly; merge masters agree within 1.14×10^-7 normalized signal. All outputs are finite. Saturated samples have zero merge weight; no coordinate exhausts all source weights. Those numerical invariants pass.

Code inspection confirms per-CFA black subtraction, normalization before weighting, near-white rejection before Bayer-cell RGB construction, identical middle-frame white balance for both paths and identical display gain/transfer. The half-resolution sensor-RGB display is a research rendering, not a calibrated color conversion or a Lightroom comparison. Channelwise tone mapping can change color appearance; because both paths share it, it does not manufacture an asymmetric processing advantage, but it still limits conclusions about natural color or final edit quality.

The identical shadow-lifted run 02 crop visibly shows less grain in the merge. That is a qualitative observation of this derived display, with no photographer preference result and no independent signal/noise separation. Spatial variance of textured objects is not used as a noise estimate. The experiment is not an [EMVA1288 camera characterization](https://www.emva.org/standards-technology/emva-1288/): it has no calibration sequence to quantify sensor SNR or DR, and preprocessing remains uncharacterized.

At middle-clipped coordinates the merged unaligned radiance medians exceed the baseline's fixed 1.0: 1.109,1.222,1.097. Some low deciles fall below 1.0 despite middle clipping. Misalignment and radiometric inconsistency make a claim of accurate recovery at every coordinate inappropriate. The merge remains an informational demonstration with possible edge artifacts, especially run 01.

## Global-alignment control

A subsequent diagnostic variant applies the independent provisional translations to each CFA-color plane separately, preserving the original unaligned output. It uses first-order interpolation and rejects any contributing footprint touching near-white pixels or lying outside the image. SciPy documents the [shift operation and boundary behavior](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.shift.html). This is a global translation test, with no local warp, deghosting or geometry ground truth.

The independent [aligned-master verification](aligned-merge-verification.json) confirms the same baseline, finite float output, no contribution from rejected footprints, no exhausted-weight coordinates, and formula agreement within 1.27×10^-7. Both final output sets identify source script SHA-256 `66a8393b18b89577eb5d756cd2fbffd744c00b15963d63c663cf7eb18e04dbbc`, matching the file inspected and merge source commit `7410de66dd4aa33bdb0c23fb9b25730de0143216`. [Aligned control review](aligned-control-review.json) records displacement and residual details.

Median green disagreement improves for long exposures and short exposures in runs 02/03, but worsens for run 01's short exposure: 0.00834→0.00958 normalized radiance. Samples entering that check differ slightly at boundaries. The improvement elsewhere does not validate a uniform geometry correction. First-order interpolation itself smooths grain and detail, so any quieter aligned rendering cannot be assigned entirely to capture-data quality. Run 01's aligned towel crop remains textured but smoother; this is not a resolution measurement.

The merge agent additionally selected a clipped-highlight tile from source saturation, after the original preselected ROIs were found not to clip. This exploratory source-driven crop is appropriate for inspecting the affected area, but it is not one of the originally fixed ROIs or an independent photographer assessment. Its tiny bright-object region shows a rendering difference; accurate radiometric recovery and photographic importance remain bounded by alignment and illumination uncertainties.

## Costs and next decision

Each middle source is 24,029,520 bytes; its three-file bracket is 72,088,560 bytes, three times the source storage. Sum of sensor integration is 104.908902 ms versus 19.982648 ms, a 5.25× budget. This does not measure wall-clock capture latency because readout/captures can overlap. Desktop decode/merge/render times are not phone-runtime performance.

The baseline was AE-selected near ISO 1160 at 20 ms despite a fixed phone. A concrete untested alternative is a single approximately 80 ms exposure near ISO 290, which could collect more light while retaining approximately the baseline output brightness under a simple linear gain model. Actual analog gain, full-well and clipping behavior must be measured; the outcome is not assumed. Compare that tripod-aware single exposure against brackets next. The already available  +2 EV same-ISO source alone is also a useful analysis control: it supplies most merged dark-region weight but clips bright regions.

Verdict: successful source-preserving merge experiment; limited evidence of additional exposure support and qualitatively quieter lifted shadows. Alignment/illumination concerns and a weak auto-metered single baseline prevent a broad capture-quality or optimal-strategy claim. No Samsung comparison, S25 inference, adaptive-bracketing win, AI requirement or product-superiority conclusion follows.

## Reproduce the audit

From the archived source checkout, run the scripts with the existing RAW-inspection Python environment, passing the standardized source directory and an output JSON path. `source_audit.py SOURCE OUTPUT` reproduces independent source statistics. `verify_merge.py SOURCE MERGE OUTPUT` verifies unaligned masters; add `--shifts-json alignment-shifts.json` and select `merge-aligned` for the diagnostic variant. Use a new output path when independently reproducing evidence. The protocol and results here remain separate from the capture originals.
