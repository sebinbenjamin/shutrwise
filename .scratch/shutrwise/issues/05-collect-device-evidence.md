---
kind: decision
status: claimed
claimed_by: /root
type: task
execution: human
parent: ../map.md
blocked_by:
  - ./04-choose-capture-trials.md
---

# Collect S25 Ultra evidence for chosen trials

## Question

Obtain the on-device records and comparison captures required by Choose capture trials and evidence thresholds so the product decision can rely on observed facts.

This is a human-assisted evidence task because it requires the owner's phone and shooting conditions. Once trials are chosen, provide a precise checklist for software versions, camera capability records, source files, and capture conditions. A minimal probe may be used if the agreed trial requires it; no full camera app is implied. Resolve with what was measured, links to assets, limitations, and remaining facts, rather than with a product recommendation.

## Comments

### Evidence collection started

Prepared the [device evidence checklist](../assets/device-evidence-checklist.md) and [device evidence record](../assets/device-evidence-record.md). The workspace has no ADB executable and no image captures in the repository. Requested the owner's Android/One UI versions and installed Expert RAW/Open Camera inventory first. No phone capability has been measured; the task remains claimed and unresolved.

### Software inventory and spare-phone offer

Recorded the owner's S25 Ultra inventory: One UI 8.5, Android 16, Expert RAW 5.0.08.2, Open Camera 1.56.2. The owner offers a spare S22 Ultra for a persistent development/test connection. Preparing that connection is authorized; device measurements must remain separate, and target S25 conclusions still require S25 evidence. Connection is not established.

### Linux/T3 connection preparation

The owner confirmed Linux, a homelab running T3, and authorized agent-browser use. Installed Google's Linux ADB platform-tools and prepared `tools/collect-device-inventory.py`. Its help and syntax checks pass; a real run correctly reports no authorized device. No phone is visible to ADB or this workspace's USB inventory.

Inspected the local T3 UI through an isolated paired browser session. Enabled Device hub and Agent device access for this environment through normal settings and verified persistence after reload. No SSH device hosts are configured; physical-phone support remains unverified. The current MCP call still reports access disabled, so tool availability has not been established by the settings change alone.

Requested the actual phone-connected host or SSH target. Added [development connection notes](../assets/development-phone-connection.md). The evidence task remains unresolved pending an authorized device connection and actual camera observations.

Installed Device hub 0.12.0 and Agent device 0.21.12 using T3's settings controls. Verified the installed status and Agent device's CLI version. Official Agent device documentation confirms physical Android support through ADB; T3 panel support remains unverified. Tracker validation passes with 8 canonical documents and no unsafe documents; whitespace checks pass. No phone data has been read.

### Connection host confirmed

The owner confirms the S22 will plug into the machine running this workspace. A fresh ADB device list is empty, and the workspace USB inventory contains only QEMU's tablet and root hub. Await physical connection and USB-debugging authorization, then establish whether USB passthrough is necessary. The current T3 MCP device list still reports agent access disabled. No phone inventory or camera measurements have been collected.

### S22 connected and software inventory collected

Verified Samsung USB passthrough into Debian and an authorized ADB connection on 2026-10-06. Collected a separate [S22 evidence record](../assets/s22-ultra/device-record.md) and timestamped JSON inventory. Observed SM-S908E, Android 16 / API 36, Samsung Camera 16.0.00.66. Scoped Expert RAW and Open Camera package queries returned no version records.

The T3 device-list call now responds but reports Android unavailable because the SDK directory is not configured, and iOS unavailable on Linux. It lists no panel devices. Direct ADB access works. No camera capture or capability probe has run; the evidence decision remains unresolved, and S25 findings still require S25 measurements.

### Repository documentation consolidated

Added a root [README](../../../README.md) that indexes the decision map, research, comparison method and separate device evidence. Consolidated operational instructions in [Development phone setup](../../../docs/development-phone.md), including Proxmox USB passthrough, verified tool versions, ADB inventory commands, the T3 Device panel limitation and remaining camera checks. The existing connection asset now links that canonical guide. This is documentation of the current state, not a new product decision or a completed camera experiment.

### S22 Camera2 probe and standardized repeat

The owner authorized the next probe experiment with "do". Installed a local Java 21/Android SDK toolchain and built a throwaway native probe on isolated branch `prototype/s22-camera-probe`, committed as `eeaf02f24cba56590990e3bcd2ec0666a0984441`. Recorded all listed/physical camera characteristics, and independently decoded DNGs captured through listed IDs 0, 1, 2 and 3. Main-camera separate -2/0/+2 EV capture works. This is a technical finding, not a choice of production camera framework or product direction.

The owner clarified that earlier lighting varied. Preserved those initial captures as technical smoke tests, excluding them from between-run quality claims. After the owner confirmed garage closed, lights on and fixed phone placement, collected three more main-camera brackets. All nine new 4000 × 3000 DNGs decoded, passed orientation and exposure/ISO tag checks, and achieved actual -2/0/+2 EV spacing with consistent ISO/focus/white-balance gains within each bracket. New runs remeter and refocus; they are not globally locked comparisons. Original sources, capture metadata, condition notes, inspection and hashes are linked by the [measurement report](../../../docs/research/s22-camera2-probe-20261006.md).

T3's device panel still reports SDK discovery unavailable despite the local SDK working for native builds. Direct ADB is sufficient for these intent-driven measurements; no T3 or VM restart was performed. S25 measurements, Samsung baseline comparisons, a documented RAW merge and capture-quality benefit remain outstanding. Keep this evidence ticket claimed and unresolved.

### RAW comparison authorized

On 2026-10-06, the owner requested "If you can do it yourself run the data experiment using subagents." Started separate merge and independent-audit agents, using only the nine standardized S22 captures. Compare each bracket to its own middle RAW with matching rendering parameters, preserve source hashes and report costs and limits. This authorizes analysis and deterministic merging of existing sources; no new phone capture or owner setup is required for this subexperiment. The target S25 task remains unresolved.

### Delegated RAW comparison completed

Both agents completed the experiment and archived source on separate branches: `prototype/raw-bracket-comparison` at `7410de66dd4aa33bdb0c23fb9b25730de0143216`, and `research/raw-comparison-audit` at `3a6766db4ff5355a16a6fb96f1c7307a43a69961`. The [canonical report](../../../docs/research/raw-bracket-comparison-20261006.md) links source integrity, unaligned and provisionally aligned variants, matched renders, float masters, output manifests and the independent audit.

The long source provides more unsaturated shadow signal; the short source supplies unsaturated samples at approximately 0.079% of middle-saturated sensor coordinates. Matched lifted shadows look less grainy. Numerical reconstruction verifies the merge formula, fixed baseline and exclusion of rejected saturated samples. Estimated translations and spatial radiometric disagreement limit artifact-free/detail-recovery claims; provisional alignment is a diagnostic control, with interpolation itself a confounder.

The bracket uses three times the RAW storage and 5.25 times the summed integration of its middle source. That auto-metered middle frame is not an optimized single exposure. Next compare a supported-scene longer/lower-ISO single exposure against brackets, with controls and conditions recorded. No calibrated SNR/DR, Samsung superiority, adaptive-planning win, owner preference or S25 conclusion was established. Keep the task claimed and unresolved.

### Longer/lower-ISO single control started

The owner authorized the proposed next control with "Okay do them now." Delegated exclusive phone capture/processing to the capture agent and independent method/results review to the audit agent. Prepare a matched four-frame sequence: fixed-ISO -2/0/+2 bracket plus a longer/lower-ISO single, with focus and white balance held in one camera session. The candidate single uses four times the metered shutter where the API permits, reducing requested ISO to preserve the nominal shutter×ISO product, with clamps and actual results recorded.

Use a fresh dataset rather than comparing against historical garage captures. The earlier garage confirmation is not independent confirmation of current light, framing or stability. Current source frames and consistency diagnostics must ground the comparison. T3 still reports SDK discovery unavailable; direct ADB is the established capture route. The user has authorized capture and analysis; further confirmation is only needed if the physical connection or setup actually requires owner action.

### Longer/lower-ISO control completed

Captured twelve fresh DNGs in three matched four-frame sessions, with actual 4.995662/19.982648/79.930592 ms bracket shutters at ISO 1132, 1126 and 1129, plus 79.930592 ms singles at ISO 283, 281 and 282. All intended capture controls, timestamp associations, TIFF metadata and within-session focus/white-balance consistency passed independent checks. Capture/comparison source is archived at `prototype/long-single-control`, commit `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`; independent audit at `research/long-single-control-audit`, commit `a5b3c77e485dd425a8f4ad3fedfbe9075a815a2f`.

The [canonical report](../../../docs/research/long-single-control-20261006.md) links original sources, conditions, three-way float/PNG outputs, metrics, hashes and the audit. The longer/lower-ISO single shows less visible color grain than the metered baseline, with similar brightness and slightly more clipping. The bracket looks quieter still and retains an unsaturated short source, at three times the RAW storage and 31.25% more summed integration than the longer single. Primary qualitative quartet 01 satisfies the predeclared source-registration caution; other repeats show shifts, and fine-detail claims remain bounded.

This completes the authorized control subexperiment. It does not establish optimal settings, calibrated SNR/DR, owner preference, Samsung superiority or S25 behavior. Keep the broader target-device evidence task claimed and unresolved; no product direction or AI requirement is selected by these measurements alone.

### All-camera lighting batch: normal and dark conditions complete

The owner asked to land the helper scripts in the repo for S25 Ultra reuse and record possible future onboarding-calibration reuse in the map, then authorized the dark capture with lights dimmed and the phone/scene fixed. The reusable batch landed on `develop` (commits `6ddd53b`, `79bdb4a` and follow-ups): shared ADB selection, one geometric ROI table, Bayer-pattern-aware green extraction, and restored `probe/inspect_dng.py`. A two-axis review was run first; its real findings were fixed and validated bit-identical against recorded camera-2 evidence. One reviewer claim (wrong capability-gate constants) was rejected after verification against `MainActivity.java` and on-device behavior.

Dark capture (2026-10-07) saved 48 DNGs: three quartets for each listed camera 0-3. Physical IDs 5-7 again failed direct open and are recorded, not photographed. The first analysis pass failed for cameras 1-3: in dark conditions their longer/lower-ISO singles carry black level 64 while bracket frames carry 65, tripping the same-metadata assumption. The pipeline correctly refused rather than mixing calibrations. The analysis was corrected to normalize per frame (as the math already did), record `quartet_black_level_per_frame`, and require only structural layout equality; camera-0 (uniform black 64) was re-analyzed under the same code for within-condition schema consistency. All four dark cameras verify, and the analyze stage now honors `--camera-ids` and preserves prior status records.

Evidence: `.scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006/{normal,dark}/` with per-condition manifests and hashes. This is device-behavior evidence on the S22 only: no calibrated noise/DR, no Samsung baseline comparison, no S25 measurement, and no product-direction choice. A combined research report is the natural next step.


### Samsung baseline comparison authorized — 2026-10-07

The owner requested execution of the proposed same-scene S22 comparison: Samsung Photo, Samsung Pro RAW where available, custom longer single RAW and bracket merge. [The experiment record](../assets/s22-ultra/samsung-baseline-20261007/README.md) records the procedure and current state. Initial app opening revealed a lock-screen overlay; no comparison photographs have been taken. Awaiting the owner's unlock and confirmation of unchanged framing/lighting. This subexperiment does not resolve target S25 evidence.


### Samsung baseline comparison completed — 2026-10-07

The owner asked whether manual unlock could be avoided. ADB wake plus `wm dismiss-keyguard` succeeded, and agent-device verified access to Samsung Camera. No lock settings were changed. Completed three Photo JPEGs, three Pro DNG/JPEG pairs and three custom main-camera control quartets; one additional JPEG-only Pro smoke capture is preserved separately. Pro's original JPEG-only setting was restored.

[The Samsung baseline report](../../../docs/research/samsung-baseline-20261007.md) preserves method, source records, measured values and interpretation limits. The inspected Pro DNG shadow views appear quieter, but exposure/processing differences prevent a calibrated ranking. The custom metered ISO was clamped and its longer-single control is not a globally optimized baseline. No custom superiority or target S25 claim follows. Custom source audits and independent verification passed. Both camera processes were absent after cleanup; display diagnostics included OFF and DOZE_SUSPEND.

This adds S22 evidence without resolving the target S25 task. Matched manual exposure/ISO comparisons and S25 measurements remain outstanding; both output workflows and the product direction remain open.
