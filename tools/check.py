#!/usr/bin/env python3
"""Local lint/regression/report gate; --staged checks exactly the Git index."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def check_links():
    files=[ROOT/'README.md',ROOT/'AGENTS.md',ROOT/'CLAUDE.md',ROOT/'docs/development-phone.md',
           ROOT/'tools/raw-camera-experiment/README.md',ROOT/'tools/raw-camera-experiment/probe/README.md',
           ROOT/'docs/development-checks.md', ROOT/'prototypes/capture-flow/README.md']
    for path in files:
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('http:','https:','#')):continue
            target=target.split('#')[0]
            # Historical image/JSON links are restored through VM backups, not the Git-only gate.
            if '.scratch' in Path(target).parts and Path(target).suffix!='.md':continue
            if not (path.parent/target).exists():raise ValueError(f'Broken link: {path.relative_to(ROOT)} -> {target}')


def prototype_check():
    html=(ROOT/'prototypes/capture-flow/index.html').read_text()
    scripts=re.findall(r'<script[^>]*>(.*?)</script>',html,re.S)
    for script in scripts:
        result=subprocess.run(['node','--check'],input=script,text=True,capture_output=True)
        if result.returncode:raise ValueError(result.stderr)
    pure=scripts[0].split('// PAGE SHELL')[0]
    assertions='''
const assert = require('node:assert/strict');
const original = JSON.stringify(SCENES);
const first = reduce(INITIAL, {type:'observe', sceneId:'beach'});
const snapshot = JSON.stringify(first);
const changed = reduce(first, {type:'conditions', change:'movement-starts'});
assert.equal(JSON.stringify(first), snapshot);
assert.equal(JSON.stringify(SCENES), original);
assert.equal(reduce(INITIAL, {type:'observe', sceneId:'beach'}).scene.movement, SCENES.beach.movement);
assert.equal(changed.scene.movement, 'moving');
'''
    result=subprocess.run(['node'],input=pure+'\n'+assertions,text=True,capture_output=True)
    if result.returncode:raise ValueError(result.stderr)


def gate():
    subprocess.run([sys.executable,'-m','ruff','check','tools','tests'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)
    check_links();prototype_check()
    for spec in __import__('json').loads((ROOT/'evidence/reports.json').read_text()):
        subprocess.run([sys.executable,ROOT/'tools/evidence.py','report',ROOT/spec['index'],ROOT/spec['report'],'--check'],check=True)
    print('Local gate passed: lint, regressions, links, prototype and report facts')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--staged',action='store_true');a=p.parse_args()
    candidates=[os.environ.get('SHUTRWISE_CHECK_PYTHON'),ROOT/'.venv/bin/python',Path.home()/'.local/share/shutrwise/raw-inspection/bin/python']
    interpreter=next((str(c) for c in candidates if c and Path(c).exists()),sys.executable)
    if Path(sys.executable).absolute()!=Path(interpreter).absolute():
        os.execv(interpreter,[interpreter,__file__,*sys.argv[1:]])
    if a.staged:
        with tempfile.TemporaryDirectory(prefix='shutrwise-staged-') as temporary:
            prefix=temporary+os.sep
            subprocess.run(['git','checkout-index','--all','--prefix='+prefix],cwd=ROOT,check=True)
            checker=Path(temporary)/'tools/check.py'
            if not checker.exists():raise ValueError('Stage the check tooling before running the staged gate')
            env=os.environ.copy();env['SHUTRWISE_CHECK_PYTHON']=sys.executable
            subprocess.run([sys.executable,checker],env=env,cwd=temporary,check=True)
    else:gate()


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        print('Check gate failed: '+str(error)+'\nSetup: python3 -m pip install -r requirements-dev.txt',file=sys.stderr)
        raise SystemExit(1)
