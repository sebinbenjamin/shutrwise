# Development phone setup

Last connection and capture verification: 2026-10-06. The spare Galaxy S22 Ultra is connected and authorized through USB ADB. Its [device evidence record](../.scratch/shutrwise/assets/s22-ultra/device-record.md) links the original software inventory and [Camera2 measurement report](research/s22-camera2-probe-20261006.md).

## Environment and device roles

The physical homelab server runs Proxmox. A Debian VM runs the T3 server and this workspace at `/home/t3agent/workspace/shutrwise`. The phone connects to the physical Proxmox server, and USB passthrough exposes it to Debian. No remote SSH device host is configured or needed for this connection.

The owner authorized leaving the spare S22 connected for camera development and experiments. The S25 Ultra remains the target phone. Keep each device's evidence separate; repeat hardware-dependent checks on the S25 before making claims about its lenses, RAW output, exposure limits, throughput or image quality.

The Proxmox version, VM ID and physical host port were not recorded. Guest USB port `2-1` was observed; it must not be assumed to be the Proxmox host port.

## Configure USB passthrough

These steps document the working connection route and how to recreate it:

1. Enable Developer options and USB debugging on the S22.
2. Connect it with a USB data cable to the physical Proxmox server.
3. In Proxmox's web interface, select the Debian VM running T3.
4. Open Hardware → Add → USB Device.
5. Choose Use USB Port, then select the port showing the Samsung phone. Keep using that physical port for this persistent setup.
6. Retain the default Use USB3 setting where shown and click Add.
7. Unlock the phone and approve Debian's USB-debugging RSA prompt when it appears. Remember the host if a persistent connection is wanted.

The USB choices are defined in [Proxmox's USB dialog](https://github.com/proxmox/pve-manager/blob/master/www/manager6/qemu/USBEdit.js). Proxmox [introduced USB hotplug in VE 7.3](https://www.proxmox.com/en/about/company-details/press-releases/proxmox-virtual-environment-7-3), so try adding it while the VM runs. If the configuration stays pending and the guest cannot see the phone, gracefully shut down the Debian VM and then start it through Proxmox. That temporarily interrupts T3. The agent has not changed Proxmox configuration or shut down the VM.

USB debugging and the RSA authorization prompt are documented in the [Android ADB guide](https://developer.android.com/tools/adb#Enabling).

## Installed tools

These paths describe this workspace's installation, not prerequisites that every checkout must use.

| Tool | Verified version | Local location or configuration |
| --- | --- | --- |
| ADB | 1.0.41, platform-tools 37.0.1-15733141 | `/home/t3agent/.local/share/shutrwise/android/platform-tools/adb` |
| Android SDK | Platform 36 revision 2, build-tools 36.0.0, command-line tools 23.0 | `/home/t3agent/.local/share/shutrwise/android/sdk`, also symlinked at `/home/t3agent/Android/Sdk` |
| Java | OpenJDK 21.0.12.1 | `/home/t3agent/.local/share/shutrwise/android/debian-jdk/root/usr/lib/jvm/java-21-openjdk-amd64` |
| RAW inspection | rawpy 0.27.1, LibRaw 0.22.1, NumPy 2.5.3, Pillow 12.3.0, tifffile 2026.9.20, SciPy 1.18.1 | Virtual environment `/home/t3agent/.local/share/shutrwise/raw-inspection` |
| agent-browser | 0.37.1 | `/home/t3agent/.local/bin/agent-browser` |
| T3 Device hub | 0.12.0 | `/home/t3agent/.t3/tools/expo-device-hub/0.12.0/` |
| T3 Agent device | 0.21.12 | `/home/t3agent/.t3/tools/agent-device/0.21.12/` |
| Android Emulator | 37.2.12, build 16428233 | SDK `emulator/`; installed for T3's host check, no virtual device created |

ADB was installed from Google's Linux platform-tools distribution. Device hub and Agent device were installed through T3's Settings → Integrations controls. Device hub and Agent device access were enabled specifically for the `debian-docker` environment and verified after reloading the page.

The SDK was installed from Google's official command-line-tools distribution and repository packages. The download URL and checked checksum are recorded in `/home/t3agent/.local/share/shutrwise/android/toolchain-downloads.json`. Java was extracted from official Debian packages into the user directory, without a system package installation. `java-home.txt` in that Android tool directory records its location. A local Java trust store uses the host's public certificate roots. These paths can be replaced by an ordinary Java 21 and Android SDK installation on another host.

On 2026-10-06, T3 discovery and screen capture were fixed. `device_list` reports the physical S22 Ultra as available, `device_open` opens it in this thread's panel, and `device_screenshot` returns the probe app's screen. The previously reported SDK/Emulator failures are historical; USB passthrough and ADB were already working.

T3 requires the Emulator package even for this physical phone. The running service also needed discoverable Java and SDK paths. `/home/t3agent/.local/bin/java` and `emulator` point to the installed executables; `/home/t3agent/Library/Android/sdk` points to the same SDK as `/home/t3agent/Android/Sdk`. These links avoid a service restart and also satisfy Device hub's default SDK lookup.

Device hub 0.12.0 additionally defaults to an emulator-only capture source. The running phone session now uses `scrcpy`. A reversible local compatibility patch selects `scrcpy` automatically for physical phones on future hub starts, leaving emulator defaults intact. See the [fix report](research/t3-device-panel-fix-20261006.md) for evidence, the regression check, and reapply/restore instructions. A hub package update may replace this patch. No virtual device was created, and T3 and the VM were not restarted. Browser rendering on the owner's client remains separate from the verified discovery, panel registration and screen capture.

[Agent device](https://github.com/callstack/agent-device) supports physical Android interaction through ADB. Use the native T3 device tools where available and retain the exact launcher and session configuration returned by `device_open`. Use agent-browser for web pages with an isolated named session; it does not replace native Android camera access.

For the `t3agent` user, `/home/t3agent/.local/bin/agent-device` links to T3's managed launcher at `/home/t3agent/.t3/userdata/device/bin/agent-device`. The user-local bin directory is already on PATH; `agent-device --version` reports `0.21.12`. This adds no separate global installation. For T3 device work, continue using the exact launcher and target/session flags returned by `device_open`.

## Verify and record the connection

From Debian, check:

```bash
/home/t3agent/.local/share/shutrwise/android/platform-tools/adb devices -l
```

An entry marked `device` means the phone is connected and authorized. An entry marked `unauthorized` requires approving the prompt on the unlocked phone. An empty list requires checking the cable, physical connection and Proxmox passthrough before investigating camera software.

The repository's [inventory helper](../tools/collect-device-inventory.py) finds the local ADB installation automatically:

```bash
python3 tools/collect-device-inventory.py --label s22-ultra
```

To preserve a report, supply `--output` with a new filename under `.scratch/shutrwise/assets/s22-ultra/`. The helper refuses to overwrite an existing file. Use `--adb /path/to/adb` on another machine and `--device` if several authorized phones are visible.

The helper reads software properties and versions for Samsung Camera, Expert RAW and Open Camera. It omits the unique ADB serial. It retains the raw One UI property without guessing a display version. A missing package version is inconclusive about installation for other Android users. The report is a software inventory, not a Camera2 capability map.

## Run the camera probe

The throwaway source is committed on `prototype/s22-camera-probe`, commit `eeaf02f24cba56590990e3bcd2ec0666a0984441`. It remains separate from product code. Open that branch in an isolated checkout, or use the existing `/tmp/shutrwise-camera-probe` checkout while present:

```bash
git worktree add /path/to/new/probe-checkout prototype/s22-camera-probe
```

From that checkout:

```bash
python3 probe/build.py
python3 probe/run.py --action capabilities --output /path/to/new/capability-record
python3 probe/run.py --skip-install --action capture --camera-id 0 --mode bracket --output /path/to/new/bracket-record
/home/t3agent/.local/share/shutrwise/raw-inspection/bin/python probe/inspect_dng.py /path/to/evidence-root --output /path/to/inspection.json --contact-sheet-run bracket-record
```

Keep the phone unlocked and use a fresh output directory per run. The runner installs the debug APK unless `--skip-install` is given, grants its declared CAMERA permission and accesses only `dev.shutrwise.probe` storage. It does not access personal media. The source README documents tool overrides, single captures and inspection dependencies. Reinstall after rebuilding changed Android source; `--skip-install` assumes the installed APK matches the local build.

The measured S22 exposes four listed RAW/manual paths, all of which yielded an independently decoded DNG. Three main-camera bracket repeats after owner-standardized conditions saved nine valid RAWs. The [report](research/s22-camera2-probe-20261006.md) links capability JSON, original sources, inspection, conditions and artifact hashes. Earlier captures had varying light and are preserved as technical smoke tests. The debug app and source captures remain on the phone; each capture closes its camera session after saving.

## Reproduce the RAW comparison

The [RAW-versus-bracket report](research/raw-bracket-comparison-20261006.md) documents a subsequent deterministic merge and independent audit using the existing standardized sources. Processing source is on `prototype/raw-bracket-comparison`, commit `7410de66dd4aa33bdb0c23fb9b25730de0143216`; independent audit source is on `research/raw-comparison-audit`, commit `3a6766db4ff5355a16a6fb96f1c7307a43a69961`. Open either branch in its own worktree. Their READMEs give processing commands, pinned dependencies and verification methods. Analysis needs no live phone connection.

Canonical derived results are in `.scratch/shutrwise/assets/s22-ultra/raw-bracket-comparison-20261006/merge/` and `merge-aligned/`; `audit/` contains the independent checks. Original capture files are unchanged. Source manifests, scientific float masters, matching preview transforms and output hashes are retained. Desktop processing time is not on-phone performance or capture latency.

## Run the longer-single control

A subsequent [longer/lower-ISO control](research/long-single-control-20261006.md) captured three new four-frame sessions. It keeps focus and white balance constant within each session and records a fixed-ISO bracket plus a longer/lower-ISO single. Source is on `prototype/long-single-control`, commit `70fef8daabf4f3bac4dbe0c4c7b5a9b6e5f4af07`; audit source is on `research/long-single-control-audit`, commit `a5b3c77e485dd425a8f4ad3fedfbe9075a815a2f`.

The updated debug probe is installed on the phone. To reproduce, use this newer branch, build with `python3 probe/build.py`, and run `probe/run.py --action capture --camera-id 0 --mode control --output /path/to/new/captures/control-01`. Repeat into new `control-02` and `control-03` directories. Its `comparison/README.md` gives the processing command. Analysis source/output directories remain isolated from the earlier evidence. Camera sessions close after captures, and original files remain preserved.

Advertised capability, one successful capture and sustained reliability are different evidence. Do not infer untouched 200 MP data or Samsung pipeline parity from a DNG file. Preserve source captures and metadata, then compare with the [agreed baseline method](../.scratch/shutrwise/assets/initial-capture-comparison.md).

The [current evidence task](../.scratch/shutrwise/issues/05-collect-device-evidence.md) remains unresolved. A connected development phone and its software versions do not settle the product direction or target S25 capabilities.

## Batch all directly exposed RAW cameras

The reusable [batch script](../tools/raw-camera-experiment/batch.py) automates fresh capability mapping, three control sequences per listed RAW/manual camera, separate physical-ID direct-access attempts, source export, RAW processing and metadata/formula checks. The [batch README](../tools/raw-camera-experiment/README.md) gives normal/dark capture and analysis commands. Capture completes before desktop processing, allowing the owner to change lights while analysis runs.

The script uses the locally built probe, verifies its installed APK hash, and refuses existing evidence paths. The copied capture source is unchanged from the longer-single prototype commit. Each condition's capture/analysis status and file manifest distinguish successes from failures. This covers directly listed API paths; physical telephoto IDs that fail direct opening require separate logical-camera routing work and must not be counted as photographed.
