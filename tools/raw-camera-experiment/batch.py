#!/usr/bin/env python3
"""Sequential RAW acquisitions, followed by a separate desktop analysis stage."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = 'dev.shutrwise.probe'

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, log, serial=None):
    result = subprocess.run([str(v) for v in command], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=180)
    output = result.stdout.replace(serial, '[development phone]') if serial else result.stdout
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(output)
    if result.returncode:
        raise RuntimeError(f'Command exited {result.returncode}; see {log.name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['capture', 'analyze'], required=True)
    parser.add_argument('--lighting', choices=['normal', 'dark'], required=True)
    parser.add_argument('--output', type=Path, required=True, help='Shared root for both lighting conditions')
    parser.add_argument('--adb', default='/usr/bin/adb')
    parser.add_argument('--device', help='Authorized ADB serial; omitted from saved records')
    parser.add_argument('--analysis-python', type=Path, default=Path.home()/'.local/share/shutrwise/raw-inspection/bin/python')
    parser.add_argument('--camera-ids', nargs='+', help='Optional subset of directly listed cameras')
    parser.add_argument('--skip-physical-check', action='store_true')
    args = parser.parse_args()
    folder = args.output.resolve()/args.lighting
    errors = []
    if args.stage == 'capture':
        if folder.exists():
            parser.error('Lighting output already exists. Originals are never overwritten; choose a new root.')
        devices = subprocess.check_output([args.adb, 'devices'], text=True)
        online = [line.split()[0] for line in devices.splitlines() if len(line.split())>=2 and line.split()[1]=='device']
        serial = args.device or (online[0] if len(online)==1 else None)
        if serial not in online:
            parser.error('Select one connected, authorized phone with --device.')
        adb = [args.adb, '-s', serial]
        apk = HERE/'probe/build/probe.apk'
        if not apk.exists():
            parser.error('Build the probe first with python3 probe/build.py.')
        location = subprocess.check_output(adb+['shell','pm','path',PACKAGE], text=True).strip()
        if not location.startswith('package:') or '\n' in location:
            parser.error('Install this probe APK first; one package APK is required.')
        installed = subprocess.check_output(adb+['shell','sha256sum',location.removeprefix('package:')], text=True).split()[0]
        if installed != digest(apk):
            parser.error('Installed APK differs from local probe/build/probe.apk. Install the intended build first.')
        folder.mkdir(parents=True)
        save(folder/'conditions.json', {'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'lighting_label': args.lighting, 'setup': 'Owner requested fixed-phone lighting comparison; no lux or flicker measurement.',
             'protocol': 'Three control quartets per directly listed RAW+MANUAL_SENSOR camera; physical IDs attempted once in single mode.',
             'caveat': 'Different focal lengths and front cameras see different fields of view. Front IDs may be overlapping paths, not distinct sensors.',
             'probe_apk_sha256': installed, 'capture_runner_sha256': digest(HERE/'probe/run.py')})
        common = [sys.executable, HERE/'probe/run.py', '--adb',args.adb,'--device',serial,'--skip-install']
        run(common+['--action','capabilities','--output',folder/'capabilities'],folder/'capabilities.log',serial)
        capabilities = json.loads((folder/'capabilities/capabilities.json').read_text())
        listed = capabilities['listed_cameras']
        known = {c['id'] for c in listed}
        if args.camera_ids and not set(args.camera_ids)<=known:
            parser.error('--camera-ids must be directly listed IDs from the fresh capability dump.')
        records = []
        def acquire(c, physical=False):
            camera_id = c['id']
            if not re.fullmatch(r'[a-zA-Z0-9_.-]+',camera_id):
                raise ValueError('Unsafe camera ID in capability report')
            meta = c['characteristics']; caps = meta.get('android.request.availableCapabilities',[])
            record = {'camera_id':camera_id,'directly_listed':not physical,'lens_facing':meta.get('android.lens.facing'),
                      'focal_lengths_mm':meta.get('android.lens.info.availableFocalLengths'), 'status':'pending','runs':[]}
            records.append(record)
            if not {1,3}<=set(caps):
                record['status']='skipped_missing_raw_or_manual_sensor';return
            base = folder/('physical-'+camera_id if physical else 'camera-'+camera_id)
            print('Capturing',base.name,flush=True)
            for index in range(1,2 if physical else 4):
                name='single-access-check' if physical else f'control-{index:02d}'
                destination=base/'captures'/name
                try:
                    run(common+['--action','capture','--camera-id',camera_id,'--mode','single' if physical else 'control','--output',destination],base/(name+'.log'),serial)
                    capture=json.loads((destination/'run.json').read_text())
                    expected=1 if physical else 4
                    if capture['state']!='FINISHED' or len(list(destination.glob('frame-*.dng')))!=expected:
                        raise RuntimeError('Missing finished capture or expected DNG files')
                    record['runs'].append({'name':name,'state':'saved','dngs':expected})
                    print(base.name,name,'saved',expected,'DNGs',flush=True)
                except (RuntimeError,subprocess.TimeoutExpired) as error:
                    record['status']='direct_open_failed' if physical else 'capture_failed'
                    record['error']=str(error)
                    if (destination/'run.json').exists():
                        record['device_error']=json.loads((destination/'run.json').read_text()).get('error')
                    if not physical: errors.append(camera_id)
                    print(base.name,record['status'],record.get('device_error') or record['error'],flush=True)
                    break
            else:
                record['status']='single_access_confirmed' if physical else 'captured'
            save(folder/'capture-status.json',{'cameras':records})
        for c in listed:
            if not args.camera_ids or c['id'] in args.camera_ids: acquire(c)
        if not args.skip_physical_check:
            for c in capabilities.get('additional_physical_camera_characteristics',[]):
                if 'characteristics' in c: acquire(c,physical=True)
        save(folder/'capture-status.json',{'cameras':records,'uncompleted_listed_camera_ids':errors})
    else:
        status=json.loads((folder/'capture-status.json').read_text())
        records=[]
        for c in status['cameras']:
            if c['status']!='captured':continue
            base=folder/('camera-'+c['camera_id'])
            if (base/'comparison').exists():
                parser.error(f'Analysis output already exists for {base.name}. Preserve it and use a fresh capture root.')
            record={'camera_id':c['camera_id'],'status':'pending'};records.append(record)
            try:
                run([args.analysis_python,HERE/'analysis/compare.py','--source',base/'captures','--output',base/'comparison'],base/'comparison.log')
                run([args.analysis_python,HERE/'analysis/long_control_audit.py',base/'captures',base/'source-audit.json'],base/'source-audit.log')
                run([args.analysis_python,HERE/'analysis/verify_long_control.py',base/'captures',base/'comparison',base/'pipeline-verification.json'],base/'pipeline-verification.log')
                record['status']='verified';print(base.name,'analysis verified',flush=True)
            except (RuntimeError,subprocess.TimeoutExpired) as error:
                record['status']='analysis_failed';record['error']=str(error);errors.append(c['camera_id'])
                print(base.name,record['error'],flush=True)
            save(folder/'analysis-status.json',{'cameras':records})
    files=[{'path':str(p.relative_to(folder)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='manifest.json']
    save(folder/'manifest.json',{'files':files})
    print(args.stage,'complete for',args.lighting,'; failures:',errors,flush=True)
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
