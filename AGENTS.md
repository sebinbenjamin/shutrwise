## Agent skills

### Issue tracker

Track issues as local Markdown in `.scratch/<effort>/`. Before creating, querying, claiming, or resolving issues, read `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage labels. Before triaging an issue, read `docs/agents/triage-labels.md`.

### Domain docs

Use one root glossary and `docs/adr/`. Before exploring domain concepts or architectural decisions, read `docs/agents/domain.md`.

### Browser and device tools

- `agent-browser` for any browser task: pages, web apps, opening local HTML. Begin with `agent-browser skills get core --full`; its built-in skills are version-matched, so prefer them over guessed flags.
- `agent-device` for anything on a device: inspecting, driving or verifying apps on the connected phone, and TV or desktop apps. Begin with `agent-device open <app> --foreground` and `agent-device help workflow`; resolve unknown app ids through `devices`, then `apps`, then `open`. Web automation inside a device session runs `agent-browser`.
- Leave the phone dark when a device run ends: force-stop apps the run launched, end `agent-device` sessions with `agent-device close`, then sleep the screen with the workspace adb (`shell input keyevent 223`; agent-device has no screen-off command). Capture runs need the phone unlocked again before starting.
- A running RAW capture (`tools/raw-camera-experiment`) owns the phone's camera: start device sessions only after the batch reports complete.
