# tests/test_chat.py
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient


def make_test_app(monkeypatch) -> FastAPI:
    """
    Build a tiny FastAPI app that only mounts the /chat_stream route,
    with all heavy dependencies mocked out.
    """
    # Import after fixtures so env vars etc. are already patched
    import src.advanced_agent.api.routes.chat as chat

    # --- Dummy workflow that produces one log + one final result ---
    class DummyWorkflow:
        def __init__(self):
            self._log_cb = None

        def set_llm(self, model: str, temperature: float) -> None:
            # we don't care in tests
            self.model = model
            self.temperature = temperature

        def set_log_callback(self, cb):
            self._log_cb = cb

        def run(self, query: str):
            # Simulate a single log message
            if self._log_cb:
                self._log_cb(f"processing: {query}")

            # Minimal result object with an `analysis` attribute
            class Result:
                analysis = "dummy analysis"
                companies: list = []

            return Result()

    # --- Patch dependencies used inside chat_stream() ---

    # Always classify into our dummy topic
    monkeypatch.setattr(
        chat,
        "classify_topic_with_llm",
        lambda q: ("fake_topic", "Fake Topic", "fake_domain"),
        raising=True,
    )

    # Force "not Chinese" path for now
    monkeypatch.setattr(chat, "is_chinese", lambda text: False, raising=True)
    monkeypatch.setattr(
        chat, "translate_text", lambda text, target: text, raising=True
    )

    # Don’t call real LLM or filesystem code when formatting / saving
    monkeypatch.setattr(
        chat,
        "format_result_text",
        lambda query, result: "formatted result text",
        raising=True,
    )

    # --- NEW: mock layout generation + file generation ---

    # This replaces generate_document_and_slides(query, raw_text, language=...)
    def fake_generate_document_and_slides(
            query: str,
            raw_text: str,
            language: str = "Eng",
            sources=None,  # Add this
            entities=None  # Add this
    ):
        class DummyLayout:
            title = query
            report_markdown = raw_text
            slides = []

        return DummyLayout()

    # This replaces generate_all_files_for_layout(layout, base_folder, base_filename)
    # IMPORTANT: keys must match chat.py expectations: "pdf", "docx", "txt", "pptx"
    def fake_generate_all_files_for_layout(layout, base_folder: str, base_filename: str):
        base = f"{base_folder}/{base_filename}"
        return {
            "pdf": f"{base}.pdf",
            "docx": f"{base}.docx",
            "txt": f"{base}.txt",
            "pptx": f"{base}.pptx",
        }

    monkeypatch.setattr(
        chat,
        "generate_document_and_slides",
        fake_generate_document_and_slides,
        raising=True,
    )
    monkeypatch.setattr(
        chat,
        "generate_all_files_for_layout",
        fake_generate_all_files_for_layout,
        raising=True,
    )

    # Replace the global TOPIC_WORKFLOWS dict with a simple one
    chat.TOPIC_WORKFLOWS.clear()
    chat.TOPIC_WORKFLOWS["fake_topic"] = DummyWorkflow()

    # Build a minimal app just for this router
    app = FastAPI()
    app.include_router(chat.router)
    return app


def _collect_sse_events(response) -> list[dict]:
    """
    Helper to parse SSE "data: ..." lines into JSON payloads.
    Stops when a 'final' event is seen.
    """
    events: list[dict] = []
    for line in response.iter_lines():
        if not line:
            continue
        # TestClient yields bytes; decode if needed
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        assert line.startswith("data: ")
        payload = json.loads(line[len("data: ") :])
        events.append(payload)
        if payload.get("type") == "final":
            break
    return events


def test_chat_stream_sends_topic_log_and_final(monkeypatch):
    app = make_test_app(monkeypatch)
    client = TestClient(app)

    with client.stream("GET", "/chat_stream?message=Hello+world") as response:
        # Basic SSE response properties
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        events = _collect_sse_events(response)

    # We expect at least:
    #  - first event: topic
    #  - one or more log events
    #  - one final event
    types = [e["type"] for e in events]
    assert types[0] == "topic"
    assert "log" in types
    assert "final" in types

    # Check topic event payload
    topic_event = events[0]
    assert topic_event["type"] == "topic"
    assert topic_event["topic_key"] == "fake_topic"
    assert topic_event["topic_label"] == "Fake Topic"

    # Check final event payload structure
    final_event = next(e for e in events if e["type"] == "final")
    assert final_event["reply"] == "formatted result text"

    # Multi-format URLs for the frontend hover menu
    assert final_event["download_pdf_url"].startswith("/download/")
    assert final_event["download_pdf_url"].endswith(".pdf")

    assert final_event["download_txt_url"].startswith("/download/")
    assert final_event["download_txt_url"].endswith(".txt")

    # docx is optional in real code, but in this test we *do* provide one:
    assert final_event["download_docx_url"].startswith("/download/")
    assert final_event["download_docx_url"].endswith(".docx")

    # Slides remain the same
    assert final_event["slides_download_url"].startswith("/download/")
    assert final_event["slides_download_url"].endswith(".pptx")

    assert final_event["topic_used"] == "Fake Topic"


# ---- Integration-style test with the real app factory ----

from src.api.app import create_app

client = TestClient(create_app())


def test_chat_stream_handles_chinese_branch(monkeypatch):
    # 1) Force is_chinese() to return True
    def fake_is_chinese(text: str) -> bool:
        return True

    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.is_chinese",
        fake_is_chinese,
        raising=True,
    )

    # 2) Track calls to translate_text()
    calls = {"count": 0}

    def fake_translate(text: str, target_lang: str) -> str:
        calls["count"] += 1
        # Just tag output so we can see it’s been run
        return f"[{target_lang}] {text}"

    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.translate_text",
        fake_translate,
        raising=True,
    )

    # 3) Avoid real workflows / LLMs in this test
    class DummyResult:
        companies = []
        analysis = "dummy"

    class DummyWorkflow:
        def set_llm(self, model, temp):
            pass

        def set_log_callback(self, cb):
            self._cb = cb

        def run(self, query: str):
            # Emit one log line for the stream
            if hasattr(self, "_cb") and self._cb:
                self._cb("dummy log")
            return DummyResult()

    # Patch the workflow + classifier used by chat_stream
    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.TOPIC_WORKFLOWS",
        {"developer_tools": DummyWorkflow()},
        raising=True,
    )

    def fake_classify(query: str):
        return "developer_tools", "Developer Tools", "tools"

    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.classify_topic_with_llm",
        fake_classify,
        raising=True,
    )

    # 4) Avoid real formatting / file generation here as well
    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.format_result_text",
        lambda q, r: "dummy formatted",
        raising=True,
    )

    # Mock the LLM layout + file generation in the Chinese branch too
    def fake_generate_document_and_slides(
            query: str,
            raw_text: str,
            language: str = "Chn",
            sources=None,  # Add this
            entities=None  # Add this
    ):
        class DummyLayout:
            title = query
            report_markdown = raw_text
            slides = []

        return DummyLayout()
    def fake_generate_all_files_for_layout(layout, base_folder: str, base_filename: str):
        base = f"{base_folder}/{base_filename}"
        return {
            "pdf": f"{base}.pdf",
            "docx": f"{base}.docx",
            "txt": f"{base}.txt",
            "pptx": f"{base}.pptx",
        }

    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.generate_document_and_slides",
        fake_generate_document_and_slides,
        raising=True,
    )
    monkeypatch.setattr(
        "src.advanced_agent.api.routes.chat.generate_all_files_for_layout",
        fake_generate_all_files_for_layout,
        raising=True,
    )

    # 5) Call the endpoint as an SSE stream
    params = {
        "message": "测试中文",
        "model": "gpt-4.1-nano",
        "temperature": "0.1",
    }

    # Use client.stream instead of client.get(stream=...)
    with client.stream("GET", "/chat_stream", params=params) as resp:
        assert resp.status_code == 200

        # Consume the stream into a single text blob
        body = "".join(chunk for chunk in resp.iter_text())

    # We should have at least one translated log or reply
    assert calls["count"] >= 1
    # And the payload should mention the topic and logs in some form
    assert '"type": "topic"' in body
    assert '"type": "log"' in body
    assert '"type": "final"' in body
