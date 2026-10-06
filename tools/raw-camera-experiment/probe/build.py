#!/usr/bin/env python3
"""THROWAWAY APK build with official SDK tools; no Gradle or app framework."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import zipfile


def build():
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path.home() / '.local/share/shutrwise/android'
    parser.add_argument('--sdk', type=Path, default=base / 'sdk')
    parser.add_argument('--java-home', type=Path)
    args = parser.parse_args()
    java = args.java_home or Path((base / 'java-home.txt').read_text().strip())
    root = Path(__file__).resolve().parent
    sdk = args.sdk.resolve()
    bt = sdk / 'build-tools/36.0.0'
    android = sdk / 'platforms/android-36/android.jar'
    out = root / 'build'
    out.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['JAVA_HOME'] = str(java)
    env['PATH'] = str(java / 'bin') + os.pathsep + env.get('PATH', '')
    trust = base / 'android-truststore.jks'
    if trust.exists():
        env['JAVA_TOOL_OPTIONS'] = '-Djavax.net.ssl.trustStore=' + str(trust)

    def run(*cmd):
        subprocess.run([str(x) for x in cmd], check=True, env=env, cwd=root)

    classes = out / 'classes'
    dex = out / 'dex'
    classes.mkdir(exist_ok=True)
    dex.mkdir(exist_ok=True)
    sources = sorted((root / 'src').rglob('*.java'))
    run(java / 'bin/javac', '--release', '8', '-classpath', android,
        '-d', classes, *sources)
    jar = out / 'classes.jar'
    with zipfile.ZipFile(jar, 'w') as z:
        for f in classes.rglob('*.class'):
            z.write(f, f.relative_to(classes))
    run(bt / 'd8', '--lib', android, '--min-api', '28', '--output', dex, jar)
    unsigned = out / 'probe-unsigned.apk'
    run(bt / 'aapt2', 'link', '-I', android, '--manifest', root / 'AndroidManifest.xml',
        '-o', unsigned)
    with zipfile.ZipFile(unsigned, 'a', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(dex / 'classes.dex', 'classes.dex')
    aligned = out / 'probe-aligned.apk'
    run(bt / 'zipalign', '-f', '4', unsigned, aligned)
    keydir = base / 'probe-signing'
    keydir.mkdir(mode=0o700, exist_ok=True)
    key = keydir / 'debug.keystore'
    if not key.exists():
        run(java / 'bin/keytool', '-genkeypair', '-keystore', key,
            '-storepass', 'android', '-keypass', 'android', '-alias', 'probe',
            '-keyalg', 'RSA', '-validity', '3650', '-dname', 'CN=Shutrwise Throwaway Probe')
        key.chmod(0o600)
    apk = out / 'probe.apk'
    run(bt / 'apksigner', 'sign', '--ks', key, '--ks-key-alias', 'probe',
        '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', apk, aligned)
    run(bt / 'apksigner', 'verify', apk)
    print(apk)


if __name__ == '__main__':
    build()
