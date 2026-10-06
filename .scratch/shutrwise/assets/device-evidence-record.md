# S25 Ultra device evidence record

The owner has reported the S25 Ultra software inventory below. No S25 Ultra connection, capability dump or image evidence has been received. User-reported versions are not independently read from that phone. The spare S22 Ultra is now connected; its measured software inventory is kept separately.

## Software inventory

| Item | Observed value |
| --- | --- |
| Phone model or model number | Galaxy S25 Ultra, owner-reported; model number pending |
| Android version | 16, owner-reported |
| One UI version | 8.5, owner-reported |
| Build number | Pending owner report |
| Samsung Camera version | Pending owner report |
| Expert RAW installed and version | Installed, 5.0.08.2, owner-reported |
| Open Camera installed and version | Installed, 1.56.2, owner-reported |

## Workspace access

At the start of this task, the workspace had no ADB executable or saved image or RAW captures. ADB is now installed from Google's Linux platform-tools distribution at `/home/t3agent/.local/share/shutrwise/android/platform-tools/adb`, version 1.0.41, platform-tools 37.0.1-15733141. The current device list shows one authorized Samsung SM-S908E. No camera capability was measured. Documentation research is linked from the resolved research decisions and must not be substituted for device observations.

The owner uses T3 Code in a Debian VM on Proxmox. USB passthrough now works: Debian sees Samsung's USB device 04e8:6860 on guest port 2-1, and ADB reports `device`, establishing an authorized connection. No remote SSH host is needed.

Prepared host USB port passthrough instructions before the owner connected the phone. The agent has not changed Proxmox configuration.

Using an isolated agent-browser 0.37.1 session and T3's normal short-lived pairing flow, inspected Settings → Integrations. Enabled Device hub and Agent device access specifically for the `debian-docker` environment and verified both settings persisted after reload. No remote device host is configured. The current MCP device-list call now works, but reports Android unavailable because an Android SDK directory is not configured. It reports iOS simulators unavailable because this is Linux. It lists no devices in T3's panel. Direct ADB access to the physical phone works independently.

T3's UI describes simulator/emulator hosts. Physical-phone support through that panel remains unverified. See the [development connection notes](development-phone-connection.md). The [software inventory helper](../../../tools/collect-device-inventory.py) is prepared, but requires an authorized ADB connection and does not measure Camera2 capabilities.

Installed T3's required Device hub 0.12.0 and Agent device 0.21.12 through their normal settings controls. The UI reports both installed, and Agent device's CLI version check returns 0.21.12. Its [official documentation](https://github.com/callstack/agent-device) confirms physical Android support through ADB. That CLI support does not prove T3's panel will display a physical device.

## Capture paths and files

Pending. Record app, camera or lens, format, dimensions, source file count, actual exposure metadata, failures, and linked evidence separately for each tested path.

## Comparisons and limitations

Pending. Scene coverage remains open; every comparison must state its actual conditions and the limits of what it establishes.

## Spare development device offered

The owner offers a spare Galaxy S22 Ultra that can remain connected for development and camera experiments. This authorizes scoped camera-development work. The connection and software inventory are now verified; see the [S22 Ultra evidence record](s22-ultra/device-record.md). Camera capabilities and capture quality remain unmeasured.

Keep observations from each phone in separate device records. The S22 Ultra can establish software behavior and identify its own hardware limitations; its results do not establish the S25 Ultra's lenses, RAW structure or resolution, exposure limits, throughput, image quality, or vendor processing. Repeat relevant capability and capture checks on the target S25 Ultra before treating them as target-device findings.
