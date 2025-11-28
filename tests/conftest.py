# tests/conftest.py
import os

# Set fake keys as soon as pytest loads this file
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("FIRECRAWL_API_KEY", "test-key")

# (Optional) still keep a fixture if you want
import pytest

@pytest.fixture(autouse=True)
def fake_env_keys(monkeypatch):
    # This ensures they stay set even if some test mutates them
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
