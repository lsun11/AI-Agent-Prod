# AI Agent Researcher & Document Generator

## Overview

This repository contains an advanced AI-powered research assistant that turns raw user queries into **structured, presentation-ready research reports** in multiple formats:

- 🧠 **Multi-agent LLM workflows** (per topic)
- 🌐 **Automated research & web scraping (Firecrawl)**
- 🎨 **LLM-based document layout + comparison tables + citations**
- 📄 **Multi-format export: PDF / DOCX / TXT / PPTX**
- 💬 **Streaming chat interface (FastAPI + SSE)**
- 🔁 **Smart history of past reports**
- 👀 **In-app preview for generated files (PDF / TXT / PPTX)**
- 🌏 **Chinese / English support with CJK-safe fonts**

It is designed for developers, researchers, analysts, and engineers who want a workflow that is **better than traditional search + copy/paste + manual formatting**.

---

## ✨ Key Features

### 🔍 1. Intelligent Topic Classification

Every query is first classified into a topic domain, for example:

- Developer Tools / IDEs
- Cloud Infrastructure & Databases
- SaaS / Productivity Tools
- Software Engineering & Architecture

The classifier:

- Uses LLM reasoning to infer intent
- Works with both English and Chinese queries
- Routes the request to the correct topic workflow automatically

This means the same chat endpoint can handle very different research tasks with the right specialized logic behind the scenes.

---

### 🧠 2. Specialized Research Workflows (LangGraph + LangChain)

Each topic has a dedicated workflow built on top of `RootWorkflow` and `BaseCSWorkflow`, using **LangGraph** and **LangChain**:

- Performs multi-step research (search → scrape → analyze)
- Extracts entities (tools, products, cloud services, etc.)
- Pulls structured fields like:
  - Pricing model and details
  - API availability
  - Tech stack / language support
  - Integrations & ecosystem
  - Strengths / limitations
- Produces a final, semantically rich analysis

Under the hood, these workflows:

- Use `FirecrawlService` for web search + scraping
- Extract candidate tools (e.g., IDEs, DBs, cloud services)
- Scrape official websites for markdown + branding (logo, colors)
- Run structured LLM analysis (`with_structured_output`)
- Merge all this into a clean, unified `companies` list and an `analysis` text block

---

### 🌐 3. Firecrawl Web Scraping Integration

Firecrawl is used as the primary “eyes on the web” for the agent:

- Searches for comparison articles and tool descriptions
- Normalizes different response shapes
- Optionally deep-scrapes official websites
- Extracts:
  - Markdown content
  - Titles & descriptions
  - URLs
  - Branding data (colors, icons/logos)

The helper methods `_get_web_results` and `_collect_content_from_web_results` in `RootWorkflow` provide a **consistent, topic-agnostic** interface for downstream analysis.

---

### 🧾 4. LLM-Based Layout & Comparison Engine

After the topic workflow finishes, the app **does not** send raw text directly to PDF. Instead, it uses a dedicated layout LLM via `generate_document_and_slides` (in `layout_llm.py`) to:

1. **Rewrite raw analysis as a clean Markdown report**  
   - Uses only the information from the analysis (no new facts)  
   - Applies section headings (`##`, `###`)  
   - Creates bullet lists and emphasizes important concepts  
   - Adds emojis to make the PDF visually friendly but still professional  

2. **Generate comparison tables**  
   - Detects multiple comparable entities (tools, cloud services, databases, etc.)  
   - Builds GitHub-style Markdown tables where:
     - Rows = attributes (pricing, OSS, language support, etc.)  
     - Columns = tool names  
   - Tables are inserted **before** the recommendations/final analysis section.

3. **Add inline citations and a Sources section**  
   - If web sources are provided (title + URL), the LLM can attach `[1]`, `[2]` style citations.  
   - Adds a final `## Sources` section listing all referenced URLs.

4. **Produce slide outlines** (4–8 slides)  
   - Each slide has a `title` and 3–6 bullet points  
   - Designed to feed into PPTX generation directly

This separation means the layout logic is **model-driven**, easy to extend, and shared across all topics.

---

### 📄 5. Multi-format Export Engine

Located under `src/saving/`, the system exports the layout into four formats:

#### ✅ TXT (`write_txt`)

- Simple UTF‑8 text
- Uses `report_markdown` as-is
- Good for raw text usage or CLI workflows

#### ✅ DOCX (`docx_builder.py`)

- Heading-aware Word document (via `python-docx`)
- Uses correct fonts for:
  - Latin-based text
  - CJK content (Chinese)
- Keeps hierarchy and bullet lists

#### ✅ PDF (`pdf_builder.py`)

A custom **ReportLab**-based renderer with:

- **Title + subtitle** block derived from user query and topic
- Beautiful **color scheme** for headings and body text
- Proper margins and line spacing
- **CJK-safe fonts** (Song / Noto) and a Latin fallback
- **Emoji font** support when needed
- **Inline markdown rendering** (bold, lists, etc.)
- **Tables** rendered as real table layouts, with:
  - Auto-fit column widths
  - Wrapped text in cells
  - Alternating row colors for readability
- A subtle diagonal **watermark**: “Generated by AI Agent Researcher”

#### ✅ PPTX (`write_slides`)

- Uses `python-pptx`
- First slide = title slide
- Remaining slides = bullet slides from the layout LLM
- Bullets are plain text → safe for any theme
- Easy to customize templates later

---

### 🌏 6. Chinese / English Language Support

The app is designed to work well for both English and Chinese users:

- Detects Chinese queries (`is_chinese`)
- Uses translation (`translate_text`) only where needed
- Ensures layout text stays in the intended language
- Uses proper CJK fonts in PDF and DOCX
- Works with mixed-language content

---

### 💬 7. Streaming Chat API (FastAPI + SSE)

The main backend entrypoint is `/chat_stream`, which:

- Accepts query parameters:
  - `message`
  - `model`
  - `temperature`
- Streams back events of types:
  - `"topic"` — which topic/workflow is used
  - `"log"` — step-by-step progress messages
  - `"final"` — final report + all download URLs

This gives the frontend a chat-like, **real‑time experience** instead of a single blocking response.

---

### 📂 8. Smart History (Per-Session, Model-Agnostic)

A lightweight **history panel** keeps track of past runs:

- Stores:
  - Query text
  - Topic label
  - Timestamps
  - File download URLs (PDF / DOCX / TXT / PPTX)
- Accessible via a draggable side panel (history UI)
- Lets users quickly re-open or re-download earlier research runs
- Implemented with a small backend store + simple frontend integration

This makes the tool feel like a **research notebook** rather than a one-shot chatbot.

---

### 👀 9. In‑App File Preview (PDF / TXT / PPTX)

The chat UI includes an optional right-hand side preview panel:

- Clicking “Preview” next to a format shows:
  - **PDF**: embedded in an `<iframe>`
  - **TXT**: rendered in a scrollable white panel
  - **PPTX**: trigger browser’s default download/preview (or a future viewer)
- The preview panel:
  - Is **hidden by default**
  - Appears only when a preview is requested
  - Can be closed with a dedicated “×” button
  - Does not interfere with the main chat scroll

This makes it feel more like an **IDE for research output** than a basic file download list.

---

### 🎯 10. Comparison Tables + Sources = “Better Than Search”

When multiple tools are involved, the system:

- Extracts the tools from the web
- Normalizes each one (pricing, OSS, APIs, features, etc.)
- Generates:
  - A detailed per-tool breakdown
  - A **side-by-side comparison table**
  - A **Sources** section for transparency

This is exactly the kind of work people usually do manually with Google + Excel + copy/paste. Here it’s done **end-to-end in a single query**.

---

## 📂 Project Structure

```text
src/
  api/
    app.py                  # FastAPI app factory
    routes/
      chat.py               # /chat_stream SSE endpoint
      downloads.py          # /download/{filename}
      history.py            # /history endpoints (list / details)
  saving/
    layout_llm.py           # LLM layout & slides generator
    generate_files.py       # Multi-format file pipeline
    pdf_builder.py          # ReportLab PDF renderer
    docx_builder.py         # DOCX builder
    markdown.py             # Markdown → HTML for ReportLab
    fonts.py                # CJK + emoji font registration
  topics/
    root_workflow.py        # Shared glue: LLM, Firecrawl, helpers
    base_workflow.py        # BaseCSWorkflow (tools/infra research)
    developer_tools/        # Topic-specific models/prompts
    cloud_infra/
    software_eng/
frontend/
  index.html
  css/
    styles.css
  js/
    main.ts / main.js       # App entrypoint
    chat-ui.ts / chat-ui.js # Chat logic + SSE handling
    history.ts / history.js # Draggable history panel & storage
tests/
  test_app.py
  test_chat.py
  test_server.py
  test_translate.py
```

---

## 🧰 Requirements

- Python ≥ 3.12  
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- FastAPI + Uvicorn
- LangChain, LangGraph
- Firecrawl SDK
- ReportLab
- python-docx
- python-pptx
- dotenv

Configure your OpenAI and Firecrawl keys via environment variables (`.env`).

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
uv sync
```

or

```bash
pip install -r requirements.txt
```

### 2. Run the Backend

```bash
uv run server.py
```

This launches the FastAPI app (with `/chat_stream`, `/download`, `/history`, etc.).

### 3. Open the Frontend

Serve `frontend/` via any static server (or integrate into your own web app).  
The chat UI will:

- Stream logs in real-time
- Show topic badges
- Reveal download and preview buttons for all file formats
- Allow you to open the history panel and revisit past reports

---

## 📦 API Overview

### `GET /chat_stream`

Server-Sent Events (SSE) endpoint.

Emits JSON messages like:

- `{"type": "topic", "topic_key": "...", "topic_label": "...", ...}`
- `{"type": "log", "message": "..."}`
- `{"type": "final", "reply": "...", "download_pdf_url": "...", ...}`

### `GET /download/{filename}`

Returns the generated file:

- Sets `Content-Disposition: inline` to support browser previews
- Works with PDF/TXT; browsers may trigger download for DOCX/PPTX

### `GET /history`

Returns a list of stored past runs:

- Query text
- Timestamp
- Topic label
- File URLs

### `GET /history/{id}`

(Optional, depending on implementation) Returns details for a single history entry.

---

## 🗂 Output Examples

Each query can generate:

| Format | Purpose |
|--------|---------|
| `.pdf` | Primary “final report” for sharing or printing |
| `.docx` | Editable report for teams that live in Word |
| `.txt` | Raw markdown text for terminals, search, or further processing |
| `.pptx` | Slide deck for presentations / demos |

The combination of **comparison tables + citations + sources + multi-format export** makes this app function like a **research assistant + technical writer + document production pipeline** in one.

---

## 🧭 Roadmap & Future Ideas

Some directions that can make this tool even more powerful:

- 📚 Multi-pass, multi-engine research with deduplication and clustering  
- 🧩 Plugin/MCP integration for more precise tools (GitHub, StackOverflow, docs)  
- 🧠 Long-term memory of user preferences and prior reports  
- 🏗️ More topic packs: observability, MLOps, security tools, data platforms  
- 💼 Export to HTML and Notion/Confluence-friendly formats  
- 🔄 Batch mode: turn a list of queries into a report pack

---

## ❤️ Contributing

PRs, bug reports, and feature suggestions are very welcome.

You can contribute by:

- Adding new topic workflows  
- Improving prompts, layouts or table logic  
- Enhancing frontend UX (preview, theming, filters)  
- Extending tests and CI

---

## 📜 License

MIT License
