
# AI Agent Researcher & Document Generator

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**Multi-Source AI Research Pipeline • Structured Knowledge Extraction • PDF/PPTX/DOCX Output**

---

## 🔥 New: Dual Research Modes (Fast vs Deep Thinking)

This project now supports **two execution modes** so users can explicitly trade off **speed vs depth** at runtime.

### 🚀 Fast Mode (Default)
Optimized for **speed and responsiveness**.

* Single-pass research
* Limited web sources
* No global knowledge synthesis
* Focused summaries & comparison tables
* Ideal for quick decisions and exploratory questions

Typical latency: **5–20 seconds**

### 🧠 Deep Thinking Mode
Designed for **comprehensive analysis** and **high-confidence research**.

* Multi-pass Firecrawl search (query variants)
* Deep scraping of official docs
* Tool / entity extraction across sources
* Knowledge graph construction (entities, risks, timelines)
* Consolidated comparison tables
* Enforced **superset guarantee**:
  > Deep mode always includes everything Fast mode produces — plus more

Typical latency: **45–180 seconds**

### ✅ Superset Guarantee
Deep Thinking mode explicitly **re-runs and merges** the Fast pipeline internally to guarantee:
* No loss of tool lists
* No missing comparison tables
* No regression in recommendations

You always get **Fast Results + Deep Insights**.

---

## 🎚️ UI Control

A **“Deep Thinking” toggle button** is placed next to **Send** in the chat UI:

* **Off (default)** → Fast mode
* **On** → Deep Thinking workflow

The toggle is passed end-to-end:
Frontend → API → RootWorkflow → Topic Workflow

---

## 🔩 Architecture Updates

### RootWorkflow Enhancements
* Unified `fast_mode` flag propagated through all workflows
* Conditional execution of:
  * multi-pass search
  * knowledge extraction
  * deep analysis steps
* Fast-mode short‑circuiting logic for low-latency paths

### Topic Workflow Guarantees
All topic workflows (Developer Tools, Software Engineering, Career):

* Always generate **baseline tool listings**
* Always build **comparison tables**
* Deep mode augments with:
  * knowledge objects
  * risk modeling
  * entity relationships
  * multi-source synthesis

---

## 🧠 Knowledge Extraction Layer
Deep mode activates a shared global extractor that produces:

* **Entities** – tools, platforms, services
* **Relationships** – integrates_with, competes_with
* **Risks** – business / technical / security
* **Timelines** – releases & roadmap signals

This enables advanced queries like:

> “Show only open‑source tools with low vendor lock‑in risk.”

---

## 📦 Outputs

Both Fast and Deep modes support:
* Chat responses
* Comparison tables
* PDF / DOCX / PPTX exports
* Chinese & English rendering (CJK-safe)

Deep mode adds:
* Rich citations
* Structured reasoning
* Cross-article consolidation

---

## Installation

```bash
uv sync
uv run server.py
