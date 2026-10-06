# Session retrospective, 2026-10-07

Reviewed the current T3 conversation, including its durable messages through position 1193, the current camera tooling, tracked configuration, evidence metadata and recent commits. Recommendations below are ordered by severity. Existing Bayer extraction, per-frame black normalization, ADB selection and subset-status fixes are already landed; they should be protected rather than reimplemented.

## 1. Enforce device lifecycle in the tooling

The phone was found awake with the probe foregrounded after the experiments. Commit `7cab307` added a cleanup instruction to AGENTS.md, but `batch.py` still has no cleanup finalizer and `probe/run.py` only force-stops the app before starting it. An instruction changes agent behavior; it does not automate the standalone script.

Add cleanup at the outer capture-batch boundary, on success, failure and interruption: stop the probe after export or failure handling, close the run-owned agent-device session if present, then sleep the selected phone. Record cleanup outcomes without hiding the capture error. Keep the phone available between quartets; sleeping it after each child runner would break the batch. Enforce exclusive camera ownership across automation entry points rather than relying only on the current instruction. A mocked process test should prove cleanup ordering and failure handling without touching a phone.

## 2. Add an automated guardrail

No tracked pre-commit hook, CI job or repository lint/check command was found. The session introduced undefined `original_x` and `MIDDLE_STRUCT` references and accidentally changed `hexdigest()` to `hexsha256_bytes()`. Compilation alone did not catch those runtime mistakes. The analysis branch also initially ignored `--camera-ids` and overwrote other camera statuses during subset reruns.

Add one no-phone check command with local lint and a local Git gate. GitHub CI is deferred per the owner’s instruction on 2026-10-07. Use an undefined-name linter plus targeted regressions for digest helpers, subset selection/status preservation and device cleanup. Protect the measured RAW cases with small fixtures: GRBG and RGGB mosaics, black levels differing by frame, and all-near-white shortest-source fallback. Keep formula reconstruction separate from production helpers so the verifier retains its value. A useful minimum is deterministic checks, not another prose coding rule.

## 3. Make evidence and prototypes recoverable

The root ignore rule excludes every non-Markdown file under the evidence trees. That includes source DNGs, capability/result JSON, manifests and the HTML interaction prototype. A Git clone can recover the reports but cannot recover those artifacts. No archive/restore procedure is documented in the repo; this does not establish whether the homelab has external backups.

Track small prototype source and compact evidence indexes outside the ignored capture trees. Store large originals and scientific outputs in an explicitly documented archive with checksums and a restore command. Keep the large binary corpus out of ordinary Git history.

## 4. Derive report facts from recorded metadata

The session corrected camera-facing descriptions and a median-versus-distribution claim while writing the combined report. Another current discrepancy remains: the report calls main/front mosaics GBRG, while the saved pattern `[[1,0],[2,3]]` with color description RGBG spells GRBG in row-major order. The image-processing code uses the actual pattern; this discrepancy is in the prose/table.

Generate camera coverage, CFA labels, clamps and cost tables from saved JSON. Check those generated values against the report. Keep photographic interpretation written separately, with uncertainty explicit. This provides a deterministic check for copied facts rather than asking reviewers to remember every value.

## 5. Improve navigation and tool output

Early captures depended on temporary prototype worktrees; reusable tools and the development-phone guide now provide a durable route. Add a short AGENTS.md pointer to that existing guide for camera setup, capture resumption and streaming troubleshooting. Keep detailed CLI instructions in version-matched tool help. AGENTS.md is still small; there is no reason to add a large standards section.

A compact status command should report device/camera coverage, acquisition completion, analysis failures and next commands. The session repeatedly read large metadata/logs or inspected multiple paths to reconstruct this state. Stream file hashes and distinguish source manifests from derived-output manifests to avoid unnecessary full-tree rescans while retaining integrity checks.

## Recommended order

Implement lifecycle cleanup and the no-phone check gate first. Follow with artifact recovery and metadata-derived reporting. These are recommendations; this retrospective adds this note without modifying capture behavior or waking the phone.

The owner requested an implementation plan for all five items, with local lint/gating and no GitHub CI yet. See [the implementation plan](../plans/retro-improvements-20261007.md).


## Implementation and validation — 2026-10-07

All five recommendations are implemented. The owner confirmed regular VM backups and asked us not to add separate RAW backup tooling. Git now preserves the capture-flow prototype and compact evidence indexes; image bytes and full derived outputs remain covered by those VM backups. Source verification uses recorded streaming hashes after restoration.

The local gate runs focused Ruff checks, 16 regression tests, maintained-link checks, prototype syntax/state checks and metadata-derived report freshness checks. The installed pre-commit hook checks the staged snapshot. A deliberately broken staged fixture was rejected even after an unstaged fix; staging the fix passed. No GitHub CI was added.

Lifecycle tests cover success, failure, signals, competing leases, inherited batch ownership, cleanup failure and output refusal without side effects. A real capability-only S22 run completed without photographs: the probe process was absent afterward, ADB sleep succeeded, and display diagnostics reported OFF. The saved cleanup record and [post-cleanup state](../../.scratch/shutrwise/assets/s22-ultra/retro-cleanup-validation-20261007/post-cleanup-state.json) preserve those observations. Future capture runs need an unlocked phone.

All indexed historical sources passed explicit checksum verification. Reprocessing three dark ultrawide quartets reproduced 45 scientific masters/previews byte for byte, with independent formula verification. Zero-signal brightness ratios now report a missing value instead of infinity. These checks protect the existing S22 evidence; they establish no S25 image-quality result.

Report tables derive CFA spelling from numeric patterns and color descriptions, alongside actual exposure/ISO, auto settings, focal lengths, bracket spacing, clipping, calibration and costs. Offline status offers detailed logs with `--verbose`, distinguishes failed physical access from photographed paths and recommends retries using fresh output roots. Acquisition and derived manifests remain separate.
