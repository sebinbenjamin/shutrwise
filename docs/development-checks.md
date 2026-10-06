# Local development gate

Create a local Python environment and install the pinned dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
python3 tools/check.py
python3 tools/install_hooks.py
```

Node is required for the prototype syntax/state checks. On this homelab, the gate also recognizes the existing `raw-inspection` Python environment. Set `SHUTRWISE_CHECK_PYTHON` to select another environment explicitly. Dependencies are installed during setup, never during a check.

The gate runs focused Ruff syntax/undefined-name rules, small no-phone regressions, maintained-link checks, prototype JavaScript checks and generated-report freshness. Missing dependencies fail the gate. There is no GitHub CI.

The pre-commit hook checks the staged source snapshot through `python3 tools/check.py --staged`. Stage all required tooling/configuration/index files together. The normal command checks the working tree. Hook installation preserves an existing custom hook configuration instead of replacing it.

The tests cover hashing/tampering, subset/status behavior, Bayer layouts, per-frame black calibration, shortest-source fallback, resource ownership and cleanup failure/interruption handling. Formula reconstruction remains independent of the production RAW helpers. Scientific-data and hardware checks are explicit, separate operations; the quick gate never connects to the phone or requires large local images.
