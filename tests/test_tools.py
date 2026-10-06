import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
sys.path.insert(0, str(ROOT/'tools/raw-camera-experiment/analysis'))
from device_lifecycle import DeviceBusy, DeviceRun
from file_integrity import manifest, sha256_file, verify_manifest, write_json
from evidence import cfa_label, facts, status, update_report, START, END
from raw_common import bayer_green, merge_bracket, normalize_raw, safe_ratio

spec = importlib.util.spec_from_file_location('batch', ROOT/'tools/raw-camera-experiment/batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


class ToolsTests(unittest.TestCase):
    def test_output_refusal_has_no_device_side_effects(self):
        from unittest.mock import patch
        import device_session
        spec=importlib.util.spec_from_file_location('probe_run',ROOT/'tools/raw-camera-experiment/probe/run.py')
        probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'normal').mkdir()
            record=root/'normal/cleanup.json';record.write_text('prior evidence')
            entries=[(batch,['--stage','capture','--lighting','normal','--output',str(root)]),
                     (probe,['--output',str(root/'normal')]),
                     (device_session,['--output',str(root/'normal'),'--launcher','agent-device','--config','config','--session','existing','--package','probe'])]
            for module,args in entries:
                with patch.object(sys,'argv',['tool',*args]), patch.object(module,'select_serial',side_effect=AssertionError('device selection')), patch.object(module,'DeviceRun',side_effect=AssertionError('device ownership')), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):module.main()
                self.assertEqual(record.read_text(),'prior evidence')
            calls=[]
            with DeviceRun('adb','fixture',state_dir=root,record=record,runner=lambda cmd,**kw:calls.append(cmd)):
                pass
            self.assertEqual(calls,[]);self.assertEqual(record.read_text(),'prior evidence')

    def test_cfa_numeric_freshness_and_verbose_failure(self):
        import copy
        index=json.loads((ROOT/'evidence/indexes/s22-all-camera-lighting-20261006.json').read_text())
        changed=copy.deepcopy(index)
        changed['conditions']['dark']['cameras'][0]['runs'][0]['frames'][1]['cfa']=[[0,1],[3,2]]
        self.assertNotEqual(facts(index),facts(changed))
        self.assertIn('Actual bracket EV',facts(index));self.assertIn('Focal lengths mm',facts(index));self.assertIn('Auto shutter ms',facts(index))
        camera=changed['conditions']['dark']['cameras'][0]
        camera['status']='capture_failed';camera['error']='fixture failure';camera['log_paths']=['dark/camera-0/control-01.log']
        text=status(changed,verbose=True)
        self.assertIn('fixture failure',text);self.assertIn('control-01.log',text)
        self.assertIn('--camera-ids 0',text);self.assertIn('-retry',text)
        camera['status']='skipped_missing_raw_or_manual_sensor'
        camera['analysis_status']='not_started'
        self.assertNotIn('Capture retry:',status(changed))

    def test_hash_manifest_and_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root/'file'; path.write_bytes(b'abc')
            self.assertEqual(sha256_file(path), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            document = manifest(root, [path]); verify_manifest(root, document)
            path.write_bytes(b'abd')
            with self.assertRaises(ValueError): verify_manifest(root, document)
            with self.assertRaises(ValueError): verify_manifest(root, {'files':[{'path':'../escape'}]})

    def test_subset_and_preserved_status(self):
        cameras = [{'camera_id':str(i),'status':'captured'} for i in range(4)]
        self.assertEqual([c['camera_id'] for c in batch.selected_cameras(cameras, ['2'])], ['2'])
        old = [{'camera_id':'0','status':'verified'}, {'camera_id':'2','status':'failed'}]
        new = [{'camera_id':'2','status':'verified'}]
        self.assertEqual(batch.merge_status(old,new),[old[0],new[0]])

    def test_all_bayer_green_positions(self):
        for pattern in [[[1,0],[2,3]], [[0,1],[3,2]], [[2,1],[3,0]], [[1,2],[0,3]]]:
            p = np.array(pattern)
            signal = np.where(np.isin(p,[1,3]), 12., 999.)
            self.assertEqual(bayer_green(signal,p).item(),12.)

    def test_black_calibration_and_signed_values(self):
        colors = np.array([[0,1],[2,3]])
        first = normalize_raw(np.full((2,2),70),colors,[65]*4,1023)
        second = normalize_raw(np.full((2,2),69),colors,[64]*4,1023)
        np.testing.assert_allclose(first,5/958)
        np.testing.assert_allclose(second,5/959)
        self.assertLess(normalize_raw(np.zeros((2,2)),colors,[64]*4,1023).max(),0)

    def test_shortest_fallback_and_unsaturated_merge(self):
        samples = [np.array([[1.,.1]],dtype=np.float32),np.array([[1.,.4]],dtype=np.float32),
                   np.array([[1.,.8]],dtype=np.float32),np.array([[1.,.4]],dtype=np.float32)]
        radiance,weights,total,fallback,result = merge_bracket(samples,[.25,1,2,1])
        self.assertTrue(fallback[0,0]); self.assertEqual(result[0,0],4)
        self.assertFalse(fallback[0,1]); self.assertAlmostEqual(float(result[0,1]),.4,places=6)
        self.assertTrue(all(w[0,0]==0 for w in weights))

    def test_lifecycle_success_failure_and_interruption(self):
        for exception in [None,ValueError('original'),KeyboardInterrupt()]:
            calls=[]
            def runner(command, **kwargs):
                calls.append(command);return subprocess.CompletedProcess(command,0)
            with tempfile.TemporaryDirectory() as folder:
                owner=DeviceRun('adb','test-phone',state_dir=folder,runner=runner,
                                record=Path(folder)/'cleanup.json',owned_session_command=['agent-device','close','--session','owned'])
                try:
                    with owner:
                        owner.started('dev.shutrwise.probe')
                        if exception: raise exception
                except (ValueError,KeyboardInterrupt) as error:
                    self.assertIs(error,exception)
                self.assertIn('force-stop',calls[0]);self.assertEqual(calls[1][1],'close')
                self.assertEqual(calls[2][-2:],['keyevent','223'])
                self.assertTrue(json.loads((Path(folder)/'cleanup.json').read_text())['ok'])
                self.assertIsNone(owner.fd)
                self.assertTrue(all('test-phone' not in c['action'] for c in json.loads((Path(folder)/'cleanup.json').read_text())['actions']))

    def test_cleanup_failure_keeps_original_and_attempts_sleep(self):
        calls=[]
        def bad(command, **kwargs):
            calls.append(command);return subprocess.CompletedProcess(command,1)
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(ValueError,'original'):
                with DeviceRun('adb','test',state_dir=folder,runner=bad) as owner:
                    owner.started('probe');raise ValueError('original')
            self.assertEqual(calls[-1][-1],'223')

    def test_lease_competition_inheritance_and_keep_awake(self):
        calls=[]
        def runner(command,**kwargs):calls.append(command);return subprocess.CompletedProcess(command,0)
        with tempfile.TemporaryDirectory() as folder:
            with DeviceRun('adb','test',state_dir=folder,runner=runner,keep_awake=True) as outer:
                outer.started('probe')
                with self.assertRaises(DeviceBusy):
                    with DeviceRun('adb','test',state_dir=folder,runner=runner):pass
                with DeviceRun('adb','test',state_dir=folder,runner=runner,inherited_fd=outer.fd) as child:
                    child.started('probe')
                self.assertEqual(calls,[])
            self.assertEqual(len(calls),1)
            with DeviceRun('adb','test',state_dir=folder,runner=runner):pass
            self.assertEqual(len(calls),1)

    def test_signal_raises_for_finalizer(self):
        with self.assertRaises(KeyboardInterrupt):DeviceRun._interrupted(signal.SIGTERM,None)


    def test_zero_signal_ratio_is_missing_not_infinity(self):
        self.assertIsNone(safe_ratio(1,0));self.assertIsNone(safe_ratio(float('nan'),1))
        self.assertEqual(safe_ratio(2,4),.5)

    def test_generated_facts_and_stale_report(self):
        self.assertEqual(cfa_label([[1,0],[2,3]],'RGBG'),'GRBG')
        self.assertEqual(cfa_label([[0,1],[3,2]],'RGBG'),'RGGB')
        index=json.loads((ROOT/'evidence/indexes/s22-all-camera-lighting-20261006.json').read_text())
        self.assertIn('GRBG',facts(index));self.assertIn('RGGB',facts(index))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'index.json';report=Path(folder)/'report.md'
            write_json(path,index);report.write_text(START+'\n'+END)
            update_report(path,report);update_report(path,report,check=True)
            report.write_text(report.read_text().replace('GRBG','GBRG'))
            with self.assertRaisesRegex(ValueError,'stale'):update_report(path,report,check=True)

    def test_status_incomplete_and_failed_physical_path(self):
        document={'device':'fixture','experiment':'run','source_root':'.scratch/fixture',
                  'conditions':{'normal':{'cameras':[],'physical':[{'camera_id':'6','status':'direct_open_failed'}]}}}
        text=status(document)
        self.assertIn('not counted',text);self.assertIn('--lighting dark',text)
        self.assertIn('cleanup: not_recorded',text)

    def test_signal_cleanup_and_cleanup_failure_after_success(self):
        def bad(command,**kwargs):return subprocess.CompletedProcess(command,1)
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                with DeviceRun('adb','signal',state_dir=folder,runner=bad) as owner:
                    owner.started('probe');os.kill(os.getpid(),signal.SIGTERM)
            with self.assertRaisesRegex(RuntimeError,'cleanup failed'):
                with DeviceRun('adb','signal',state_dir=folder,runner=bad) as owner:owner.started('probe')

    def test_large_hash_uses_stream_and_source_manifest_stays_fixed(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);original=root/'original.bin'
            with original.open('wb') as stream:
                for _ in range(16):stream.write(b'x'*65536)
            with patch.object(Path,'read_bytes',side_effect=AssertionError('whole-file read')):
                source=manifest(root,[original])
            write_json(root/'source-manifest.json',source)
            digest=sha256_file(root/'source-manifest.json')
            derived=root/'derived.txt';derived.write_text('derived')
            write_json(root/'analysis-manifest.json',manifest(root,[derived]))
            self.assertEqual(sha256_file(root/'source-manifest.json'),digest)


if __name__ == '__main__':unittest.main()
