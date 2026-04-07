# API Contract

## `POST /v1/score`

### Request
```json
{
  "cv_text": "string",
  "jobs": [
    {
      "job_id": "string",
      "title": "string",
      "description": "string",
      "company_name": "string"
    }
  ],
  "top_k": 8
}
```

### Behavior
- Accepts one CV and job list.
- Filters to Ethiopian Airlines jobs only.
- Keeps only supported trainee titles in this phase:
  - Trainee Pilot
  - Trainee Cabin Crew
  - Trainee Aircraft Mechanic
  - Trainee Avionics Technician
  - Trainee Power Plant Technician
  - Trainee Ground Operations Officer
  - Trainee Customer Service Agent
  - Trainee Finance / Accounting (College, Trainee)
- Enforces max 8 jobs by deterministic trimming: sort by `(job_id.lower(), title.lower())`, keep first 8.
- Scores with TF-IDF + cosine and ranks descending.

### Success Response
```json
{
  "request_id": "uuid",
  "scorer_source": "baseline_tfidf_cosine_v1",
  "ranked_results": [
    {
      "rank": 1,
      "job_id": "et-ground-001",
      "score": 0.5123,
      "label": "good",
      "top_terms": ["operations", "baggage", "ramp"]
    }
  ],
  "excluded_jobs": [
    {"job_id": "x", "reason": "non-ethiopian"}
  ],
  "latency_ms": 7.2
}
```

### Error Response
```json
{
  "detail": "user-friendly message",
  "request_id": "uuid"
}
```

## Health Endpoints
- `GET /health` -> `{ "status": "ok" }`
- `GET /ready` -> `{ "status": "ready", "scorer_source": "baseline_tfidf_cosine_v1" }`
