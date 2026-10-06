# Physical Android phone in T3's Device panel

On 2026-10-06, the connected S22 Ultra was discovered and opened in this thread's T3 Device panel. The native `device_screenshot` tool returned a 1080 × 2316 PNG showing the Shutrwise probe app. A fresh, temporary Device hub also selected the correct capture source and returned a PNG without a manual stream-mode override.

This applies to T3 `0.0.46-nightly.20261003.2610`, Device hub `0.12.0`, Agent device `0.21.12`, and the Debian host. The [redacted tool evidence](../../.scratch/shutrwise/assets/s22-ultra/t3-device-panel-verification-20261006.json) and [fresh-hub check](../../.scratch/shutrwise/assets/s22-ultra/t3-device-panel-fresh-check-20261006.json) record the results.

## Causes and fixes

The phone was already connected and authorized through ADB. No additional Proxmox passthrough or phone registration was needed.

1. T3's `LocalDeviceHost.platformReason` requires the SDK's Emulator executable before marking Android available, including for physical phones. Installed Google's Android Emulator package `37.2.12`, build `16428233`. No system image or virtual device was created. Installation used the existing SDK command-line tooling as described in [Android's SDK package documentation](https://developer.android.com/tools/sdkmanager).
2. The running T3 host had captured its environment before the SDK was discoverable. Its command runner could not find `emulator`, returning exit code 127. Added `/home/t3agent/.local/bin/emulator` pointing to the installed executable. This directory was already in the service's PATH.
3. Java 21 existed in the project tool directory, but was outside the service's PATH. Added `/home/t3agent/.local/bin/java` pointing to that Java executable, so `avdmanager` runs without a shell-specific `JAVA_HOME`.
4. Device hub's SDK resolver defaults to `~/Library/Android/sdk` when neither `ANDROID_HOME` nor `ANDROID_SDK_ROOT` is set. The running hub had neither variable. Added that directory as a symlink to the same SDK already linked at `~/Android/Sdk`.
5. Device hub defaults to `grpc-screenshot`, which requires an emulator serial. The physical phone's screenshot endpoint returned HTTP 503 with that specific error. Changed the running phone's stream source to `scrcpy` through the hub's supported per-device `PUT /vendor/serve-emu/api/stream-mode?device=...` endpoint, with JSON body `{"mode":"scrcpy"}`.

The fifth problem would recur on a new hub session. A local compatibility patch now makes the router choose `scrcpy` for physical phones. Emulators retain their configured default. The patch changes two default-selection expressions in the installed `vendor/serve-emu/dist/middleware.js`; it does not change T3's executable or Shutrwise's camera code.

## Reapply, verify or restore the compatibility patch

Run from this repository:

```bash
python3 tools/fix-t3-physical-stream.py
node tools/check-t3-physical-stream.mjs \
  /home/t3agent/.t3/tools/expo-device-hub/0.12.0/node_modules/expo-device-hub/vendor/serve-emu/dist/middleware.js
```

The patch helper checks the package identity/version and exact SHA-256 hashes of the original, patched file and restore backup. It preserves the original alongside the installed file as `middleware.js.shutrwise-original` and refuses to overwrite unexpected source. It writes a complete temporary file, preserves permissions and atomically replaces the target. Repeated application is a no-op.

To restore the original package file:

```bash
python3 tools/fix-t3-physical-stream.py --restore
```

The regression check calls the installed router's actual default-selection path, stopping at the capture boundary without accessing a phone. Before the fix, it failed because the physical-device case chose `grpc-screenshot`. After the fix, physical-device and emulator cases pass. It checks the physical-device input source too.

An existing hub keeps its loaded module until it restarts. Its per-device stream-mode switch fixes the current session; the file patch fixes future starts. A package reinstall or update may replace the patch. Recheck the new version rather than blindly patching unfamiliar source.

## Verification and limits

- `device_list` now reports Android available and lists `samsung SM-S908E`, Android 16.0, with `physical: true`.
- `device_open` succeeds and `device_list` confirms an open session in this thread.
- Native `device_screenshot` succeeds before and after the fresh-hub check.
- The temporary fresh hub starts with the original CLI defaults, chooses `scrcpy` automatically for the real phone, and returns a valid PNG. That hub is stopped after verification.
- The patch regression check passes and repeated application preserves the patched file.

The existing T3 service and Debian VM were not restarted. The phone's camera probe was not changed or triggered to take more photographs. The Linux host still reports iOS unavailable and an `xcrun` lookup error, which does not prevent Android discovery. These checks confirm discovery, panel registration and screen capture; browser rendering on the owner's client is not separately measured.

## Operational review

A subsequent review confirmed that discovery and native screen capture still pass. The physical/emulator router regression checks also pass. Temporary package fixtures verified patch application, repeated application, restoration, permission preservation, and refusal to modify unfamiliar source, a corrupt backup or another package version. Those fixtures were removed after the check. The installed patch bytes were unchanged during the review.

This is an interim compatibility workaround. Editing an app-managed dependency is a maintenance cost, even with a pinned hash, original backup and regression check. A hub update/reinstall can remove it, and the patch helper deliberately refuses unfamiliar versions.

The installed hub supports `--stream-source scrcpy`, and its per-device stream-mode API works. Inspection of this T3 version's `LocalDeviceHost.spawnHub` shows that it starts the hub with port, host and panel-display flags, without that source option. A T3-supported capture-source setting or an upstream physical-device default would be preferable to maintaining a local package patch. No such option was found in the inspected launcher. No upstream issue or PR was published during this review.

The SDK and Java symlinks make the already-running service work, but an explicit service environment is easier to maintain. Android documents `ANDROID_HOME` as the SDK location and PATH entries for executable discovery; `ANDROID_SDK_ROOT` is deprecated. See [Android's environment-variable documentation](https://developer.android.com/tools/variables). At a planned service maintenance window, configure `ANDROID_HOME`, `JAVA_HOME` and PATH in the actual T3 service launcher, restart deliberately, and verify discovery/screen capture before removing fallback links. This review did not change the service launcher or restart it.

The hub stays bound to loopback and no T3 authentication settings were changed. Browser video rendering and control on the owner's client remain unverified; a successful native screenshot alone does not establish those behaviors.

## Follow-up check for a missed capture-source setting

Checked the installed T3 executable and Device panel bundle, plus the published [T3 local-host launcher](https://github.com/pingdotgg/t3code/blob/main/apps/server/src/device/LocalDeviceHost.ts), [Device panel tools](https://github.com/pingdotgg/t3code/blob/main/apps/web/src/components/device/DeviceToolsPanel.tsx), and [browser stream client](https://github.com/pingdotgg/t3code/blob/main/packages/client-runtime/src/device/stream.ts). No capture-source preference, launcher flag forwarding or browser source selector was found in those inspected paths. Upstream `main` is additional context, not proof of the installed version's behavior.

The installed hub supports `--stream-source scrcpy`; this is distinct from video transport or codec selection. Its [CLI option parser](https://github.com/expo/expo-device-hub/blob/main/packages/expo-device-hub/src/server/cli/options.ts) exposes that flag. T3's launcher supplies no `--stream-source` flag. Browser H.264/MJPEG fallback selects how frames are delivered/decoded, not whether Android frames come from scrcpy or emulator gRPC.

Also checked `EXPO_DEVICE_HUB_SERVE_EMU_OPTIONS`, which the hub server reads. The standalone CLI unconditionally rebuilds this variable from its parsed options before importing the server. A temporary copy of the installed CLI stopped immediately before that import and printed only the resulting options. With an inherited `{"streamMode":"scrcpy"}` and no CLI flag, it selected `grpc-screenshot`; with `--stream-source scrcpy`, it selected `scrcpy`. The temporary probe was deleted and did not start a hub or modify running T3.

The supported per-device stream-mode API remains usable and was already used for the current phone session. Its selection belongs to that running router and does not supply a default for a newly started hub. Therefore no overlooked persistent T3 setting was established. A native T3 source option or upstream physical-device auto-selection remains the clean replacement for the local compatibility patch.

## Known upstream issue and fix

Checked public trackers on 2026-10-06. This exact default-selection defect is reported in [T3 issue #14824](https://github.com/pingdotgg/t3code/issues/14824), which is still open, and [Device hub issue #209](https://github.com/expo/expo-device-hub/issues/209), which is closed. [Device hub PR #239](https://github.com/expo/expo-device-hub/pull/239) merged on 2026-10-05 at 14:00:43 UTC, commit `ffa6c99cef6a60c57744d87a746a17e489e86a11`. It automatically selects scrcpy for physical serials while retaining emulator defaults, matching our local workaround's intent.

That PR also fixes a separate unchanged-size video-session notification loop that can prevent browser video after source selection succeeds. We have not established that this second defect occurs on this host; native screenshot success alone cannot exclude it.

The currently installed Device hub 0.12.0 required our local patch. A merged upstream PR does not prove that T3's pinned packaged dependency includes it. Before retiring the workaround, verify a shipped hub version containing the fix, T3's use of that version, and actual discovery/screen/video behavior. No dependency update or upstream posting was performed as part of this tracker lookup.
