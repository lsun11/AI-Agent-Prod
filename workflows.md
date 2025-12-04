# Workflows & Research Pipelines

This document explains how the **topic workflows** in this project operate, from user query to final structured analysis.

At a high level, the workflow for most topics looks like:

> **User Query → Topic Workflow → Web Search & Scrape → Tool/Entity Extraction → Per-Entity Analysis → Final Recommendations → Layout & Export**

---

## 1. Base Abstractions

### 1.1 `RootWorkflow`

Located in `src/topics/root_workflow.py`, `RootWorkflow` provides:

- A primary `self.llm` (configurable)  
- `set_llm(model_name, temperature)` to switch underlying providers (OpenAI, DeepSeek, Claude, Gemini)  
- Logging via `_log`, with an optional callback for streaming logs to the frontend  
- Firecrawl helpers:
  - `_get_web_results(...)`
  - `_collect_content_from_web_results(...)`

It **does not** define domain-specific behavior. Instead, it defines the “bones” on which each topic workflow stands.

### 1.2 `BaseCSWorkflow`

Located in `src/topics/base_workflow.py`, `BaseCSWorkflow` is a generic base for **CS-product research topics** (tools, SaaS, infra, etc.).

It is parameterized by:

- `StateT` – the workflow state (Pydantic model)
- `CompanyT` – per-entity/company model
- `AnalysisT` – structured analysis model (pricing, tech stack, etc.)

Key responsibilities:

- Build a **LangGraph** state machine with nodes:
  - `extract_tools`
  - `research`
  - `analyze`
- Manage a `self.prompts` object (topic-specific prompts)
- Expose a public `run(query: str)` that returns a filled state

---

## 2. State Machine: Nodes & Flow

### 2.1 Node: `extract_tools`

Purpose:

- Search the web for comparison content related to the query
- Extract candidate tools/services/products from the content

Steps:

1. Construct a search query (e.g. `"{query} comparison best alternatives"`)
2. Use `FirecrawlService.search_companies(...)` to get search results
3. Normalize and collect content via `_get_web_results` and `_collect_content_from_web_results`
4. Call the LLM with a **tool extraction** prompt, for example:

   - System prompt: `TOOL_EXTRACTION_SYSTEM`
   - User prompt: `tool_extraction_user(query, all_content)`

5. Parse the LLM response into a list of tool names

Outputs:

- `state.extracted_tools` – a list like `["VS Code", "PyCharm", "Vim", ...]`

### 2.2 Node: `research`

Purpose:

- For each extracted tool, perform a **focused research pass**

Steps:

1. Determine which tool names to use:
   - Use `extracted_tools` if available
   - Otherwise, fall back to titles in search results
2. Use a `ThreadPoolExecutor` to parallelize research for each tool
3. For each tool, call `_research_single_tool(tool_name)`

### 2.3 `_research_single_tool(tool_name)`

This method does the heavy lifting for each entity:

1. Logs “researching: {tool_name}”
2. Builds a search query targeting the official site
3. Uses Firecrawl to search and fetch `web_results`
4. Extracts:
   - URL (website)
   - Brief description (if available)
5. Initializes a `CompanyT` instance:
   - `name`
   - `website`
   - `description`
6. Scrapes the official website via `firecrawl.scrape_company_pages(url)`:
   - Collects `markdown` content
   - Extracts `branding` info (colors, images)
   - Determines `logo_url`, `primary_color`, `brand_colors`
7. If content is available:
   - Calls `_analyze_company_content(company.name, content)`

### 2.4 `_analyze_company_content(company_name, content)`

Uses a **structured LLM call**:

- `structured_llm = self.llm.with_structured_output(self.analysis_model)`
- System prompt: `TOOL_ANALYSIS_SYSTEM`
- User prompt: `tool_analysis_user(company_name, content)`

The LLM fills a Pydantic model `AnalysisT`, which might contain fields like:

- `pricing_model`, `pricing_details`
- `is_open_source`
- `tech_stack`, `language_support`
- `integration_capabilities`
- `api_available`
- `description`

If analysis fails, a safe default object is returned.

### 2.5 `_apply_analysis_to_company(company, analysis)`

After we have `analysis`, this helper:

- Converts it into a dict
- Copies over fields that:
  - Exist on the company model
  - Are not `None`
  - Are not “protected” identifiers like `name` or `website`

This ensures:

- The `CompanyT` object gets enriched with all relevant fields
- Existing non-empty fields are not overwritten with `None`

### 2.6 Node: `analyze`

Purpose:

- Combine all company-level analysis into final recommendations

Steps:

1. Collects all `state.companies`
2. Serializes them (e.g. `company.model_dump_json()`)
3. Calls the LLM with:
   - System prompt: `RECOMMENDATIONS_SYSTEM`
   - User prompt: `recommendations_user(state.query, company_data)`

The LLM returns a narrative text block (in the target language) that provides:

- Overall evaluation
- How each tool compares
- When to choose which
- Trade-offs and caveats

Outputs:

- `state.analysis` – the narrative analysis string
- `state.companies` – list of enriched company objects

### 2.7 `run(query)`

The public API:

```python
def run(self, query: str) -> StateT:
    initial_state = self.state_model(query=query)
    final_state = self.workflow.invoke(initial_state)
    return self.state_model(**final_state)
```

This hides all the intermediate graph details and returns a **final immutable state**.

---

## 3. Integration with Layout & Export

Once a workflow finishes, `chat_stream` receives a result object that contains at least:

- `analysis` (string)
- `companies` (list of company models)

Then the pipeline is:

1. **Layout LLM** (`generate_document_and_slides`):
   - Input: `query`, `raw_text=analysis`, `sources` and `entities` if available
   - Output: `DocumentLayout` with:
     - `title`
     - `report_markdown`
     - `slides[]`
2. **File Generator** (`generate_all_files_for_layout`):
   - Writes `.txt`, `.pdf`, `.docx`, `.pptx`
   - Returns paths

`chat_stream` then packages these paths into URLs and sends them back in the `"final"` SSE message.

---

## 4. Example Topic: Developer Tools / IDEs

The **Developer Tools** topic uses `BaseCSWorkflow` to research things like:

- “Best Python IDEs 2025”
- “VS Code alternatives for remote development”

Internally, it will:

1. Find comparison articles and blog posts
2. Extract tool names such as “Visual Studio Code”, “PyCharm”, “Vim”, “Neovim”
3. For each:
   - Identify official site
   - Scrape pages for features, pricing, languages
   - Extract branding for UI use (logo, colors)
4. Run structured analysis into fields like:
   - `pricing_model`, `is_open_source`, `language_support`
5. Generate text recommendations and a comparison table
6. Turn the whole thing into a report + slides

The exact prompts differ, but the pattern is the same for other topics (Cloud infra, SaaS, software engineering tools).

---

## 5. Extending or Customizing a Workflow

To adjust behavior for a given topic:

- Change the `article_query_template` to bias towards different content:
  - e.g. `"{query} benchmarks"` or `"{query} vs alternatives"`
- Tune the extraction prompt so:
  - It prefers official tools over blogs
  - It extracts fewer or more entities
- Modify the analysis model to include new fields:
  - e.g. “GPU support”, “multi-region replication”, “SOC 2 compliance”
- Enhance the final recommendations prompt to:
  - Emphasize performance, cost, or ecosystem depending on audience

All these changes are encapsulated per topic and do **not** require changes to:

- The chat API
- The layout engine
- The exporters

---

## 6. Summary

Each workflow in this repo is built as a **small, explicit research pipeline**:

1. Find web content relevant to the query  
2. Extract entities (tools/services/products)  
3. Deep-dive each entity through scraping + structured LLM analysis  
4. Generate a global recommendation narrative  
5. Hand off to the layout engine for **polished document production**  

This architecture makes it straightforward to add new topics, new fields, and new research strategies, while reusing the same powerful document and slide generation pipeline.
