---
kind: decision
status: resolved
type: grilling
execution: human
parent: ../map.md
blocked_by:
  - ./01-define-beginner-promise.md
  - ./02-android-capture-controls.md
  - ./03-existing-capture-options.md
---

# Choose capture trials and evidence thresholds

## Question

How should comparisons provide evidence for a product direction while keeping scene coverage open, and what early results would justify further exploration?

Begin with the owner's scenic interests: New Zealand beaches, mountains, bright sky, shaded foreground, and optional people or selfies. Determine practical constraints and quality, learning, and workflow measures with the owner. Compare against appropriate existing camera modes and simple RAW or fixed-bracket baselines. Treat difficult motion as a possible boundary case rather than a permanent exclusion. Decide the evidence required before commissioning a probe or making UI and algorithm claims.

## Comments

### Practical preferences from the owner, 2026-10-06

- Use a mix of handheld and tripod situations. Neither is assumed to be the sole primary workflow.
- The owner proposes a slower, more deliberate default aimed at captured data and possibly feedback; quick capture is optional. They question the value of duplicating Samsung's quick-capture experience.
- No fixed duration or upper waiting limit has been chosen. Total workflow time, individual exposure duration, and useful added information are separate quantities.
- The suggested initial scenes remain proposals: bright sky with shaded foreground, a person against a bright background, and ordinary even lighting.
- The timing and meaning of default feedback are unresolved. The evidence criteria must test useful data and useful guidance rather than treating extra elapsed time or extra files as success.

### Owner's agreement on capture feedback, 2026-10-06

Use brief feedback before and during capture, with a deeper explanation available afterward when wanted. Examples in the discussion were hypothetical, not measured S25 Ultra behavior. This settles feedback timing as an input to the trials; the specific interface remains open for experience prototypes.

Draft comparison proposal: [Initial capture comparison](../assets/initial-capture-comparison.md). Its scenes and continuation criteria are proposed for owner discussion, not approved trial instructions or a record of completed tests.

### Owner's correction and tentative criterion, 2026-10-06

The owner asks not to limit scene situations and asks what the comparison step is for. The comparison exists to investigate value in captured data and clearer decisions; it is not a supported-scene list. The owner tentatively agrees that a meaningful benefit in either area can justify further exploration.

## Answer

Use an open-ended comparison method rather than a fixed scene roster. The owner may photograph any subject or location; scenic interests do not exclude other situations. Record light, contrast, motion, stability, selected camera, and photographic intent so differences can be assessed. Use both handheld and tripod conditions. Compare existing capture paths on the same scene where practical, preserving source files and noting conditions that changed.

Evaluate captured-data value and clearer decision-making separately, alongside capture reliability, waiting time, and editing effort. The working continuation criterion is a meaningful, repeatable benefit in either area, with costs and regressions reported. This remains provisional until actual examples help the owner judge what is worthwhile. No numerical threshold or claim of superiority is locked. Extra files or elapsed time alone are not a benefit.

The agreed feedback flow is brief guidance before and during capture, with a deeper explanation available afterward when wanted. The final interaction remains open.

[Initial capture comparison](../assets/initial-capture-comparison.md) holds the supporting method. Collect S25 Ultra evidence for chosen trials will obtain actual device facts and comparisons; Explore capture and explanation interactions will compare experience alternatives. Neither a fixed scene scope nor a specific camera algorithm is selected.
