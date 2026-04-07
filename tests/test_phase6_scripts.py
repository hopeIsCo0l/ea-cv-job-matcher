"""Smoke tests for Phase 6 audit/export scripts."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_export_audit_package_runs():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_audit_package.py"), "--no-dataset"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    # Find latest audit_export_* under artifacts
    artifacts = ROOT / "artifacts"
    dirs = sorted(artifacts.glob("audit_export_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    assert dirs, "expected audit_export_* directory"
    latest = dirs[0]
    manifest = json.loads((latest / "manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("export_type") == "audit_package"
    assert (latest / "README_AUDIT.txt").is_file()


@pytest.mark.slow
def test_run_periodic_eval_optional():
    """Optional: run full periodic pipeline (slow). Skip with pytest -m 'not slow'."""
    pytest.skip("Run manually: python scripts/run_periodic_eval.py")
