# tests/test_server.py
import sys
import importlib


def test_load_dotenv_called(monkeypatch):
    """
    Ensure that load_dotenv() is executed when server.py is imported.
    """

    called = {"loaded": False}

    def fake_load():
        called["loaded"] = True
    monkeypatch.setattr("dotenv.load_dotenv", fake_load)

    if "server" in sys.modules:
        del sys.modules["server"]
    importlib.import_module("server")

    assert called["loaded"] is True


def test_create_app_importable():
    """
    Just ensure the FastAPI app can be instantiated from server.py.
    """
    server = importlib.import_module("server")
    assert hasattr(server, "app")
