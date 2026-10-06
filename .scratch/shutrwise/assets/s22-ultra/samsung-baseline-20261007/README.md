# Samsung baseline comparison — 2026-10-07

Status: completed. Three Samsung Photo JPEGs, three Pro DNG/JPEG pairs and three custom four-frame RAW sequences were saved. A separate Pro JPEG smoke capture is also preserved. The nonsecure/trusted lock overlay was dismissed by ADB; no owner unlock or lock-setting change was required.

The owner authorized this experiment with “Do” after the agreed core interaction was recorded. Compare Samsung Photo, Samsung Pro RAW where available, a custom longer single RAW and the existing deterministic bracket merge on newly captured source material. Use the main rear camera, fixed phone placement, current lighting and comparable framing. Capture three repeats where practical, recording settings, mode, dimensions, source hashes and any differences in conditions. Preserve existing files; use this fresh evidence root.

Samsung Photo is a delivered-photo baseline. RAW files are also compared under documented common development settings, distinct from the delivered JPEG comparison. Report highlight clipping, visible shadow/detail differences, blur/ghosting, editing steps, repeatability and costs. Do not equate RAW clipping percentages with clipping in a processed JPEG. Summed exposure is not elapsed capture latency. Do not infer S25 behavior from S22 results, or call a capture strategy globally optimal.

Session preparation found a lock-screen overlay above Samsung Camera. Device control could open the package, but normal app interaction requires an unlocked phone. No secure unlock will be automated. The owner was asked to unlock, keep placement/lighting unchanged and reply ready.

Capture sequence after unlock:

1. Confirm Samsung Camera Photo mode, rear main 1× and framing; record any HDR/scene/settings visible. Save three new photos and identify only the files created by this experiment.
2. Check Pro mode and RAW saving without assuming it exists. Record existing preferences and restore any settings changed by the run. If supported, capture three RAW/JPEG pairs at the mode's metered settings.
3. Close the owned agent-device session and stop Samsung Camera before the RAW batch owns the camera. Keep the screen awake only for this authorized consecutive run.
4. Capture three main-camera control quartets in a fresh child root. The maintained batch saves a fixed-ISO bracket and longer/lower-ISO single, records actual controls and performs cleanup.
5. Analyze sources offline, independently verify the custom merge, inspect consistent previews, preserve original hashes, and publish a bounded report. The owner's preference/editing assessment remains a human judgment.

Default final cleanup stops apps launched by the run, closes owned device sessions and sends ADB sleep. Verify process/display state afterward. The prototype and research tooling do not constitute a product camera.


## Completed artifacts

[Samsung source record](samsung-source-record.md) preserves hashes and compact metadata. Full manifests, interaction logs and image outputs remain beside this record. [The report](../../../../../docs/research/samsung-baseline-20261007.md) records findings and limits. The maintained rendering source is `tools/raw-camera-experiment/analysis/samsung_baseline.py`; custom acquisition and independent verification use the existing batch tool.

The run's `normal` custom folder is an operational batch label, not a claim of standardized normal lighting or lux. The owner did not reconfirm light stability during this sequential run. Both Samsung and probe processes were absent afterward; sleep was requested. Display diagnostics reported OFF and DOZE_SUSPEND states, so no stronger all-displays-OFF claim is made.
