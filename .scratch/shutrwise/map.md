---
kind: map
status: open
resolution_scope: planning
---

# Shutrwise

## Destination

Choose a product direction and its core experience for a Samsung Galaxy S25 Ultra photography system that helps make capture decisions while preserving RAW source material for later editing.
Finish with a clear account of its intended user, value, and evidence needed to justify the direction.

## Notes

- This is a planning effort. It does not commit to a full implementation specification or a commercial product.
- The owner is learning photography and currently has a Galaxy S25 Ultra, DJI Osmo Action 5 Pro, and a tripod. The S25 Ultra is the primary experimental device.
- Keep the photography-learning experience, dynamic range, exposure bracketing, and access to source captures central to exploration.
- A learning assistant, RAW camera, adaptive bracketing tool, comparison tool, and open-source research project remain possible directions.
- ML, natural-language intent, autonomous capture, and the separation of semantic intelligence from deterministic capture control are possibilities, not decisions.
- Target S25 RAW capabilities and Samsung application behavior remain unverified. Distinguish documentation claims from measurements on the owner's exact device and software versions.
- The spare S22 Ultra is the connected development device. On 2026-10-06, the probe collected Camera2 capabilities, decoded DNGs through all four listed paths and verified three main-camera bracket repeats after owner-standardized conditions. Earlier captures had varying light and establish technical behavior only. See [Development phone setup](../../docs/development-phone.md), the [S22 evidence record](./assets/s22-ultra/device-record.md) and [measurement report](../../docs/research/s22-camera2-probe-20261006.md). A later [all-camera lighting batch](../../docs/research/all-camera-lighting-20261006.md) verified control quartets from every listed RAW path under normal and dimmed lighting. Optimized capture strategies and target S25 behavior remain unmeasured.
- Delegated [RAW-versus-bracket](../../docs/research/raw-bracket-comparison-20261006.md) and [longer-single control](../../docs/research/long-single-control-20261006.md) experiments found useful exposure trade-offs and qualitatively less grain with a stronger single-RAW baseline. Registration/scene limits, globally optimal settings, Samsung comparisons and S25 evidence remain outstanding. This is progress within the evidence task, not a resolved product choice.
- A [Samsung baseline comparison](../../docs/research/samsung-baseline-20261007.md) completed three repeats on the S22. The saved Pro DNGs are linear RGB rather than mosaics; inspected lifted shadows look quieter, but metering/processing confounds prevent a calibrated quality ranking or a claim of custom superiority. S25 evidence remains outstanding.
- Consult wayfinder, grilling, and domain-modeling when charting or resolving decisions. Use research for external facts and prototype for concrete experience explorations.

## Decisions so far

- [Define the beginner promise](./issues/01-define-beginner-promise.md): Help beginners make deliberate capture choices, with quick capture optional and deeper learning on demand; compare capture improvements and clearer decisions while keeping output workflows open.
- [Establish Android capture controls and measurement gaps](./issues/02-android-capture-controls.md): Android exposes conditional RAW and exposure controls; the exact S25 Ultra capabilities and reliability still need measurement.
- [Compare Samsung and Open Camera capture options](./issues/03-existing-capture-options.md): Samsung describes computational Expert RAW; Open Camera supports conditional separate RAW brackets; exact installed Samsung AEB availability remains unresolved.

- [Choose capture trials and evidence thresholds](./issues/04-choose-capture-trials.md): Keep scene coverage open; compare captured data and clearer decisions separately, treating a meaningful benefit in either as a provisional reason to continue.

- [Explore capture and explanation interactions](./issues/06-explore-core-experience.md): Camera-led deliberate capture with visible duration, immediate shutter execution, optional priorities/explanations, and simple completion/cancellation; keep both output workflows for comparison.

## Not yet specified

- Whether the reusable device-evidence batch (`tools/raw-camera-experiment`) can become a first-run onboarding/calibration step in the product, characterizing a new phone's cameras and limits on setup. This is a possible future reuse of the research tooling, not a chosen product behavior.
- Further decisions and experiments may emerge if the measured camera behavior contradicts the proposed experience.
- How distribution, licensing, and project ownership constrain the selected direction once its intended use and reuse strategy are clearer.
- What model evaluation, latency, privacy, and deployment decisions become relevant if the selected direction needs a semantic model.
- What additional experience and camera constraints emerge as comparisons cover different scenes.

## Out of scope

- Full product implementation and deployment. This effort ends at a product direction and core experience.
- Commercial launch planning and a camera purchase decision.
