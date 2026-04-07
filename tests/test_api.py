from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def _base_jobs():
    return [
        {
            "job_id": "et-ground-001",
            "title": "Trainee Ground Operations Officer",
            "description": "Ramp and baggage coordination in airport operations",
            "company_name": "Ethiopian Airlines",
        },
        {
            "job_id": "et-cabin-001",
            "title": "Trainee Cabin Crew",
            "description": "Passenger service and cabin safety checks",
            "company_name": "Ethiopian Airlines",
        },
    ]


def test_health_and_ready():
    assert client.get("/health").status_code == 200
    ready = client.get("/ready")
    assert ready.status_code == 200
    body = ready.json()
    assert body["status"] == "ready"
    assert "model_version" in body
    assert "rollout_mode" in body
    assert "serving_backend" in body


def test_score_response_schema():
    response = client.post(
        "/v1/score",
        json={
            "cv_text": "airport operations and baggage coordination experience",
            "jobs": _base_jobs(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["scorer_source"] == "baseline_tfidf_cosine_v1"
    assert isinstance(data["ranked_results"], list)
    assert "latency_ms" in data
    assert data.get("serving_backend") == "local"
    assert data.get("model_version") is not None


def test_empty_or_invalid_input_handling():
    empty_cv = client.post(
        "/v1/score",
        json={"cv_text": "   ", "jobs": _base_jobs()},
    )
    assert empty_cv.status_code == 400
    assert "request_id" in empty_cv.json()

    no_jobs = client.post(
        "/v1/score",
        json={"cv_text": "valid", "jobs": []},
    )
    assert no_jobs.status_code == 422
    assert no_jobs.json()["detail"] == "Invalid request payload"


def test_non_ethiopian_jobs_excluded():
    payload = {
        "cv_text": "passenger customer care support",
        "jobs": _base_jobs()
        + [
            {
                "job_id": "non-et-1",
                "title": "Cabin Crew",
                "description": "Passenger support",
                "company_name": "Another Airline",
            }
        ],
    }
    response = client.post("/v1/score", json=payload)

    assert response.status_code == 200
    excluded = response.json()["excluded_jobs"]
    assert any(item["job_id"] == "non-et-1" and item["reason"] == "non-ethiopian" for item in excluded)
