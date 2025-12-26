# tests/test_app.py
from fastapi.testclient import TestClient
from src.api.app import create_app


def test_create_app_basic():
    """App should initialize properly."""
    app = create_app()
    client = TestClient(app)
    assert client is not None


from starlette.responses import Response


def test_root_serves_index(monkeypatch):
    captured = {}

    class FakeFileResponse(Response):
        def __init__(self, path: str):
            # create an empty valid HTTP response
            super().__init__(content=b"", media_type="text/html")
            captured["path"] = str(path)

    monkeypatch.setattr("src.api.app.FileResponse", FakeFileResponse)

    from src.api.app import create_app
    from fastapi.testclient import TestClient

    app = create_app()
    client = TestClient(app)

    resp = client.get("/")
    assert resp.status_code == 200
    assert captured["path"].endswith("index.html")



def test_static_mounts():
    """
    Verify the two static directories are mounted.
    """
    app = create_app()
    mounted = list(app.routes)

    static_routes = [r for r in mounted if getattr(r, "name", None) in ["static", "static_build"]]
    assert len(static_routes) == 2
