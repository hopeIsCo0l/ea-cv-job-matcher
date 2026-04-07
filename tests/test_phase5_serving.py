from src.config.serving import effective_remote_url, load_serving_config


def test_effective_remote_production_requires_backend_remote(monkeypatch):
    monkeypatch.setenv("SERVING_BACKEND", "local")
    monkeypatch.setenv("ROLLOUT_MODE", "production")
    monkeypatch.setenv("REMOTE_SCORER_URL", "http://example.com")
    cfg = load_serving_config()
    assert effective_remote_url(cfg, "req-1") is None

    monkeypatch.setenv("SERVING_BACKEND", "remote")
    cfg = load_serving_config()
    assert effective_remote_url(cfg, "req-1") == "http://example.com"


def test_canary_routes_without_serving_backend_remote(monkeypatch):
    monkeypatch.setenv("SERVING_BACKEND", "local")
    monkeypatch.setenv("ROLLOUT_MODE", "canary")
    monkeypatch.setenv("CANARY_PERCENT", "100")
    monkeypatch.setenv("REMOTE_SCORER_URL", "http://remote.test")
    cfg = load_serving_config()
    assert effective_remote_url(cfg, "any-request-id") == "http://remote.test"


def test_shadow_never_remote(monkeypatch):
    monkeypatch.setenv("SERVING_BACKEND", "remote")
    monkeypatch.setenv("ROLLOUT_MODE", "shadow")
    monkeypatch.setenv("REMOTE_SCORER_URL", "http://example.com")
    cfg = load_serving_config()
    assert effective_remote_url(cfg, "req-1") is None
