# Integration Guide (External Backend)

## Endpoint
- Base URL: `http://<host>:8000`
- Score API: `POST /v1/score`
- Auth: add gateway/API-key in front of this service (placeholder for now).

## Recommended Client Behavior
- Timeout: 3-5 seconds.
- Retries: up to 2 retries with exponential backoff (e.g. 200ms, 500ms).
- Circuit breaker: open if repeated failures exceed threshold.

## Fallback Rule
If AI service is unavailable or times out, caller should return neutral response:
```json
{
  "request_id": "caller-generated-id",
  "scorer_source": "fallback_unavailable",
  "ranked_results": [],
  "excluded_jobs": [],
  "latency_ms": 0
}
```

## Versioning Strategy
- Path-versioned API (`/v1/score`, future `/v2/score`).
- `scorer_source` identifies model/scoring implementation lineage.
- Keep contract backward compatible within same `v1` path.

## Example Request
```json
{
  "cv_text": "Aviation operations graduate with strong customer support exposure.",
  "jobs": [
    {
      "job_id": "et-cs-001",
      "title": "Trainee Customer Service Agent",
      "description": "Airport check-in and passenger issue resolution",
      "company_name": "Ethiopian Airlines"
    }
  ],
  "top_k": 8
}
```
