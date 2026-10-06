---
kind: decision
status: claimed
claimed_by: /root
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
