# Independent RAW-bracket audit protocol

Recorded before independent pixel measurements and before seeing merge output, 2026-10-06.

Use only the nine DNGs and metadata in `camera2-probe-controlled-20261006`. Each middle exposure is its own one-RAW baseline. Three repeats establish limited consistency, not a calibrated noise or dynamic-range measurement. User standardized lighting/position; flicker and motion remain unmeasured.

Preselected ROIs use full raw sensor coordinates, fractional bounds `(left, top, right, bottom)`: textured towel `(0.42, 0.45, 0.63, 0.80)`; dark lower-left `(0.025, 0.66, 0.175, 0.90)`; bright upper-left wall `(0.02, 0.05, 0.12, 0.22)`; narrow right metal highlight `(0.93, 0.42, 0.98, 0.62)`. Selected from the already-existing contact sheet; do not change them to favor an outcome. Source dimensions 4000×3000; exclude raw margin in overall comparisons where LibRaw identifies one, and state chosen convention.

Metrics: per-frame reported-white-level saturation and black-subtracted signal percentiles; same-coordinate middle-saturated/short-unsaturated fraction (potential exposure support, not proven recovered photographic detail); unsaturated long-exposure support in dark/towel ROIs; actual shutter×ISO normalized same-CFA ratios within signal gates. Inspect tiled ratio spread and translation using exposure-invariant log green-cell images. Ratio/phase statistics diagnose consistency and do not certify perfect alignment or absence of flicker.

Ratiometric gates are fixed: for short/middle, middle black-subtracted codes 64–600 and short >=8, below 0.80 normalized saturation; for long/middle, middle 16–150 and long >=8, below 0.80 normalized saturation. Report medians and 10/90 percentiles. Tiled and ROI ratios use these same gates, with counts. Noise/texture changes can widen these distributions; departures are not uniquely attributed to motion or illumination.

The merge must preserve linear float radiance, reject saturated source samples before rendering, use identical white balance and display transformation for baseline and merge, and avoid conflating tone mapping or brightness with data gain. No raw-mosaic spatial interpolation across CFA colors. Native-mosaic unregistered merging requires consistency checks and an explicit alignment limitation. Four-source claims such as color accuracy, full sensor DR and actual SNR improvement require additional evidence and will not be made here.

Exposure budget: bracket integrates about 5+20+80=105 ms versus its 20 ms middle exposure, about5.25× sensor integration. This is not observed wall-clock shutter latency because captures may overlap in sensor readout. The +2 EV source alone is a competing longer-exposure strategy; extra captured light is not by itself evidence adaptive brackets beat an optimally chosen single exposure.

Outputs are local derived artifacts; originals are immutable. Script dependencies use the existing RAW-inspection environment. Results cite rawpy's primary API for raw-image, channel-black-level and saturation interpretation: https://letmaik.github.io/rawpy/api/rawpy.RawPy.html .

## Rendering review rules

Fixed after the source-only diagnostic and before viewing merge output: flag an estimated translation exceeding one raw pixel on either axis as an alignment concern for the unregistered native-mosaic merge. This is a conservative engineering flag, not a validated accuracy threshold or proof lesser shifts are harmless. Reject claims of newly recovered information where all source samples are saturated or the implementation assigns saturated samples a positive contribution. Treat >5% departure of a gated regional median radiance ratio from unity as a consistency concern, without ascribing a unique cause. An edge artifact, local misalignment or inconsistent illumination bounds the conclusion to source exposure support plus a merge demonstration; do not report a quantitative quality gain. Metadata correctness and successful file output can still pass independently.
