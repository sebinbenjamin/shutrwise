"""Bounded-memory file hashing and atomic JSON manifests."""
import hashlib
import json
import os
from pathlib import Path
import tempfile


def sha256_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def manifest(root, files):
    root = Path(root).resolve()
    entries = []
    for path in sorted(files):
        path = Path(path)
        relative = path.resolve().relative_to(root)
        if path.is_symlink():
            raise ValueError('Manifest input must not be a symlink')
        entries.append({'path': relative.as_posix(), 'bytes': path.stat().st_size,
                        'sha256': sha256_file(path)})
    return {'version': 1, 'files': entries}


def verify_manifest(root, document):
    root = Path(root).resolve()
    for item in document['files']:
        relative = Path(item['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe manifest path')
        path = root / relative
        path.resolve().relative_to(root)
        if path.is_symlink() or path.stat().st_size != item['bytes'] or sha256_file(path) != item['sha256']:
            raise ValueError('Manifest mismatch: ' + item['path'])
