#!/usr/bin/env python3
"""Apply or restore a guarded compatibility patch to Device hub 0.12.0.

Physical phones need scrcpy even when the hub defaults to emulator gRPC.
Existing running hubs require a stream-mode switch; this fixes future starts.
"""
import argparse
import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path


ORIGINAL_SHA256 = "41a5b434ae09a33325c8fe3b6e93cf3d49681c44d34eca7a20ab6fb47f3cd895"
PATCHED_SHA256 = "737b00565fc94fe9c1f2a5de8122b77378c21382b0f17fa4272216ff6c5da548"


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def replace_file(target, data):
    """Publish a complete file, preserving permissions and avoiding partial writes."""
    fd, temporary = tempfile.mkstemp(prefix=target.name + ".", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            os.fchmod(output.fileno(), stat.S_IMODE(target.stat().st_mode))
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", action="store_true")
    parser.add_argument("--package-dir", type=Path, default=Path.home() / ".t3/tools/expo-device-hub/0.12.0/node_modules/expo-device-hub")
    args = parser.parse_args()
    package = args.package_dir.resolve()
    metadata = json.loads((package / "package.json").read_text())
    if metadata["name"] != "expo-device-hub" or metadata["version"] != "0.12.0":
        raise SystemExit("Only expo-device-hub 0.12.0 is supported; recheck newer versions.")
    target = package / "vendor/serve-emu/dist/middleware.js"
    backup = target.with_name("middleware.js.shutrwise-original")
    original = 'defaults.streamMode ?? "scrcpy"'
    replacement = '(isEmulatorSerial(serial) ? defaults.streamMode ?? "scrcpy" : "scrcpy")'
    source = target.read_bytes()
    source_hash = sha256_bytes(source)
    if args.restore:
        if not backup.exists():
            raise SystemExit("No saved original to restore.")
        saved = backup.read_bytes()
        if sha256_bytes(saved) != ORIGINAL_SHA256:
            raise SystemExit("Original backup changed; refusing to restore it.")
        if source_hash not in (ORIGINAL_SHA256, PATCHED_SHA256):
            raise SystemExit("Installed file changed; refusing to overwrite it.")
        replace_file(target, saved)
        backup.unlink()
        print("Restored original middleware.")
        return
    if source_hash == PATCHED_SHA256:
        if not backup.exists() or sha256_bytes(backup.read_bytes()) != ORIGINAL_SHA256:
            raise SystemExit("Patched file has no verified original backup; inspect before continuing.")
        print("Compatibility patch already applied.")
        return
    if source_hash != ORIGINAL_SHA256:
        raise SystemExit("Unexpected router source; refusing to patch it.")
    patched = source.replace(original.encode(), replacement.encode())
    if sha256_bytes(patched) != PATCHED_SHA256:
        raise SystemExit("Unexpected patch result; refusing to write it.")
    if backup.exists():
        if sha256_bytes(backup.read_bytes()) != ORIGINAL_SHA256:
            raise SystemExit("Original backup changed; refusing to overwrite it.")
    else:
        with backup.open("xb") as output:
            output.write(source)
            output.flush()
            os.fsync(output.fileno())
    replace_file(target, patched)
    print(json.dumps({"packageVersion": metadata["version"], "originalSha256": source_hash, "patchedSha256": sha256_bytes(patched), "backup": str(backup)}, indent=2))


if __name__ == "__main__":
    main()
