#!/usr/bin/env python3
"""Record a connected phone's software inventory; camera capabilities need a probe."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", help="Path to the adb executable")
    parser.add_argument("--device", help="ADB serial when several devices are connected")
    parser.add_argument("--label", required=True, help="Evidence label, such as s22-ultra")
    parser.add_argument("--output", type=Path, help="Save JSON to this path; otherwise print it")
    args = parser.parse_args()

    local_adb = Path.home() / ".local/share/shutrwise/android/platform-tools/adb"
    adb = args.adb or shutil.which("adb")
    if not adb and local_adb.is_file():
        adb = str(local_adb)
    if not adb:
        parser.error("ADB is unavailable. Set --adb to the platform-tools executable.")

    def run(*command):
        result = subprocess.run(
            [adb, *command], capture_output=True, text=True, timeout=20, check=True
        )
        return result.stdout.strip()

    online = []
    for line in run("devices").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] == "device":
            online.append(fields[0])
    if args.device:
        if args.device not in online:
            parser.error("The requested device is not connected and authorized.")
        serial = args.device
    elif len(online) == 1:
        serial = online[0]
    elif not online:
        parser.error("No authorized phone is visible to this ADB server.")
    else:
        parser.error("Several phones are connected. Select one with --device.")

    def shell(*command):
        return run("-s", serial, "shell", *command)

    properties = {
        "manufacturer": "ro.product.manufacturer",
        "model": "ro.product.model",
        "device_codename": "ro.product.device",
        "android_version": "ro.build.version.release",
        "android_api_level": "ro.build.version.sdk",
        "one_ui_property": "ro.build.version.oneui",
        "build_number": "ro.build.display.id",
        "security_patch": "ro.build.version.security_patch",
    }
    inventory = {name: shell("getprop", key) or None for name, key in properties.items()}
    apps = {}
    for name, package in {
        "samsung_camera": "com.sec.android.app.camera",
        "expert_raw": "com.samsung.android.app.galaxyraw",
        "open_camera": "net.sourceforge.opencamera",
    }.items():
        dump = shell("dumpsys", "package", package)
        versions = re.findall(r"^\s*versionName=(.+)$", dump, re.MULTILINE)
        apps[name] = {
            "package": package,
            "version": versions[0].strip() if versions else None,
            "package_record_found": bool(versions),
        }

    report = {
        "label": args.label,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "adb software inventory",
        "device": inventory,
        "apps": apps,
        "camera_capabilities_measured": False,
        "notes": [
            "One UI's raw property is retained without guessing its display version.",
            "A missing package version is inconclusive about installation for other users.",
            "RAW formats, lenses, exposure controls and capture quality remain unmeasured.",
        ],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            parser.error("Output exists. Choose a new path to preserve the previous record.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
        print(f"Recorded software inventory in {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Device inventory failed: {error}", file=sys.stderr)
        sys.exit(1)
