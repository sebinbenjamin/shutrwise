#!/usr/bin/env python3
"""Install the local gate without replacing another user's hook setup."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    configured=subprocess.run(['git','config','--get','core.hooksPath'],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    if configured and configured!='.githooks':raise SystemExit('Existing core.hooksPath preserved: '+configured+'; integrate the gate manually.')
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=ROOT,text=True).strip())
    if not configured and (gitdir/'hooks/pre-commit').exists():raise SystemExit('Existing pre-commit hook preserved; integrate tools/check.py --staged manually.')
    subprocess.run(['git','config','--local','core.hooksPath','.githooks'],cwd=ROOT,check=True)
    print('Local pre-commit gate installed')


if __name__=='__main__':main()
