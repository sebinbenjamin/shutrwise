#!/usr/bin/env python3
"""Run agent-device verification under the same phone lease as RAW capture."""
import argparse
from pathlib import Path
import subprocess
from adb_select import select_serial
from device_lifecycle import DeviceRun


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adb', default='/usr/bin/adb')
    p.add_argument('--device')
    p.add_argument('--launcher', required=True, help='Exact launcher returned by T3 device_open')
    p.add_argument('--config', required=True)
    p.add_argument('--session', required=True)
    p.add_argument('--package', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('command', nargs=argparse.REMAINDER, help='Optional agent-device command after --')
    a = p.parse_args()
    if a.output.exists():p.error('Output exists; choose a new evidence directory.')
    serial = select_serial(a.adb, a.device)
    target = ['--platform','android','--serial',serial,'--config',a.config,'--session',a.session]
    with DeviceRun(a.adb, serial, record=a.output/'cleanup.json') as owner:
        a.output.mkdir(parents=True, exist_ok=False)
        owner.started(a.package)
        owner.session_command = [a.launcher,'close',*target]
        subprocess.run([a.launcher,'open',a.package,'--foreground',*target],check=True)
        subprocess.run([a.launcher,'help','workflow',*target],check=True)
        command = a.command[1:] if a.command[:1] == ['--'] else a.command
        if command:subprocess.run([a.launcher,*command,*target],check=True)


if __name__ == '__main__': main()
