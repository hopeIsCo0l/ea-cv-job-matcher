from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data.schemas import JobInput
from src.scoring.labels import label_from_score
from src.scoring.text_utils import normalize_text


class TfidfScorer:
    def __init__(
        self,
        ngram_range: tuple[int, int] = (1, 2),
        max_features: int = 5000,
        stop_words: str | None = "english",
        sublinear_tf: bool = True,
    ) -> None:
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            stop_words=stop_words,
            sublinear_tf=sublinear_tf,
        )

    def score_jobs(self, cv_text: str, jobs: List[JobInput], top_terms_k: int = 5) -> List[dict]:
        normalized_cv = normalize_text(cv_text)
        if not normalized_cv:
            raise ValueError("cv_text is empty after normalization")
        if not jobs:
            raise ValueError("jobs list is empty")

        corpus = [normalized_cv] + [normalize_text(job.description) for job in jobs]
        matrix = self.vectorizer.fit_transform(corpus)

        cv_vector = matrix[0]
        job_matrix = matrix[1:]
        scores = cosine_similarity(cv_vector, job_matrix).flatten()
        feature_names = self.vectorizer.get_feature_names_out()
        cv_dense = cv_vector.toarray().ravel()

        results = []
        for idx, job in enumerate(jobs):
            score = float(scores[idx])
            job_dense = job_matrix[idx].toarray().ravel()
            contribution = cv_dense * job_dense
            top_indices = np.argsort(contribution)[::-1]
            top_terms = [
                feature_names[i]
                for i in top_indices
                if contribution[i] > 0
            ][:top_terms_k]

            results.append(
                {
                    "job_id": job.job_id,
                    "score": round(score, 6),
                    "label": label_from_score(score),
                    "top_terms": top_terms,
                }
            )

        ranked = sorted(results, key=lambda item: (-item["score"], item["job_id"]))
        for rank, item in enumerate(ranked, start=1):
            item["rank"] = rank
        return ranked
