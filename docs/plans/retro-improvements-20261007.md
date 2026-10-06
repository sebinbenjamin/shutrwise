# Implement the session retrospective improvements

Implement all five recommendations from [the retrospective](../research/session-retro-20261007.md). Item 2 uses local lint and a local check gate. GitHub CI is deferred. The owner subsequently confirmed regular VM backups and instructed us not to add separate RAW archive tooling. This plan improves research tooling and artifact handling; product direction, capture algorithms and S25 conclusions remain open.

## Delivery order

| Phase | Work | Retro item | Depends on |
| --- | --- | --- | --- |
| 1 | Local lint/check entry point and focused regression fixtures | 2 | Existing tools |
| 2 | Capture ownership and automatic device cleanup | 1 | Phase 1 |
| 3 | Tracked prototypes, evidence indexes and VM-backup documentation | 3 | Phase 1 |
| 4 | Metadata-derived report tables and report checks | 4 | Phase 3's index format |
| 5 | Compact status output, manifest efficiency and navigation | 5 | Phases 2–4 |
| 6 | Full local acceptance pass and documentation | All | Phases 1–5 |

Make each phase independently reviewable. Preserve original captures and historical audit outputs. Add validation around the already landed Bayer, per-frame black-level and subset-status fixes.

## Phase 1: Local lint and check gate

Add `pyproject.toml` with a focused Ruff configuration and a pinned local development dependency file. Start with syntax/undefined-name checks and fix their findings without imposing an unrelated formatting rewrite. Use the existing pinned analysis dependencies for the small numerical fixtures.

Provide `python3 tools/check.py` as the single gate. It must return nonzero when a required check fails or a required dependency is unavailable, and print a concise result with the failing command or fixture. Normal checks require no phone, browser, network, SDK build or full capture archive.

The gate runs:

- Ruff on maintained Python tools and regression fixtures. Exclude generated build files and immutable historical scripts in capture archives.
- Focused standard-library test runners, using NumPy and existing analysis dependencies where needed.
- Documentation/reference checks for maintained local links and required tool files.
- Generated-report freshness checks against tracked compact evidence indexes, once Phase 4 lands.
- JavaScript syntax and state regression checks for the tracked capture-flow prototype, once Phase 3 lands. These must not open a browser.

Initial regressions cover the actual failures from the session: correct digest output, camera subset selection, preservation of other cameras' analysis statuses, all Bayer green positions, per-frame black 65/64 normalization, and all-near-white shortest-source fallback. Keep formula verification independent of pipeline helpers. Add cleanup, ownership and restored-source fixtures as those features land.

Add a tracked `.githooks/pre-commit` and an explicit local installation command. Inspect existing hook configuration before installation and preserve or integrate existing user hooks. The hook calls the same gate against the staged source snapshot; the manual command checks the working checkout. Do not silently approve commits when dependencies are missing. Document local setup and the explicit gate command in README. Create no GitHub workflow.

Acceptance: the local gate passes on current code, fails on fixtures representing the session's mistakes, and the installed pre-commit hook rejects a deliberately failing staged fixture without committing it. Checks leave the phone asleep and require no RAW corpus.

## Phase 2: Device ownership and lifecycle cleanup

Add one lifecycle helper used by the capture entry points. Acquire a cooperative host lock keyed to the selected device, using a non-identifying digest in the lock filename. Hold it for the entire acquisition and cleanup. Batch child runners inherit the ownership lease rather than trying to acquire the same lock again. Standalone probe runs acquire their own lease. A second cooperating run fails promptly with a useful ownership message.

The outer capture batch handles normal return, exceptions, timeout, Ctrl-C and termination. In cleanup, stop only apps launched by that run, close only an explicitly owned agent-device session using its exact launcher/config/session flags when applicable, and send ADB sleep keyevent 223 to the selected phone. Record the cleanup outcome and retain the original capture failure if cleanup also fails. Release the lock last. Keep saved files and originals intact.

RAW acquisition does not open an agent-device session. Any subsequent device inspection starts after the batch completes, follows the repo's device-tool workflow, and performs its own cleanup. The cooperative lock governs repo entry points and the verification wrapper; external T3 or third-party processes do not automatically honor it. Retain the AGENTS.md camera-ownership instruction for those interactions and surface actual camera-access failures.

Default behavior leaves the phone dark. Allow an explicit `--keep-awake` option for deliberate consecutive runs; it still stops the probe, closes owned sessions and releases ownership. Print that a sleeping phone needs unlocking before another capture. Desktop-only analysis does not wake, stop or sleep the phone.

Acceptance: mocked process tests prove cleanup on success, failure and interruption, correct ordering, idempotence, original-error preservation, selected-device targeting and rejection of competing owners. A scoped real-device cleanup check confirms the probe is stopped and the display sleeps. Any capture needed for that check waits for a freshly unlocked phone and uses a new evidence root.

## Phase 3: Recoverable artifacts

Move or copy the existing capture-flow HTML source into tracked `prototypes/capture-flow/`, update its references and preserve the original exploratory artifact. Keep small source files outside the ignored binary capture trees.

Create a tracked `evidence/indexes/` format containing device/condition/run identity, camera path coverage, source hashes and sizes, relevant capture/calibration metadata, failures, and capture/analysis code provenance. Store no unique phone serial. Separate exact recorded values from interpretations. Include enough compact facts for report generation and local checks without DNG access.

Rely on the owner's regular VM backups for large originals and derived outputs. Document that Git restores code and compact indexes while image bytes require the VM backup. Provide explicit streaming hash verification against the tracked index after a restore. Do not add a separate archive service or destination requirement.

Acceptance: a fresh Git checkout contains the interaction prototype and compact indexes, and source verification detects altered or missing files. Historical captures remain unchanged.

## Phase 4: Metadata-derived reporting

Build a report generator/checker consuming the tracked indexes. Derive facing, focal length, RAW dimensions, CFA spelling, per-frame black levels, auto-metered versus actual bounded settings, bracket spacing, clipping, integration and storage costs from recorded values.

Determine CFA letters from both the numeric pattern and its color description. Correct the current main/front `GBRG` report label to `GRBG`; the ultrawide remains `RGGB`. Preserve image-processing outputs, which already use the actual pattern.

Use explicit generated blocks in the current combined lighting report. Keep human interpretation outside them. A check mode computes the blocks and fails when committed facts are stale. Record missing data and failed/untested physical paths explicitly rather than implying complete hardware coverage. Distinguish medians from distributions and summed integration from elapsed capture latency.

Acceptance: report blocks regenerate identically from tracked indexes; changing a fixture fact makes the gate fail. Pattern-label and cost fixtures have known expected results. Reports retain their measured-versus-inferred limits.

## Phase 5: Navigation, status and hashing

Add a compact status command that reads experiment records and displays camera paths, lighting coverage, capture/analysis/cleanup outcomes, failures and the next valid commands. Default status is offline; it does not open a device session. JSON output supports automation, and verbose mode exposes paths to detailed logs instead of dumping them by default.

Use a streaming SHA-256 helper for large files. Keep immutable source manifests separate from versioned derived-output manifests; analysis must not rehash or modify the entire original corpus on every pass. Preserve explicit full verification for explicit restored-source checks and investigate changed files rather than trusting timestamps alone. Retain compatibility with existing manifests; avoid rewriting historical evidence merely to adopt the new format.

Add a short AGENTS.md navigation pointer to the existing development-phone guide for setup, resuming captures and stream troubleshooting. Put detailed lifecycle and gate setup in that guide and the batch README. Continue using version-matched CLI help rather than copying large command references into always-loaded instructions.

Acceptance: status correctly represents mixed success/failure and incomplete runs, keeps physical access failures distinct from photographed paths, and returns actionable commands. Hash results match known files; a large fixture is processed in bounded memory. Repeated analysis leaves source manifests unchanged.

## Phase 6: Acceptance and completion

Run the local gate, staged-hook rejection/pass checks, restored-source hash checks, report freshness check and status checks. Verify maintained links and the captured-source integrity for any real-device validation. Broaden checks only for changed behavior or failures.

Record what changed and what was actually validated in the development guide and retrospective. Local regressions are the default check; full existing-corpus validation and real-device runs are explicit checks. Do not represent code-backed cleanup as implemented until its acceptance checks pass.

Completion requires all five improvements and their checks. Regular VM backup operation remains owner-managed. No separate storage destination is needed. See the retrospective for implementation and validation results.
