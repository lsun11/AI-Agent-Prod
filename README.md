# AI Agent Researcher & Document Generator

## Overview
This repository contains an advanced AI-powered research assistant that transforms raw queries into structured, professional multi-format documents. The system integrates:
- **Multi-agent LLM workflows**
- **Automated research & web scraping**
- **LLM-based document layout generation**
- **PDF / DOCX / TXT / PPTX exporters**
- **Streaming chat interface with real-time logs**
- **Chinese/English translation support**
- **Topic classifier & workflow router**
- **FastAPI backend with SSE streaming**

It is designed for developers, researchers, analysts, and engineers who need **instant high‑quality technical research reports**, formatted in a way that looks polished and ready for presentation.

---

## ✨ Key Features

### 🔍 1. Intelligent Topic Classification
Every user query is classified into one of several research domains (e.g. Developer Tools, Cloud Infra, SaaS, Software Engineering).  
The classifier:
- Uses LLM reasoning
- Handles English & Chinese
- Ensures the correct workflow is chosen automatically

---

### 🧠 2. Specialized Research Workflows (LangGraph / LangChain)
Each topic uses a dedicated workflow that can:
- Perform structured analysis
- Extract entities (tools, companies, tech)
- Collect pricing, features, APIs, integrations
- Auto-generate comparisons
- Produce final semantic-rich results

---

### 🌐 3. Firecrawl Web Scraping Integration
When needed, the system performs:
- Website scrapes  
- Metadata extraction  
- Content extraction  
- Document summarization  

This information is merged into the final analysis.

---

### 📝 4. LLM-Based Document Layout Generator
After gathering the research output, the system uses a layout LLM to generate:
- **A clean, professional Markdown report**
- **A 4–8 slide outline**  
- **Section reorganization for clarity**
- **Automatic heading, bullets, emphasis, hierarchy**

This guarantees:
- Beautiful output  
- Consistent structure  
- Zero hallucination (no invented facts)  

---

### 📄 5. Multi-format Export Engine (PDF / DOCX / TXT / PPTX)

#### ✅ TXT Export
Simple UTF‑8 dump of the Markdown.

#### ✅ DOCX Export
Using python‑docx:
- Correct fonts for CJK and Latin
- Proper heading levels
- Clean layout

#### ✅ PDF Export (ReportLab)
Custom PDF engine:
- Modern color palette
- Title + subtitle block
- Heading styles (H1, H2, H3)
- CJK-safe fonts (Noto / Source Han)
- Emoji font support
- Watermarking
- Professional margins, spacing, typography

#### ✅ PPTX Export (python-pptx)
Slide generator:
- Title slide
- Bullet slides
- Each slide uses outline from LLM
- Clean PowerPoint-compatible typography

---

### 🌏 6. Full Chinese/English Support
The system detects Chinese automatically and:
- Translates user queries
- Translates LLM output back
- Ensures the final PDF/DOCX/PPTX use proper CJK fonts
- Handles mixed-language content perfectly

---

### 🚀 7. Streaming Chat API (FastAPI + SSE)
The `/chat_stream` endpoint:
- Streams `topic`, `log`, and `final` messages
- Shows incremental reasoning
- Supports real-time frontend rendering
- Ensures responsive UX even for long research tasks

---

### 🧪 8. Comprehensive Test Suite (pytest)
Includes tests for:
- SSE interactions
- Topic classification
- Chinese translation logic
- Workflow routing
- File generation mocking
- Chat interactions

---

## 📂 Project Structure

```
src/
  api/
    routes/
      chat.py             # Main chat + streaming endpoint
  saving/
    layout_llm.py         # LLM layout generator
    pdf_builder.py        # PDF export
    docx_builder.py       # DOCX export
    generate_files.py     # Multi-format file pipeline
    markdown.py           # Markdown inline renderer
    fonts.py              # Emoji/CJK font registration
  topics/
    base_workflow.py
    developer_tools/
    cloud_infra/
    software_eng/
tests/
  test_chat.py
  test_app.py
  ...
```

---

## 🧰 Requirements
- Python ≥ 3.12  
- uv or pip  
- ReportLab  
- python-pptx  
- python-docx  
- Firecrawl  
- LangChain + LangGraph  
- FastAPI + Uvicorn  

---

## 🚀 Running the App

### 1. Install dependencies
```
uv sync
```

### 2. Start the server
```
uv run server.py
```

### 3. Open the frontend (your web client)
Chat UI uses:
- Real-time SSE
- Topic badges
- Download links for all file formats

---

## 📦 API Endpoints

### `GET /chat_stream`
SSE streaming endpoint returning:
- `"topic"` — workflow chosen
- `"log"` — incremental logs
- `"final"` — final report + file URLs

### `GET /download/{path}`
Secure file downloader used by UI.

---

## 🗂 Output Example

Each query generates:

| Format | Output |
|--------|---------|
| `.pdf` | Beautiful formatted professional PDF |
| `.docx` | Word-friendly editable report |
| `.txt` | Raw markdown plaintext |
| `.pptx` | Clean slide deck |

---

## 🚧 Roadmap
- Add more workflows: databases, ML tools, monitoring tools
- Add embeddings memory for cross-session context
- Add proper UI for document preview
- Add citations & sources extraction
- Add Firecrawl deep crawling mode
- Add structured YAML output mode

---

## ❤️ Contributing
PRs are welcome!  
The project is modular and easy to extend with new workflows.

---

## 📜 License
MIT License
