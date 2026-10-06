# S25 Ultra device evidence checklist

This is the human-assisted checklist for Collect S25 Ultra evidence for chosen trials. Its purpose is to establish actual camera behavior and compare candidate sources of value. Scene coverage stays open. No device measurements have been completed.

## Start with the software inventory

1. On the phone, open Settings, About phone, Software information. Record Android and One UI versions and, when convenient, the build number. Record the model name or model number shown in About phone.
2. Record whether Samsung Expert RAW and Open Camera are installed. Include app versions when available. Missing apps are inventory facts; this checklist does not require installation before the inventory is recorded.
3. Record Samsung Camera's app version when convenient. Note relevant RAW save settings and any visible experimental or Labs settings in the apps actually installed.

Samsung documents the software-information path in its [software update guide](https://www.samsung.com/ca/support/mobile-devices/software-update-for-your-samsung-galaxy/). App controls can vary by installed release.

## Establish available capture paths

1. For each camera path you actually want to inspect, record the app, selected camera or lens, available output formats and resolutions, and whether manual ISO and shutter controls are offered. Rear and front paths must be recorded separately.
2. If Open Camera is already available, open its Settings and record Camera API. Then open Settings, About, and copy the camera diagnostic information to the clipboard. Inspect its RAW options; retain the diagnostic text rather than transcribing every value. Note which options are absent and which are visible but fail when exercised. The [official help](https://opencamera.org.uk/help.html) documents device-dependent Camera2, RAW and exposure-bracketing options.
3. Check installed Expert RAW for explicit exposure-bracket controls and separate-source saving. Record what is present without interpreting Multiple exposure as traditional AEB. Count the files from one operation and inspect their actual exposures before claiming separate DNG brackets.
4. A comprehensive Camera2 capability map is still a separate measurement. If existing app reports cannot answer a relevant question, prepare a minimal probe for that gap rather than treating app UI absence as proof that the hardware lacks a capability.

## Obtain the first comparison files

Choose any subject or location the owner wants to photograph. Use a consistent scene and framing for each comparison, noting changes in lighting, movement or composition.

1. Record the scene description, the photographer's priority, approximate time, handheld or tripod use, and camera path. Use a mix of handheld and tripod records as evidence accumulates; there is no exclusive scene list.
2. Save a Samsung Photo reference. For the same situation, collect source files from available RAW modes that are practical to compare. Start with the modes already installed; record unavailable paths instead of inventing results.
3. Where RAW exposure bracketing is actually available, preserve every separate source file and record the requested bracket settings. Verify the file count and actual exposure metadata rather than assuming the requested spacing was achieved.
4. Retain original files with each comparison record. Suggested repository asset location: `.scratch/shutrwise/evidence/run-001/`, then further numbered runs. Record which files are captures, composites, rendered outputs or external edits.

An initial comparison need not exhaust all modes, lenses or scene conditions. It must identify what was and was not tested. Expand it when new situations or capabilities become relevant.

## Inspection in the workspace

Once evidence is available here, inspect file counts, formats, dimensions, camera identity, exposure times, ISO and metadata completeness. Independently decode DNG files where possible. Record observed output support separately from advertised support and sustained reliability.

Assess useful highlights and shadows, detail, blur or ghosting, and editing effort under documented development settings. Assess guidance through the separate experience prototypes. Do not treat a clearer explanation as proof of better captured data, or a larger file as proof of better information.

## Resolution requirements

Resolve the task when the collected record is sufficient to support the product-direction discussion, with assets linked and remaining limitations explicit. Document missing modes and incomplete tests honestly. Software versions alone do not resolve RAW structure, lens access, burst reliability or comparative value.
