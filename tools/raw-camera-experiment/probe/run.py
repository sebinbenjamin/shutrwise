#!/usr/bin/env python3
"""THROWAWAY on-device evidence runner. Operates only dev.shutrwise.probe."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import time

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from adb_select import DeviceSelectionError, select_serial  # noqa: E402

PACKAGE = 'dev.shutrwise.probe'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', type=Path, default=Path.home() / '.local/share/shutrwise/android/platform-tools/adb')
    parser.add_argument('--device', help='Select an authorized ADB serial if several phones are connected')
    parser.add_argument('--action', choices=['capabilities', 'capture'], default='capabilities')
    parser.add_argument('--camera-id', default='0')
    parser.add_argument('--mode', choices=['single', 'bracket', 'control'], default='single')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--skip-install', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; choose a new evidence directory.')
    args.output.mkdir(parents=True)
    try:
        serial = select_serial(args.adb, args.device)
    except DeviceSelectionError as error:
        parser.error(str(error))
    adb = [str(args.adb), '-s', serial]
    apk_path = Path(__file__).parent / 'build/probe.apk'
    apk_hash = hashlib.sha256(apk_path.read_bytes()).hexdigest() if apk_path.exists() else None
    collection = {'source': PACKAGE, 'action': args.action, 'camera_id': args.camera_id if args.action == 'capture' else None, 'mode': args.mode if args.action == 'capture' else None, 'local_apk_sha256': apk_hash}

    def text(*cmd):
        return subprocess.run(adb + list(cmd), check=True, capture_output=True, text=True, timeout=30).stdout

    if not args.skip_install:
        apk = Path(__file__).parent / 'build/probe.apk'
        print(text('install', '-r', str(apk)).strip())
    text('shell', 'pm', 'grant', PACKAGE, 'android.permission.CAMERA')
    text('shell', 'am', 'force-stop', PACKAGE)
    prior_runs = []
    prior_capability_stamp = None
    try:
        prior_runs = text('shell', 'run-as', PACKAGE, 'ls', 'files/runs').splitlines()
    except subprocess.CalledProcessError:
        pass
    try:
        prior_capability_stamp = json.loads(text('shell', 'run-as', PACKAGE, 'cat', 'files/capabilities.json')).get('recorded_at_utc')
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        pass
    command = ['shell', 'am', 'start', '-W', '-n', PACKAGE + '/.MainActivity',
               '--es', 'action', args.action]
    if args.action == 'capture':
        command += ['--es', 'camera_id', args.camera_id, '--es', 'mode', args.mode]
    print(text(*command).strip())
    deadline = time.monotonic() + 110
    previous = None
    run_name = None
    while time.monotonic() < deadline:
        try:
            if args.action == 'capabilities':
                payload = text('shell', 'run-as', PACKAGE, 'cat', 'files/capabilities.json')
                report = json.loads(payload)
                if report.get('camera_ids') and report.get('recorded_at_utc') != prior_capability_stamp:
                    (args.output / 'capabilities.json').write_text(payload)
                    (args.output / 'collection.json').write_text(json.dumps(collection, indent=2)+'\n')
                    print('Capability report saved.')
                    return
            else:
                names = text('shell', 'run-as', PACKAGE, 'ls', 'files/runs').splitlines()
                matching = [n for n in names if n not in prior_runs and n.endswith('-camera' + args.camera_id + '-' + args.mode)]
                if matching:
                    run_name = sorted(matching)[-1]
                    payload = text('shell', 'run-as', PACKAGE, 'cat', 'files/runs/' + run_name + '/run.json')
                    report = json.loads(payload)
                    state = report.get('state')
                    if state != previous:
                        print('Probe state:', state, flush=True)
                        previous = state
                    if state in ['FINISHED', 'FAILED']:
                        archive = subprocess.run(adb + ['exec-out', 'run-as', PACKAGE, 'tar', '-C', 'files/runs/' + run_name, '-cf', '-', '.'], check=True, capture_output=True, timeout=120).stdout
                        with tarfile.open(fileobj=io.BytesIO(archive)) as t:
                            t.extractall(args.output, filter='data')
                        collection['device_run'] = run_name
                        (args.output / 'collection.json').write_text(json.dumps(collection, indent=2) + '\n')
                        print('Evidence collected:', args.output)
                        if state != 'FINISHED':
                            raise RuntimeError(report.get('error', 'Capture failed'))
                        return
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        time.sleep(1)
    raise RuntimeError('Probe did not finish; check the phone lock screen and probe logs.')


if __name__ == '__main__':
    main()
