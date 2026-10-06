# Evidence in Git and VM backups

Git tracks compact [indexes](indexes/) and [report mappings](reports.json). They preserve camera coverage, exposure/calibration metadata, source hashes and analysis outcomes without the large RAW corpus. The capture-flow source is tracked under [prototypes](../prototypes/capture-flow/README.md).

Original DNGs, full metadata and derived images remain in `.scratch/shutrwise/assets/`, covered by the owner's regular VM backups. Restore those files through the VM backup procedure when needed. A Git clone alone does not restore them. No separate image archive or off-VM storage service is required by this project.

Export or refresh a compact index after capture and analysis:

```bash
python3 tools/evidence.py index .scratch/shutrwise/assets/s22-ultra/all-camera-lighting-20261006 \
  --device 'S22 Ultra SM-S908E' --output evidence/indexes/s22-all-camera-lighting-20261006.json
```

Get offline status, generate facts, or verify sources restored from a VM backup:

```bash
python3 tools/evidence.py status evidence/indexes/s22-all-camera-lighting-20261006.json
python3 tools/evidence.py report evidence/indexes/s22-all-camera-lighting-20261006.json docs/research/all-camera-lighting-20261006.md
python3 tools/evidence.py verify evidence/indexes/s22-all-camera-lighting-20261006.json
```

`status --verbose` includes failure descriptions and detailed log paths. Failed runs receive retry commands using a fresh output root; preserve existing evidence and choose another suffix if that retry root already exists.

`status --json` returns structured records. `verify --root /restored/experiment` checks a restored tree without changing the index. Index export reads existing source manifests; explicit verification reads the actual bytes with streaming hashes. Generated report blocks retain the distinction between direct paths, failed physical access and untested hardware.
