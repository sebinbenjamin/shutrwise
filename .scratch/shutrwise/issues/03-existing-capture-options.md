---
kind: decision
status: resolved
type: research
execution: agent
parent: ../map.md
blocked_by: []
---

# Compare Samsung and Open Camera capture options

## Question

What do current primary sources establish about Samsung Photo, Pro RAW, Expert RAW, and Open Camera as capture baselines, and what remains dependent on the exact S25 Ultra software version?

Verify the meaning of computational RAW, separate-source exposure bracketing, saved-source availability, and relevant third-party restrictions. Revisit the handoff's claim that Expert RAW lacks traditional AEB. Separate documented support, absent documentation, source-code evidence, and unresolved device behavior. Do not treat lack of a feature in documentation as proof it does not exist. Include a reproducible comparison checklist. Record Open Camera's stated license as a fact, without selecting a licensing strategy.

## Comments

Research is claimed by `/root/capture_baselines`. Findings will be recorded on `research/capture-baselines-20261006` in the isolated worktree `/tmp/shutrwise-research-rf99787i/capture-baselines`, then linked here. Device measurements remain separate.

### Research resolution, 2026-10-06

Evidence: [existing-capture-options.md](../../../docs/research/existing-capture-options.md). Research branch `research/capture-baselines-20261006`, commit `2fe94cac59100022e9015e8720f582b24d5d4548`. The root session reviewed and imported the committed asset without modification.

## Answer

The documented baseline comparison and on-device checklist are established. Samsung describes Pro RAW as single-frame and Expert RAW as a processed multi-frame Linear DNG result; output bit depth is not effective sensor precision or dynamic range. Expert RAW Multiple exposure combines images. The reviewed official documentation did not verify traditional AEB saving separate DNGs, which does not prove absence from the owner's installed version. Open Camera source supports fixed 3/5-shot individual RAW brackets subject to camera and memory requirements; its bracket stop value is an outer span, not always adjacent-frame spacing. The project states GPL v3 or later, without selecting a reuse or licensing strategy.

Scope of resolution: documented modes, source-code behavior, and a reproducible comparison checklist. Installed app features, per-camera support including selfies, actual exposure accuracy, source files, and photographic quality remain untested and belong to the later device evidence task.
