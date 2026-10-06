# Capture-flow discussion sketches

Question: how should a beginner influence the capture choices without needing to understand every camera setting first?

These are rough discussion outlines for [Explore capture and explanation interactions](../issues/06-explore-core-experience.md). All scene analysis, recommendations and assembled-photo outputs below are simulated. The S22 probe has measured RAW saving and fixed bracketing; it has not measured autonomous planning, subject recognition or a better finished photograph. The owner selected "Camera chooses" as the starting interaction on 2026-10-06. Output workflow and detailed controls remain open.

## Three alternatives

| Alternative | Before pressing the shutter | During capture | Optional explanation |
| --- | --- | --- | --- |
| Camera chooses | A brief capture plan appears. The photographer can shoot immediately or adjust a priority. | Progress and any useful instruction, such as keeping the phone still. | Why these choices suited the scene, with the actual settings available. |
| Photographer sets a priority | Choose a plain-language priority, such as preserving the sky or keeping faces sharp. The camera proposes settings. | The same progress and guidance. | How the priority affected the capture plan and what trade-off remains. |
| Photographer reviews the plan | See the proposed shutter, ISO and frame count before shooting, with plain-language reasons and overrides. | The same progress and guidance. | Compare the intended plan with actual capture results. |

The owner agreed with the first alternative. The camera chooses and shows the capture plan; priority selection remains available, and technical settings can be disclosed on demand. The alternatives below remain context for the discussion. This is a preferred starting interaction, not a completed product decision.

## Scenic walkthrough

Hypothetical situation: a beach at sunset with a bright sky and dark foreground. The phone is supported and the scene appears still. Those observations must be established by the eventual app rather than assumed from the subject label.

- Camera chooses: "Capture plan: several RAW exposures to cover the sky and foreground." The photographer presses the shutter. If the measured scene only needs one exposure, the plan instead says one RAW.
- Photographer sets a priority: choose "Preserve the sky" or "More room to edit the foreground", then see the resulting plan before pressing the shutter.
- Photographer reviews the plan: see the proposed exposure sequence and why it may help, then accept it or change a constraint.

During a sequence, show real progress and ask the photographer to keep the framing steady where useful. Optional explanation should distinguish what was requested from what actually happened. A useful explanation might describe the highlight-safe exposure and the longer exposures, with clipping or movement limits supported by evidence. It must not promise that a merge will recover already clipped samples.

## Group/selfie walkthrough

Hypothetical situation: faces in shade with a bright background. People may move even when the phone is supported.

- Camera chooses: "Capture plan: one RAW exposure, prioritizing sharp faces." This is an example, not a fixed rule for every group photograph.
- Photographer sets a priority: choose "Keep faces sharp" or "Preserve the background", with any conflict explained briefly.
- Photographer reviews the plan: see the proposed shutter limit, ISO and whether extra exposures are considered useful. The shutter remains easy to reach.

If conditions change before capture, revise the visible plan. The eventual behavior when movement begins during a sequence is still an open interaction question. These sketches do not assume that semantic recognition or motion handling already works.

## Output workflows remain open

Compare both after-capture experiences with the same preceding flow:

| Workflow | What appears after capture | What is preserved |
| --- | --- | --- |
| Usable photo immediately | A photograph to review or share, with optional explanation and editing access | Original RAW source captures and capture metadata |
| Later RAW editing | A review preview, source captures and a clear route to editing | Original RAW source captures and capture metadata |

The immediate-photo path needs its own evidence about rendering or merging quality and latency. A preview alone does not establish it. The later-editing path must be judged for the effort it asks of a beginner. Neither workflow is selected here.

## Owner reaction and remaining questions

The owner selected the camera choosing with an optional priority. That starting interaction does not require choosing a priority before every shot or reviewing technical settings before shooting.

Next, explore which overrides need to be visible and how much capture delay is acceptable before choosing between the output workflows. The owner authorized the separate RAW-versus-bracket data experiment with subagents. Target S25 measurements remain open.
