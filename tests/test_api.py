from fastapi.testclient import TestClient

from api.index import RENDERERS, app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_card_headers_and_svg():
    response = client.get("/api/card?username=octocat&theme=cyberpunk")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "stale-while-revalidate=86400" in response.headers["cache-control"]
    assert response.text.startswith("<svg")


def test_rejects_invalid_username():
    response = client.get("/api/card?username=bad_user")
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_query_validation():
    for url in (
        "/api/card?username=octocat&border_radius=99",
        "/api/card?username=octocat&theme=unknown",
        "/api/badge?username=octocat&bg_color=nope",
    ):
        response = client.get(url)
        assert response.status_code == 422
        assert response.headers["content-type"].startswith("image/svg+xml")


def test_unhandled_card_error_is_svg(monkeypatch):
    class BrokenRenderer:
        def render(self, *_):
            raise RuntimeError("boom")

    monkeypatch.setitem(RENDERERS, "3d-card", BrokenRenderer())
    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/api/card?username=octocat")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "Internal server error" in response.text
