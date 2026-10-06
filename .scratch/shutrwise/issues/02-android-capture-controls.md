---
kind: decision
status: resolved
type: research
execution: agent
parent: ../map.md
blocked_by: []
---

# Establish Android capture controls and measurement gaps

## Question

Which Android capture controls and RAW metadata can support an adaptive capture planner, and which capabilities must be measured on the actual Galaxy S25 Ultra?

Use Android primary documentation to investigate manual sensor control, RAW/DNG, logical and physical cameras, exposure sequencing, request/result timing, and relevant CameraX or vendor-extension limits. Distinguish an API contract from a device guarantee. Produce a capability-measurement checklist; do not claim actual lens access, resolution, burst rate, or photographic quality without device evidence. This ticket resolves the documented boundary and the remaining measurement gaps, not those device measurements.

## Comments

Research is claimed by `/root/android_controls`. Findings will be recorded on `research/android-controls-20261006` in the isolated worktree `/tmp/shutrwise-research-rf99787i/android-controls`, then linked here. Device measurements remain separate.

### Research resolution, 2026-10-06

Evidence: [android-capture-controls.md](../../../docs/research/android-capture-controls.md). Research branch `research/android-controls-20261006`, commit `4ef41afcb784e9c421a1dc63d2c44d0ef6797a2e`. The root session reviewed and imported the committed asset without modification.

## Answer

The documented public API boundary and measurement checklist are established. RAW and manual sensor control are separate per-camera capabilities. CameraX supports RAW and RAW+JPEG, so RAW alone does not decide the framework choice. Camera2 offers per-request exposure bursts and detailed results, but cadence, usable streams, complete saved outputs, lenses, and sensor structure require on-device tests. Public APIs and extensions do not promise Samsung first-party pipeline equivalence or all source inputs. The linked note contains primary citations and a seven-step probe checklist.

Scope of resolution: documentation and a method for measuring missing facts. The phone has not been tested; no framework, algorithm, or product direction is selected. Capture trials and the evidence task retain those decisions and measurements.
