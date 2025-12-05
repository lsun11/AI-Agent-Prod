# Architecture Overview

This document describes the high-level architecture of the **AI Agent Researcher & Document Generator**.

The system consists of three main layers:

1. **Frontend UI** – Chat interface, file management, preview & history
2. **Backend API** – FastAPI app providing streaming chat, downloads, history
3. **Research & Document Engine** – Topic workflows, web scraping, LLM layout + multi-format exporters

---

## 1. Frontend UI

The frontend is a lightweight web client that talks to the backend via:

- `GET /chat_stream` (SSE)
- `GET /download/{filename}`
- `GET /history`

### Main Components

- **Chat UI (`ChatUI`)**
  - Renders messages from the SSE stream (`topic`, `log`, `final`)
  - Displays:
    - Topic badge (e.g., “Developer Tools”)
    - Live log messages from the workflow
    - Final formatted reply text
    - Buttons for downloading files (PDF, DOCX, TXT, PPTX)
    - Buttons for previewing files (PDF/TXT/PPTX)
- **File Preview Panel**
  - Hidden by default
  - Shown when a “Preview” button is clicked
  - Renders:
    - **PDF:** via an `<iframe>` pointing to `/download/{filename}`
    - **TXT:** via a white-panel `<pre>` or `<div>` for readability
    - **PPTX/DOCX:** can trigger download or future preview integration
  - Includes a close button that completely hides the panel
- **History Panel**
  - Draggable side panel that shows recent research runs:
    - Query text
    - Timestamp
    - Topic label
    - Quick links to PDFs / DOCXs / PPTXs
  - Uses simple HTML + JS (no heavy framework required)
  - Remains separate from the chat logic to keep `chat-ui.ts` focused

The frontend is intentionally minimal and framework-agnostic so it can be embedded in any existing web app.

---

## 2. Backend API (FastAPI)

The Python backend is built using **FastAPI** and **Starlette**, and exposes three main concerns:

1. **Chat & Research Orchestration**
2. **File Downloads**
3. **History / Metadata**

### 2.1 App Factory

`src/api/app.py` defines a `create_app()` function that:

- Configures CORS, middleware, etc.
- Mounts all routers:
  - `chat.py` – `/chat_stream`
  - `downloads.py` – `/download/{filename}`
  - `history.py` – `/history`, `/history/{id}`

### 2.2 Chat Route (`chat.py`)

The core entrypoint is:

```python
@router.get("/chat_stream")
async def chat_stream(message: str, model: Optional[str] = Query(None), temperature: Optional[str] = Query(None)):
    ...
```

Flow:

1. Read query + model + temperature from URL
2. Detect language (Chinese / non-Chinese)
3. Classify topic via `classify_topic_with_llm`
4. Fetch appropriate workflow instance from `TOPIC_WORKFLOWS`
5. Set up a queue for streaming logs + final payloads
6. Start a background thread that:
   - Configures the workflow LLM
   - Runs `workflow.run(internal_query)`
   - Invokes the layout LLM (`generate_document_and_slides`)
   - Calls `generate_all_files_for_layout` (PDF / DOCX / TXT / PPTX)
   - Pushes a `final` SSE event
   - Records a history entry
7. Stream SSE messages from the queue to the client

Events:

- `"topic"` – Contains `topic_key`, `topic_label`, `topic_domain`
- `"log"` – User-friendly text like “Searching tools”, “Analyzing pricing”, etc.
- `"final"` – Includes:
  - `reply` – final text response
  - `download_pdf_url`, `download_docx_url`, `download_txt_url`, `slides_download_url`
  - `topic_used` – label for UI
  - `companies_visual` – simplified list of tools (name, URL, logo, colors)

### 2.3 Downloads Route (`downloads.py`)

Handles:

```python
@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = SAVED_DOCS_DIR / filename
    return FileResponse(file_path, media_type=..., headers={"Content-Disposition": 'inline; filename="..."'})
```

Key points:

- Uses `inline` disposition to enable browser preview
- Properly encodes filenames with non-ASCII characters
- Validates file existence and returns 404 if missing

### 2.4 History Route (`history.py`)

Provides endpoints like:

- `GET /history` – list of recent runs
- `GET /history/{id}` – optional detailed info per run

Implementation details:

- Uses a simple store (JSON file, SQLite, or in-memory) keyed by an ID
- Each entry stores:
  - Query
  - Timestamp
  - Topic
  - File paths / URLs

The history feature is kept independent of the research workflows to keep responsibilities clean.

---

## 3. Research & Document Engine

At the heart of the system is the combination of:

1. **Topic Workflows** (LangGraph, LangChain)
2. **Firecrawl-based collection**
3. **LLM layout generator (`generate_document_and_slides`)**
4. **Multi-format exporters (`generate_all_files_for_layout`)**

### 3.1 Topic Workflows

See `src/topics/`:

- `root_workflow.py` – Common utilities:
  - Shared `self.llm`
  - Logging with callbacks
  - `_get_web_results` and `_collect_content_from_web_results`
- `base_workflow.py` – `BaseCSWorkflow` for CS / tooling topics:
  - Graph nodes: `extract_tools`, `research`, `analyze`
  - Uses `FirecrawlService` to search & scrape
  - Runs analysis with structured Pydantic models
  - Produces a final `state` with:
    - `companies` → list of analyzed tools
    - `analysis` → narrative summary

Each specific topic (e.g., `developer_tools`) supplies:

- Topic-specific `state_model`
- Topic-specific `company_model` (fields relevant to the domain)
- Topic-specific `analysis_model`
- A `Prompts` class with system/user prompts tailored to the topic

### 3.2 Firecrawl Service

`FirecrawlService` is used to:

- Search the web for comparison articles and tool mentions
- Scrape official websites for richer markdown content
- Retrieve branding info (colors, images)

The workflows rely on `FirecrawlService` but are not tightly coupled, thanks to helper methods in `RootWorkflow`.

### 3.3 Layout Generator (`layout_llm.py`)

`generate_document_and_slides(...)` takes:

- `query` – original user question
- `raw_text` – final narrative analysis from the workflow
- Optional `sources` and `entities` for:
  - Citation insertion
  - Comparison table generation

It instructs a small, deterministic LLM (`gpt-4.1-nano`) to:

- Produce `title` – overall report title
- Produce `report_markdown` – fully structured Markdown:
  - `##` / `###` headings only (no `#` top-level heading)
  - Optional section emojis
  - Comparison tables where applicable
  - Inline `[1]`, `[2]` citations and a trailing `## Sources` section
- Produce `slides` – list of `{title, bullets[]}`

This step is **purely layout** and does not introduce new factual content.

### 3.4 File Generation (`generate_files.py`)

`generate_all_files_for_layout`:

1. Constructs timestamped base filenames from the query
2. Writes:
   - `.txt` via `write_txt`
   - `.pdf` via `write_pdf`
   - `.docx` via `write_docx`
   - `.pptx` via `write_slides`
3. Returns a dict of paths that `chat_stream` turns into download URLs

The whole pipeline from **query → web research → analysis → layout → files** is linear and traceable.

---

## 4. Extensibility

### Adding a New Topic

To add a new research topic:

1. Create a new folder under `src/topics/your_topic/`
2. Define:
   - A Pydantic state model
   - A Pydantic company info model
   - A Pydantic analysis model
   - A `Prompts` class (extending `BaseCSResearchPrompts` if applicable)
3. Create a workflow class `YourTopicWorkflow(BaseCSWorkflow[...])`:
   - Set `topic_label` and `article_query_template`
   - Customize prompts if needed
4. Register it in `TOPIC_WORKFLOWS` with a key (e.g. `"your_topic"`)

The rest (layout, export, preview, history) will work automatically.

### Swapping LLMs

`RootWorkflow.set_llm` supports:

- OpenAI (`gpt-*`)
- DeepSeek (`deepseek-*`)
- Anthropic (`claude-*`)
- Google Gemini (`google-*`)

You can add more backends or routing logic here without touching the rest of the system.

---

## 5. Summary

The system is built as a **pipeline of clear stages**:

> **SSE Chat → Topic Workflow → Web Research → LLM Analysis → Layout LLM → Multi-Format Export → In-App Preview + History**

Each stage is modular, testable, and replaceable, making this repository a strong foundation for building a **serious, production-grade AI research assistant**.
