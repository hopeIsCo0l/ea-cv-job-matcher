"""
Export an audit package: registry, config, evaluation snapshots, optional dataset.
Creates artifacts/audit_export_<UTC-timestamp>/ with manifest.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def _copy_if_exists(src: Path, dest: Path) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Phase 6 audit package")
    parser.add_argument(
        "--no-dataset",
        action="store_true",
        help="Exclude data/processed/dataset_v1.jsonl (large)",
    )
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "artifacts" / f"audit_export_{stamp}"
    out.mkdir(parents=True, exist_ok=True)

    included: list[str] = []

    reg = ROOT / "registry"
    if reg.is_dir():
        shutil.copytree(reg, out / "registry")
        included.append("registry/")

    for name in ("promotion_criteria.json", "monitoring_thresholds.json"):
        src = ROOT / "config" / name
        if _copy_if_exists(src, out / "config" / name):
            included.append(f"config/{name}")

    eval_dir = out / "evaluation"
    for rel in (
        "artifacts/phase2_baseline_reference.json",
        "artifacts/phase3_comparison.json",
        "artifacts/phase3_comparison_table.md",
        "artifacts/data_distribution.json",
        "artifacts/data_quality_report.md",
    ):
        src = ROOT / rel
        if _copy_if_exists(src, eval_dir / Path(rel).name):
            included.append(f"evaluation/{Path(rel).name}")

    if not args.no_dataset:
        ds = ROOT / "data" / "processed" / "dataset_v1.jsonl"
        if _copy_if_exists(ds, out / "data" / "processed" / "dataset_v1.jsonl"):
            included.append("data/processed/dataset_v1.jsonl")

    readme = "\n".join(
        [
            "Phase 6 audit export",
            f"Generated (UTC): {stamp}",
            "",
            "See docs/phase6-audit-package.md for contents and review checklist.",
            "",
            f"Included: {', '.join(included) if included else '(config/registry only)'}",
        ]
    )
    (out / "README_AUDIT.txt").write_text(readme, encoding="utf-8")

    manifest = {
        "export_type": "audit_package",
        "version": "1",
        "utc_timestamp": stamp,
        "git_commit": _git_sha(),
        "included_paths": included,
        "dataset_included": not args.no_dataset,
        "output_dir": str(out.relative_to(ROOT)),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
