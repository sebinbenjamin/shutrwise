# Probe experiment state

This native measurement prototype follows one flow:

permission → capability dump, or opening camera → configuring RAW + preview → metering → submitting capture requests → pairing image/result timestamps → saving DNG and metadata → finished.

Any camera/session/capture failure or a 90-second deadline records FAILED and closes the session. The UI displays the capture-state JSON, including camera ID, sizes, baseline, requested plan and saved-frame count. Full metadata lives in the exported characteristic, baseline and per-frame JSON files.

The experiment settles whether advertised controls and file output work on this exact device/build. It does not settle product UI, RAW quality relative to Samsung, an optimal bracket algorithm or S25 behavior.
