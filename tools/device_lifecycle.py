"""Cooperative per-phone leases; cleanup belongs to the outer acquisition."""
import fcntl
import hashlib
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
from file_integrity import write_json


class DeviceBusy(RuntimeError):
    pass


class DeviceRun:
    def __init__(self, adb, serial, *, keep_awake=False, inherited_fd=None,
                 record=None, state_dir=None, runner=subprocess.run,
                 owned_session_command=None):
        self.adb = str(adb)
        self.serial = serial
        self.keep_awake = keep_awake
        self.inherited_fd = inherited_fd
        self.record = record
        self.runner = runner
        self.session_command = owned_session_command
        self.apps = []
        self.fd = None
        self.handlers = {}
        state = Path(state_dir or os.environ.get('XDG_STATE_HOME', Path.home()/'.local/state'))
        self.path = state/'shutrwise/devices'/ (hashlib.sha256(serial.encode()).hexdigest() + '.lock')

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.inherited_fd is not None:
            if os.fstat(self.inherited_fd).st_ino != self.path.stat().st_ino or os.fstat(self.inherited_fd).st_dev != self.path.stat().st_dev:
                raise DeviceBusy('Inherited lease does not match this device')
            self.fd = self.inherited_fd
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                os.close(self.fd)
                self.fd = None
                raise DeviceBusy('The phone is owned by another capture or verification run') from None
        # Only the outer process controls signals and cleanup. Child exports remain uninterrupted.
        if self.inherited_fd is None:
            for name in (signal.SIGINT, signal.SIGTERM):
                self.handlers[name] = signal.signal(name, self._interrupted)
        return self

    @staticmethod
    def _interrupted(number, frame):
        raise KeyboardInterrupt('Device run interrupted')

    def started(self, package):
        if not re.fullmatch(r'[A-Za-z0-9_.]+', package):
            raise ValueError('Invalid Android package ID')
        if package not in self.apps:
            self.apps.append(package)

    def cleanup(self):
        results = []
        commands = [[self.adb, '-s', self.serial, 'shell', 'am', 'force-stop', app]
                    for app in self.apps]
        if self.session_command:
            commands.append(self.session_command)
        if self.apps and not self.keep_awake:
            commands.append([self.adb, '-s', self.serial, 'shell', 'input', 'keyevent', '223'])
        for command in commands:
            try:
                result = self.runner(command, capture_output=True, text=True, timeout=15)
                results.append({'action': ' '.join(str(c) for c in command).replace(self.serial, '[phone]'),
                                'ok': result.returncode == 0})
            except (OSError, subprocess.TimeoutExpired) as error:
                results.append({'action': ' '.join(str(c) for c in command).replace(self.serial, '[phone]'),
                                'ok': False, 'error': str(error).replace(self.serial, '[phone]')})
        document = {'actions': results, 'ok': all(r['ok'] for r in results),
                    'sleep_requested': bool(self.apps and not self.keep_awake),
                    'keep_awake': self.keep_awake}
        if results and self.record and Path(self.record).parent.exists():
            write_json(self.record, document)
        if document['sleep_requested'] and results and results[-1]['ok']:
            print('Phone sleep requested; unlock it before another capture.', flush=True)
        return document

    def __exit__(self, kind, error, trace):
        if self.inherited_fd is not None:
            return False
        outcome = None
        try:
            # A repeated signal must not interrupt cleanup halfway through.
            for name in self.handlers:
                signal.signal(name, signal.SIG_IGN)
            outcome = self.cleanup()
        except Exception as cleanup_error:
            if kind is None:
                raise
            print('Cleanup record failed: ' + str(cleanup_error), file=sys.stderr)
        finally:
            for name, handler in self.handlers.items():
                signal.signal(name, handler)
            os.close(self.fd)
            self.fd = None
        if outcome and not outcome['ok']:
            if kind is None:
                raise RuntimeError('Device cleanup failed; see cleanup.json')
            print('Device cleanup also failed; original error retained', file=sys.stderr)
        return False
