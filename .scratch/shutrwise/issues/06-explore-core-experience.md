---
kind: decision
status: resolved
type: prototype
execution: human
parent: ../map.md
blocked_by:
  - ./01-define-beginner-promise.md
  - ./02-android-capture-controls.md
  - ./03-existing-capture-options.md
---

# Explore capture and explanation interactions

## Question

Which capture-and-explanation interaction best serves the agreed beginner promise?

Create cheap alternatives for the owner to react to, such as a proposed capture plan with overrides, intent-led capture, or automatic capture with optional teaching. Keep room for a different interaction. Use representative scenic and group/selfie situations. Compare both output workflows the owner has kept open: a usable photo with preserved RAW, and a workflow centred on later RAW editing. Include the owner's working preference for a deliberate default aimed at useful captured data, with quick capture optional. Compare short default feedback with deeper learning on demand. Avoid assuming that more elapsed time or more frames are inherently better. Make detailed learning optional. Establish the role and timing of explanations, how a beginner can express priorities, and what remains under their control. Mark simulated hardware behavior clearly; a prototype is evidence about an interaction, not proof that the camera can perform it.

## Comments

### Experience exploration started after the S22 probe

Claimed the next unblocked decision on 2026-10-06. The S22 measurements establish separate RAW output and fixed exposure control, while capture-quality benefit and S25 behavior remain unmeasured. The evidence task stays open; it is not a prerequisite for reacting to simulated experience alternatives.

Prepared [capture-flow discussion sketches](../assets/capture-flow-sketches.md) as a cheap outline for live discussion. These propose three interactions using the owner's existing deliberate-capture and optional-learning preferences. They do not select a product direction, output workflow, AI model or implementation architecture. Wait for the owner's reaction before recording an answer or resolving this ticket.

### Owner selected the camera-led starting interaction

The owner replied "Agree with 1" to the proposed camera-led flow. Record the preferred starting interaction as the camera choosing and showing a capture plan, with an optional priority adjustment and "Why?" explanation. Keep deliberate capture as the default, quick capture optional and deeper learning on demand. This settles the starting interaction; output workflow, acceptable delay and detailed override behavior remain open, so the ticket is not yet resolved.

The owner also authorized running the data experiment with subagents. The separate evidence task will compare each standardized S22 bracket against its middle RAW using a reproducible deterministic merge and an independent method/results audit. That experiment must not stand in for the owner's assessment of the experience or S25 measurements.

## Comments

### Interactive capture-flow prototype

Built a shareable single-file prototype at [.scratch/shutrwise/assets/capture-flow-prototype/prototype.html](../assets/capture-flow-prototype/prototype.html) (local asset). It drives the owner-selected "Camera chooses" interaction as a pure state module: observe → plan → capture → result → after-capture workflow, with priority overrides, mid-capture interruption, condition changes, and explanation before/after. Four guided walkthroughs (scenic bracket, group with movement, mid-bracket interruption, dim room with clamp + faster override) plus free play.

Every scene judgment is tagged SIMULATED; exposure/storage/trade-off numbers are grounded in measured S22 evidence (bracket 3× storage and 1.31× integration vs a longer single, 103.389 ms back-path shutter ceiling, dark-condition disagreement, actual=requested settings). The camera-profile block doubles as a sketch of what first-run onboarding calibration would measure on a new phone.

Prototype logic was module-tested: the initial version leaked state by mutating the scene library on condition changes; fixed by carrying the live scene inside session state. Awaiting owner reactions before resolution.


### Shutter execution agreed — 2026-10-07

Resumed this interaction decision in the same continuing thread. The owner agreed that pressing the shutter immediately executes the currently displayed capture plan, without an additional confirmation for multiple exposures. Show the expected capture duration before the shutter press. This is an estimated duration, not a claim that summed sensor exposure equals elapsed capture time.

The agreement settles confirmation behavior only. Acceptable delay, visible priority overrides, behavior during interruption and the after-capture output workflow remain open. Retain the camera-led deliberate default, quick capture option and optional explanations. No prototype or camera implementation was changed by this agreement.


### Priority controls and cancellation agreed — 2026-10-07

The owner agreed to both proposed defaults:

- Offer optional plain-language priorities, including protecting the sky, keeping faces sharp and finishing faster. Technical settings remain available on demand; selecting a priority is not mandatory before each shot.
- Cancel stops further exposures while preserving completed RAW source captures. Show what was saved and whether the intended capture plan finished. Preserved partial sources do not imply that a complete or usable merged photo exists.

This records interaction decisions, not implemented camera behavior. Automated response to changing conditions during capture remains open. Both after-capture workflows remain available for comparison as previously requested; no default output workflow is selected here.


### Finish the plan when movement changes — 2026-10-07

When asked whether movement during a bracket should automatically stop the sequence and switch to a motion-oriented single exposure, the owner chose: "Finish. Let's keep it simple."

Finish the original capture plan despite newly detected movement during the sequence. Do not automatically replace it with another strategy. This settles the movement-change interaction only; it does not require continuing through camera errors or an explicit Cancel. The previously agreed Cancel behavior remains: stop further exposures and preserve completed RAW sources. Completing the plan does not guarantee freedom from motion blur or merge ghosting.

Keep this initial interaction simple. Both after-capture workflows remain open for comparison, and actual capture duration/quality still need measurement. No camera code or prototype behavior was changed by this record.


### Resolution — core interaction agreed, 2026-10-07

## Answer

The owner chose a camera-led, deliberate capture experience for beginners:

- Propose and show a capture plan before the shutter, including estimated elapsed capture duration. Pressing the shutter executes the displayed plan immediately without a second confirmation.
- Offer optional plain-language priorities and disclose technical settings on demand. Quick capture remains optional.
- Give brief feedback before and during capture, with an optional deeper explanation afterward.
- Finish the original plan if movement begins during capture. Keep the initial behavior simple rather than automatically switching strategies.
- Explicit Cancel stops further exposures, preserves completed RAW source captures and reports whether the intended plan finished. Camera errors remain failures, not instructions to keep shooting.
- Retain both immediate-photo-plus-RAW and later-RAW-editing workflows for comparison. The owner has deliberately deferred choosing between them.

This resolves the starting interaction through the owner's live responses. It does not establish camera feasibility, acceptance of a particular measured delay, polished interface usability or a default output workflow. There is no fixed capture-time limit yet; measure actual waiting time and judge it alongside benefit in the evidence task.

The [discussion sketches](../assets/capture-flow-sketches.md) and [tracked simulated prototype](../../../prototypes/capture-flow/index.html) are assets for testing this direction. The recorded decisions above govern subsequent revisions; the current prototype has not been updated or newly reviewed by the owner in this exchange. Target S25 measurements and Samsung baseline comparisons remain outstanding in [Collect S25 Ultra evidence for chosen trials](./05-collect-device-evidence.md).
