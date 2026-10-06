#!/usr/bin/env python3
"""Select the one authorized ADB device shared by the device-evidence tools."""
import subprocess


class DeviceSelectionError(Exception):
    """No unambiguous authorized phone is available."""


def online_serials(adb):
    result = subprocess.run([str(adb), 'devices'], check=True, capture_output=True, text=True)
    return [line.split()[0] for line in result.stdout.splitlines()
            if len(line.split()) >= 2 and line.split()[1] == 'device']


def select_serial(adb, requested=None):
    """Return the serial of the single authorized phone, or the requested one."""
    online = online_serials(adb)
    if requested:
        if requested not in online:
            raise DeviceSelectionError('The requested phone is not connected and authorized.')
        return requested
    if len(online) == 1:
        return online[0]
    if not online:
        raise DeviceSelectionError('No authorized phone is visible to this ADB server.')
    raise DeviceSelectionError('Several phones are connected. Select one with --device.')
