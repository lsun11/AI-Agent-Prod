# src/api/routes/chat.py
import os
import json
import re
import threading
import unicodedata
from datetime import datetime
from typing import Optional
from queue import Queue
import uuid
from ...history.store import HistoryEntry, add_history_entry
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from ...saving import format_result_text, generate_document_and_slides, LanguageCode, generate_all_files_for_layout
from ..deps import TOPIC_WORKFLOWS, classify_topic_with_llm
from ..translate import is_chinese, translate_text

router = APIRouter()
SAVED_DOCS_DIR = "saved_docs"


@router.get("/chat_stream")
async def chat_stream(
        message: str,
        model: Optional[str] = Query(None),
        temperature: Optional[str] = Query(None),
        mode: Optional[str] = Query("fast"),
):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    The `message` comes from the query string, e.g. /chat_stream?message=...
    """
    user_query = message

    # --- language detection ---
    user_is_chinese = is_chinese(user_query)
    # Use an English query internally if Chinese
    internal_query = (
        translate_text(user_query, "English") if user_is_chinese else user_query
    )

    selected_model = model or "gpt-4.1-mini"
    selected_temperature = float(temperature) if temperature is not None else 0.1

    speed_mode = (mode or "fast").lower()
    fast_mode = speed_mode != "deep"
    print("User selected model:", selected_model)
    print("User selected temperature:", selected_temperature)
    print("Fast mode:", fast_mode)

    # 1) classify topic
    topic_key, topic_label, topic_domain = classify_topic_with_llm(internal_query)

    # 2) get the *instance* from TOPIC_WORKFLOWS
    workflow = TOPIC_WORKFLOWS.get(topic_key)
    if workflow is None:
        workflow = TOPIC_WORKFLOWS.get("developer_tools")
        topic_key = "developer_tools"
        topic_label = "Developer Tools"
        topic_domain = "tools"

    # If Chinese, we may also translate the topic label for UI
    topic_label_display = (
        translate_text(topic_label, "Chinese") if user_is_chinese else topic_label
    )
    q: Queue[str] = Queue()

    def log_callback(msg: str) -> None:
        out_msg = msg
        if user_is_chinese:
            # You can prefix if you want, but simplest: just translate the log
            out_msg = translate_text(msg, "Chinese")
        payload = {"type": "log", "message": out_msg}
        q.put(json.dumps(payload))

    # Initial log messages (model + temp)
    q.put(json.dumps({"type": "log", "message": f"📌 Model selected: {selected_model}"}))
    q.put(json.dumps({"type": "log", "message": f"🎛️ Temperature set to: {selected_temperature}"}))
    # 👇 NEW: log speed mode
    if fast_mode:
        speed_msg = "⚡ Fast mode: quicker answer with lighter analysis."
    else:
        speed_msg = "🧠 Deep Thinking: multi-pass research and knowledge extraction enabled."
    if user_is_chinese:
        speed_msg = translate_text(speed_msg, "Chinese")
    q.put(json.dumps({"type": "log", "message": speed_msg}))

    def format_workflow_result(result):
        reply_text_en = format_result_text(internal_query, result)

        # translate final reply back to Chinese if needed
        reply_text = (
            translate_text(reply_text_en, "Chinese")
            if user_is_chinese
            else reply_text_en
        )
        #print(reply_text)

        # Collect resources for citations
        raw_resources = []
        for res in getattr(result, "resources", []) or []:
            raw_resources.append(
                {
                    "title": getattr(res, "title", None),
                    "url": getattr(res, "url", None),
                }
            )

        # 2) Let the LLM turn reply_text into a professional layout
        language: LanguageCode = "Chn" if user_is_chinese else "Eng"
        entities = [
            {"name": c.name, "website": c.website}
            for c in result.companies or []
        ] if hasattr(result, "companies") else []

        layout = generate_document_and_slides(
            query=user_query,
            raw_text=reply_text,
            language=language,
            sources=raw_resources,
            entities=entities,
        )

        # 3) Use the layout to generate txt / pdf / docx / slides
        #    Build base filename from the user query + timestamp (old behavior)
        raw_summary = user_query.strip() or "research"

        # Normalize unicode so Chinese characters are preserved
        normalized = unicodedata.normalize("NFKC", raw_summary)

        # Replace any invalid filename characters with "_"
        safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", normalized)

        # Trim and collapse spaces, limit length
        safe = "_".join(safe.split())[:80]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{safe}_{timestamp}"

        paths = generate_all_files_for_layout(
            layout=layout,
            base_folder="saved_docs",
            base_filename=base_filename,
        )

        pdf_path = paths["pdf"]
        docx_path = paths["docx"]
        txt_path = paths["txt"]
        slides_path = paths["pptx"]

        pdf_filename = os.path.basename(pdf_path)
        docx_filename = os.path.basename(docx_path)
        txt_filename = os.path.basename(txt_path)
        slides_filename = os.path.basename(slides_path)

        download_pdf_url = f"/download/{pdf_filename}"
        download_docx_url = f"/download/{docx_filename}"
        download_txt_url = f"/download/{txt_filename}"
        slides_download_url = f"/download/{slides_filename}"

        companies_visual = []
        for company in getattr(result, "companies", []) or []:
            companies_visual.append(
                {
                    "name": getattr(company, "name", None),
                    "website": getattr(company, "website", None),
                    "logo_url": getattr(company, "logo_url", None),
                    "primary_color": getattr(company, "primary_color", None),
                    "brand_colors": getattr(company, "brand_colors", None),
                }
            )

        resources_visual = []
        for res in getattr(result, "resources", []) or []:
            resources_visual.append(
                {
                    "title": getattr(res, "title", None),
                    "url": getattr(res, "url", None),
                    "logo_url": getattr(res, "logo_url", None),
                    "primary_color": getattr(res, "primary_color", None),
                    "brand_colors": getattr(res, "brand_colors", None),
                }
            )

        # ----------------- Save to history -----------------
        entry_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"

        history_entry = HistoryEntry(
            id=entry_id,
            query=user_query,
            topic=topic_label_display,
            language="Chn" if user_is_chinese else "Eng",
            created_at=created_at,
            download_pdf_url=download_pdf_url,
            download_docx_url=download_docx_url,
            download_txt_url=download_txt_url,
            slides_download_url=slides_download_url,
        )
        add_history_entry(history_entry)

        final_payload = {
            "type": "final",
            "reply": reply_text,  # human-readable answer for the chat bubble
            "download_pdf_url": download_pdf_url,
            "download_docx_url": download_docx_url,
            "download_txt_url": download_txt_url,
            "slides_download_url": slides_download_url,
            "topic_used": topic_label_display,
            "companies_visual": companies_visual,
            # you can also add "resources_visual" if you want it on the frontend
        }
        return final_payload

    def run_workflow():
        # set callback just for this run
        workflow.set_llm(selected_model, selected_temperature)
        workflow.set_log_callback(log_callback)
        try:
            # 👇 TRY to call with fast_mode; fall back to old signature if needed
            try:
                result = workflow.run(internal_query, fast_mode=fast_mode)
            except TypeError:
                # Old workflows that don't know about fast_mode
                result = workflow.run(internal_query)
            final_payload = format_workflow_result(result)
            q.put(json.dumps(final_payload))
        finally:
            workflow.set_log_callback(None)
            q.put("__DONE__")


    # Run workflow in background thread so we can stream logs
    threading.Thread(target=run_workflow, daemon=True).start()

    def event_generator():
        # First send topic info so UI can update title immediately
        topic_payload = {
            "type": "topic",
            "topic_key": topic_key,
            "topic_label": topic_label_display,
            "topic_domain": topic_domain,
        }
        yield f"data: {json.dumps(topic_payload)}\n\n"

        while True:
            item = q.get()
            if item == "__DONE__":
                break
            yield f"data: {item}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
