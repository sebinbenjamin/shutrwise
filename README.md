# Shutrwise

An exploration of a camera assistant that helps beginner photographers choose how to capture a scene, preserves RAW source files for later editing, and explains its choices when wanted.

The current goal is to choose a product direction and its core experience using device evidence and practical comparisons. A throwaway native Camera2 probe is archived on `prototype/s22-camera-probe`; a product camera app and full implementation specification remain open.

## Starting preferences

- Help the beginner get the shot, with deeper learning available on demand.
- Use deliberate capture as the working default, with quick capture optional. Extra time or extra frames must provide a useful benefit.
- Give brief feedback before and during capture, with a deeper explanation afterward when wanted.
- Start with the camera choosing and showing a capture plan. Priorities, technical adjustments and explanations remain available when wanted. The owner selected this starting interaction; detailed controls and output workflow remain open.
- Compare capture improvements and clearer decision-making separately. Keep both immediate-photo and later-RAW-editing workflows open.
- Keep scene coverage open. New Zealand scenery is an initial interest, and people, selfies and other subjects remain relevant. Include handheld and tripod use.

These are exploration inputs. The model, camera framework, capture algorithm, final interface, licensing strategy and commercial direction remain undecided.

## Where to continue

| Document | Purpose |
| --- | --- |
| [Decision map](.scratch/shutrwise/map.md) | Destination, resolved decisions and remaining questions |
| [Current evidence task](.scratch/shutrwise/issues/05-collect-device-evidence.md) | Device investigation and its progress |
| [Development phone setup](docs/development-phone.md) | Proxmox USB passthrough, local tools and connection checks |
| [S22 Ultra evidence](.scratch/shutrwise/assets/s22-ultra/device-record.md) | Development-phone inventory and camera measurements |
| [Camera2 probe results](docs/research/s22-camera2-probe-20261006.md) | RAW paths, verified DNGs, repeated brackets and preserved evidence |
| [One RAW versus a bracket merge](docs/research/raw-bracket-comparison-20261006.md) | Matched renderings, independent audit, costs and limits |
| [Longer single versus a bracket](docs/research/long-single-control-20261006.md) | Fresh paired captures testing a stronger single-RAW baseline |
| [S25 Ultra evidence](.scratch/shutrwise/assets/device-evidence-record.md) | Owner-reported target-phone inventory and outstanding measurements |
| [All listed RAW cameras, normal and dark](docs/research/all-camera-lighting-20261006.md) | Per-camera control quartets under two lightings; layouts, shutter limits and black-level calibration |
| [Comparison method](.scratch/shutrwise/assets/initial-capture-comparison.md) | Baselines, conditions, sources of value and continuation criteria |
| [Device evidence checklist](.scratch/shutrwise/assets/device-evidence-checklist.md) | Required capability records and comparison captures |
| [Android capture research](docs/research/android-capture-controls.md) | Camera API facts and device-dependent unknowns |
| [Existing capture options](docs/research/existing-capture-options.md) | Samsung and Open Camera baselines, with primary sources |
| [Glossary](GLOSSARY.md) | Shared photographic and product terminology |

## Last verified device state

On 2026-10-06, the spare S22 Ultra was reachable through authorized USB ADB in the Debian VM running T3 on Proxmox. Its software inventory reports SM-S908E, Android 16 / API 36 and Samsung Camera 16.0.00.66. The native probe saved decodable DNGs through all four listed Camera2 paths. Three main-camera bracket repeats produced nine verified 4000 × 3000 RAW files with actual -2/0/+2 EV spacing after the owner standardized lighting and fixed the phone in place. Earlier varying-light captures are recorded separately as technical smoke tests.

The S25 Ultra remains the target device. Its reported versions are Android 16, One UI 8.5, Expert RAW 5.0.08.2 and Open Camera 1.56.2. These were reported by the owner, not read from that phone. S22 results must not be treated as S25 measurements.

T3 now discovers the physical S22 and has opened it in this thread's Device panel. Native screen capture returns the probe app's screen. The host tooling and a reversible Device hub 0.12.0 compatibility patch fix the earlier discovery/streaming failures; a fresh hub session also passes. See the [fix report](docs/research/t3-device-panel-fix-20261006.md) and [connection guide](docs/development-phone.md).

The delegated data experiments compared brackets with their metered middle RAW and then captured twelve fresh sources to test a longer, lower-ISO single. That stronger single looks less grainy than the metered baseline while keeping similar brightness and clipping. The merge appears quieter still and retains a short highlight source, at three times the RAW storage and 31.25% more summed integration than the longer single. Registration and scene limits remain; quantified SNR/dynamic range, photographer preference, Samsung comparisons and S25 behavior are unmeasured.

## Repository conventions

[AGENTS.md](AGENTS.md) defines agent instructions; [CLAUDE.md](CLAUDE.md) imports it. Decisions and tasks use local Markdown under `.scratch/shutrwise/`. Read the [issue-tracker conventions](docs/agents/issue-tracker.md) before changing tracker state. Original evidence belongs with its device or comparison record, with conditions and limitations stated.
