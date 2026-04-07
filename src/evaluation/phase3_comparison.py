"""
Phase 3: train candidate classifiers on shared TF-IDF pair features;
evaluate same ranking metrics + latency + artifact size vs TF-IDF baseline.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.config.settings import (
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    TFIDF_STOP_WORDS,
    TFIDF_SUBLINEAR_TF,
)
from src.data.schemas import JobInput
from src.evaluation.metrics import compute_metrics
from src.scoring.engine import TfidfScorer

# y encoding: 0=bad, 1=medium, 2=good — matches ordinal ranking weight
LABEL_TO_Y = {"bad": 0, "medium": 1, "good": 2}
Y_WEIGHT = np.array([0.0, 1.0, 2.0])  # ordinal relevance for ranking (same scale for every pair)


def pair_text(row: dict) -> str:
    return f"{row['cv_text']} {row['job_description']}"


def load_dataset_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def split_cv_ids(
    rows: list[dict], test_size: float = 0.2, random_state: int = 42
) -> tuple[set[str], set[str]]:
    cv_ids = sorted({r["cv_id"] for r in rows})
    buckets = {r["cv_id"]: r.get("match_bucket", "unknown") for r in rows}
    stratify = [buckets[cid] for cid in cv_ids]
    train_ids, test_ids = train_test_split(
        cv_ids, test_size=test_size, random_state=random_state, stratify=stratify
    )
    return set(train_ids), set(test_ids)


def rows_for_cvs(rows: list[dict], cv_ids: set[str]) -> list[dict]:
    return [r for r in rows if r["cv_id"] in cv_ids]


def proba_ordinal_score(proba: np.ndarray, classes: np.ndarray) -> np.ndarray:
    """Comparable relevance: 2*P(good)+P(medium)+0*P(bad) using sklearn class column order."""
    out = np.zeros(proba.shape[0], dtype=np.float64)
    for i, c in enumerate(classes):
        y = int(c)
        out += proba[:, i] * Y_WEIGHT[y]
    return out


def evaluate_ranking_for_test_cvs(
    test_rows: list[dict],
    score_fn: Callable[[str, list[dict]], np.ndarray],
) -> tuple[list[dict], dict]:
    """Group test rows by cv_id (8 jobs each). score_fn(cv_id, group) -> scores aligned with group order."""
    by_cv: dict[str, list[dict]] = {}
    for r in test_rows:
        by_cv.setdefault(r["cv_id"], []).append(r)
    per_sample = []
    for cv_id, group in by_cv.items():
        group = sorted(group, key=lambda x: x["job_id"])
        target = group[0]["target_job_id"]
        scores = np.asarray(score_fn(cv_id, group), dtype=np.float64)
        job_ids = [x["job_id"] for x in group]
        ranked = sorted(zip(job_ids, scores), key=lambda x: (-float(x[1]), x[0]))
        predicted_ids = [j for j, _ in ranked]
        per_sample.append(
            {
                "sample_id": cv_id,
                "expected_top1_job_id": target,
                "predicted_top1_job_id": predicted_ids[0] if predicted_ids else None,
                "predicted_ranking": predicted_ids,
                "top_score": float(ranked[0][1]) if ranked else 0.0,
                "top_label": "medium",
            }
        )
    metrics = compute_metrics(per_sample)
    return per_sample, metrics


def run_phase3_comparison(
    dataset_path: Path,
    artifacts_dir: Path,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    rows = load_dataset_jsonl(dataset_path)
    train_cv_ids, test_cv_ids = split_cv_ids(rows, test_size=test_size, random_state=random_state)
    train_rows = rows_for_cvs(rows, train_cv_ids)
    test_rows = rows_for_cvs(rows, test_cv_ids)

    texts_train = [pair_text(r) for r in train_rows]
    y_train = np.array([LABEL_TO_Y[r["expected_label"]] for r in train_rows])

    vectorizer = TfidfVectorizer(
        ngram_range=TFIDF_NGRAM_RANGE,
        max_features=TFIDF_MAX_FEATURES,
        stop_words=TFIDF_STOP_WORDS,
        sublinear_tf=TFIDF_SUBLINEAR_TF,
    )
    X_train = vectorizer.fit_transform(texts_train)

    models: dict[str, Any] = {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        ),
        # Linear margin model with proper multiclass probabilities (approx. linear SVM family)
        "linear_svm_sgd_modified_huber": SGDClassifier(
            loss="modified_huber",
            penalty="l2",
            alpha=1e-4,
            max_iter=3000,
            random_state=random_state,
            class_weight="balanced",
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_depth=6,
            max_iter=200,
            random_state=random_state,
        ),
    }

    fitted: dict[str, Any] = {}
    for name, clf in models.items():
        if name == "hist_gradient_boosting":
            X_fit = X_train.toarray().astype(np.float32, copy=False)
            fitted[name] = clf.fit(X_fit, y_train)
        else:
            fitted[name] = clf.fit(X_train, y_train)

    # Canonical job list for baseline scorer (same 8 roles)
    job_defs: dict[str, dict] = {}
    for r in rows:
        job_defs[r["job_id"]] = {
            "job_id": r["job_id"],
            "title": r["job_title"],
            "description": r["job_description"],
            "company_name": r["company_name"],
        }
    jobs_list = sorted(job_defs.values(), key=lambda x: x["job_id"])
    job_inputs = [
        JobInput(
            job_id=j["job_id"],
            title=j["title"],
            description=j["description"],
            company_name=j["company_name"],
        )
        for j in jobs_list
    ]
    baseline_scorer = TfidfScorer()

    out_dir = artifacts_dir / "phase3_models"
    out_dir.mkdir(parents=True, exist_ok=True)

    def save_bundle(name: str, vec: TfidfVectorizer, clf: Any) -> int:
        bundle = {
            "vectorizer": vec,
            "classifier": clf,
            "label_to_y": LABEL_TO_Y,
        }
        path = out_dir / f"{name}.joblib"
        joblib.dump(bundle, path)
        return path.stat().st_size

    results: list[dict[str, Any]] = []

    # --- Baseline TF-IDF cosine (same test CVs, same 8 jobs) ---
    def baseline_scores(_cv_id: str, group: list[dict]) -> np.ndarray:
        cv_text = group[0]["cv_text"]
        ranked = baseline_scorer.score_jobs(cv_text, job_inputs)
        by_job = {r["job_id"]: r["score"] for r in ranked}
        return np.array([by_job[j["job_id"]] for j in group])

    _, baseline_metrics = evaluate_ranking_for_test_cvs(test_rows, baseline_scores)

    first_test_cv = sorted(test_cv_ids)[0]
    sample_group = sorted(
        [r for r in test_rows if r["cv_id"] == first_test_cv],
        key=lambda x: x["job_id"],
    )
    latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        baseline_scores(sample_group[0]["cv_id"], sample_group)
        latencies.append((time.perf_counter() - t0) * 1000)
    baseline_latency_ms = float(np.median(latencies))

    results.append(
        {
            "model_name": "tfidf_cosine_baseline",
            "top1_accuracy": baseline_metrics["top1_accuracy"],
            "top3_hit_rate": baseline_metrics["top3_hit_rate"],
            "mrr": baseline_metrics["mrr"],
            "inference_latency_ms_median": round(baseline_latency_ms, 4),
            "artifact_size_bytes": 0,
            "notes": "Shared-corpus TF-IDF in process; no separate model file",
        }
    )

    baseline_row = results[0]
    X_test_all = vectorizer.transform([pair_text(r) for r in test_rows])
    y_test = np.array([LABEL_TO_Y[r["expected_label"]] for r in test_rows])

    for name, clf in fitted.items():
        X_eval = (
            X_test_all.toarray().astype(np.float32, copy=False)
            if name == "hist_gradient_boosting"
            else X_test_all
        )
        y_pred = clf.predict(X_eval)
        pair_acc = accuracy_score(y_test, y_pred)

        def make_scorer(model: Any, model_name: str) -> Callable[[str, list[dict]], np.ndarray]:
            def scores_fn(_cv_id: str, group: list[dict]) -> np.ndarray:
                Xg = vectorizer.transform([pair_text(r) for r in group])
                if model_name == "hist_gradient_boosting":
                    Xg = Xg.toarray().astype(np.float32, copy=False)
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(Xg)
                    return proba_ordinal_score(proba, model.classes_)
                dv = model.decision_function(Xg)
                if dv.ndim == 1:
                    return dv
                exp = np.exp(dv - dv.max(axis=1, keepdims=True))
                p = exp / exp.sum(axis=1, keepdims=True)
                return proba_ordinal_score(p, model.classes_)

            return scores_fn

        scorer_fn = make_scorer(clf, name)
        _, m = evaluate_ranking_for_test_cvs(test_rows, scorer_fn)

        g = sample_group
        lat_ms = []
        for _ in range(50):
            t0 = time.perf_counter()
            Xg = vectorizer.transform([pair_text(r) for r in g])
            if name == "hist_gradient_boosting":
                Xg = Xg.toarray().astype(np.float32, copy=False)
            if hasattr(clf, "predict_proba"):
                proba_ordinal_score(clf.predict_proba(Xg), clf.classes_)
            else:
                dv = clf.decision_function(Xg)
                if dv.ndim == 1:
                    pass
                else:
                    exp = np.exp(dv - dv.max(axis=1, keepdims=True))
                    p = exp / exp.sum(axis=1, keepdims=True)
                    proba_ordinal_score(p, clf.classes_)
            lat_ms.append((time.perf_counter() - t0) * 1000)

        total_bytes = save_bundle(name, vectorizer, clf)

        results.append(
            {
                "model_name": name,
                "top1_accuracy": m["top1_accuracy"],
                "top3_hit_rate": m["top3_hit_rate"],
                "mrr": m["mrr"],
                "pair_accuracy_on_test_rows": round(float(pair_acc), 4),
                "inference_latency_ms_median": round(float(np.median(lat_ms)), 4),
                "artifact_size_bytes": total_bytes,
            }
        )

    # Promotion vs same-run baseline (same test split)
    best = max(
        (r for r in results if r["model_name"] != "tfidf_cosine_baseline"),
        key=lambda r: (r["top1_accuracy"], r["mrr"]),
    )
    beats = (
        best["top1_accuracy"] >= baseline_row["top1_accuracy"] + 0.05
        and best["top3_hit_rate"] >= baseline_row["top3_hit_rate"]
        and best["mrr"] > baseline_row["mrr"]
    )
    promotion = {
        "baseline_on_this_split": {
            "top1_accuracy": baseline_row["top1_accuracy"],
            "top3_hit_rate": baseline_row["top3_hit_rate"],
            "mrr": baseline_row["mrr"],
        },
        "best_candidate": best["model_name"],
        "beats_baseline_on_same_split": beats,
        "recommendation": "promote_candidate" if beats else "defer_to_tfidf",
        "test_split": {
            "test_size": test_size,
            "random_state": random_state,
            "n_train_cvs": len(train_cv_ids),
            "n_test_cvs": len(test_cv_ids),
        },
    }

    comparison = {
        "dataset": str(dataset_path),
        "tfidf_config": {
            "ngram_range": list(TFIDF_NGRAM_RANGE),
            "max_features": TFIDF_MAX_FEATURES,
            "stop_words": TFIDF_STOP_WORDS,
            "sublinear_tf": TFIDF_SUBLINEAR_TF,
        },
        "results": results,
        "promotion": promotion,
    }

    (artifacts_dir / "phase3_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    (artifacts_dir / "phase3_comparison_table.md").write_text(
        _format_markdown_table(results, promotion), encoding="utf-8"
    )

    return comparison


def _format_markdown_table(results: list[dict], promotion: dict) -> str:
    lines = [
        "# Phase 3 Model Comparison (same train/test split, shared TF-IDF features)",
        "",
        "| Model | Top-1 | Top-3 | MRR | Latency ms (median) | Artifact bytes |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in results:
        lines.append(
            f"| {r['model_name']} | {r['top1_accuracy']} | {r['top3_hit_rate']} | {r['mrr']} | "
            f"{r['inference_latency_ms_median']} | {r['artifact_size_bytes']} |"
        )
    lines.append("")
    lines.append(f"- **Best candidate:** `{promotion.get('best_candidate')}`")
    lines.append(
        f"- **Beats same-split baseline (+0.05 Top-1, Top-3 not worse, MRR higher):** "
        f"`{promotion.get('beats_baseline_on_same_split')}`"
    )
    lines.append(f"- **Recommendation:** `{promotion.get('recommendation')}`")
    lines.append("")
    lines.append(
        "If no candidate clearly beats the baseline, keep TF-IDF as production scorer. "
        "See `docs/phase3-promotion-criteria.md` for business gates vs frozen Phase 2 numbers."
    )
    return "\n".join(lines)
