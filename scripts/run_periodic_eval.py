"""
Periodic evaluation: regenerate Phase 2 pipeline, validate registry, run Phase 3 comparison.
Writes artifacts/periodic_eval_<UTC-timestamp>/ with manifest and key file copies.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def _git_sha() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "artifacts" / f"periodic_eval_{stamp}"
    out.mkdir(parents=True, exist_ok=True)

    _run([sys.executable, str(ROOT / "scripts" / "run_phase2_pipeline.py")])
    _run([sys.executable, str(ROOT / "scripts" / "validate_registry.py")])
    _run([sys.executable, str(ROOT / "scripts" / "run_phase3_comparison.py")])

    copies = [
        ("artifacts/phase2_baseline_reference.json", "phase2_baseline_reference.json"),
        ("artifacts/phase3_comparison.json", "phase3_comparison.json"),
        ("artifacts/phase3_comparison_table.md", "phase3_comparison_table.md"),
        ("artifacts/data_quality_report.md", "data_quality_report.md"),
        ("artifacts/eval_ready_summary.md", "eval_ready_summary.md"),
    ]
    for rel, name in copies:
        src = ROOT / rel
        if src.is_file():
            shutil.copy2(src, out / name)

    manifest = {
        "export_type": "periodic_eval",
        "version": "1",
        "utc_timestamp": stamp,
        "git_commit": _git_sha(),
        "scripts_run": [
            "scripts/run_phase2_pipeline.py",
            "scripts/validate_registry.py",
            "scripts/run_phase3_comparison.py",
        ],
        "output_dir": str(out.relative_to(ROOT)),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
