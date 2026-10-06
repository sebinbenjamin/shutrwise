# RAW bracket comparison artifacts

Canonical interpretation: [One RAW versus a bracket merge on the S22 Ultra](../../../../../docs/research/raw-bracket-comparison-20261006.md).

| Artifact | Purpose |
| --- | --- |
| [Source conditions](../camera2-probe-controlled-20261006/conditions.json) | Owner-standardized garage setup and original capture limits |
| [Source dataset manifest](../camera2-probe-controlled-20261006/artifact-manifest.json) | Original DNG, metadata and preview hashes |
| [Source costs](source-costs.json) | Independently checked source hashes, storage and integration budget |
| [Audit protocol](audit/protocol.md) | Source regions, gates and caution rules |
| [Independent audit](audit/method-and-results.md) | Source facts, output checks and interpretation |
| [Final verification](verification.json) | Original/canonical artifact hashes, source-code match and repository checks |
| [Unaligned summary](merge/summary.json) | Canonical native-coordinate merge, parameters and software |
| [Aligned summary](merge-aligned/summary.json) | Canonical global-translation control and interpolation limits |
| [Alignment input](alignment-shifts.json) | Independent signed shifts supplied to the aligned control |
| [Unaligned artifact manifest](merge/artifact-manifest.json) | Generated masters, images and metadata hashes |
| [Aligned artifact manifest](merge-aligned/artifact-manifest.json) | Generated control hashes |
| [Repeat 02 full comparison](merge/main-bracket-02/comparison.png) | Middle RAW left, three-RAW merge right, matching display transform |
| [Repeat 02 lifted dark crop](merge/main-bracket-02/crop-dark_lower_left.png) | Same gain 16 applied to both images |
| [Repeat 02 aligned highlight crop](merge-aligned/main-bracket-02/crop-source_selected_clipped_highlight.png) | Exploratory fixed source-selected region, not a predeclared audit ROI |

Each canonical run directory contains original-source references, float32 mosaic `.npy` masters, float32 sensor-RGB TIFFs, matched PNG previews/crops, masks and metrics. Float masters preserve values beyond the middle exposure's saturation and retain signed noise samples; they are derived outputs rather than additional RAW source captures.

`merge-first-diagnostic` preserves the first unaligned processing attempt before the final script revision. Its script hash differs from the archived final source. It is historical diagnostic evidence, not the canonical comparison. Reproduction and product discussion should use `merge` and `merge-aligned`.
