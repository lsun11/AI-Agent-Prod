# AI Agent Researcher & Document Generator

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**Multi-Source AI Research Pipeline • Structured Knowledge Extraction • PDF/PPTX/DOCX Output**

## Overview

This repository contains an advanced AI-powered research assistant designed to transform raw user queries into structured, presentation-ready research reports. By automating multi-source web research, content comparison, and document assembly, the agent produces comprehensive reports in seconds that typically require hours of manual effort.

**Key Capabilities:**
* **Intelligent Topic Classification:** Automatically detects domain context.
* **Multi-Source Web Research:** Utilizes multi-pass Firecrawl search and deep scraping.
* **Knowledge Extraction:** structured parsing of entities, relationships, risks, and timelines.
* **LangGraph Architecture:** Modular, topic-specific workflows.
* **Layout Engine:** LLM-based formatting for Markdown, tables, and slides.
* **Multi-Format Export:** PDF, DOCX, PPTX, and TXT.
* **Global Support:** Full English and Chinese support with CJK-safe rendering.

---

## Core Features & Architecture Updates

### 1. Multi-Source, Multi-Pass Web Research
The agent employs a robust research strategy to ensure data accuracy:
* **Multiple Search Passes:** Iterative querying via Firecrawl.
* **Automatic Deduplication:** Cleans and merges redundant sources.
* **Deep Scraping:** Optional crawling of official product documentation.
* **Smart Content Merging:** Reduces hallucination by cross-referencing sources.

### 2. Shared RootWorkflow & Topic Workflows
The architecture separates core utilities from domain logic for better extensibility:
* **RootWorkflow:** Handles generic tasks including Firecrawl utilities, logging, normalization, and the global knowledge extraction layer.
* **TopicWorkflows:** Inherit from Root to handle specific resource summarization and recommendation logic.

### 3. Global Knowledge Extraction Layer
A shared component (`RootPrompts` + `RootWorkflow`) parses unstructured text into a structured `state.knowledge` object. This allows for:
* **Entity Extraction:** Tools, APIs, companies, cloud services.
* **Relationship Mapping:** `integrates_with`, `depends_on`, `competes_with`.
* **Risk Analysis:** Classification of business, technical, and security risks.
* **Timeline Generation:** Tracking release history and roadmap events.

### 4. Advanced Document Generation
The LLM layout engine handles complex formatting requirements:
* Automatic generation of comparison tables.
* Creation of multi-slide presentation outlines.
* Rendering of complex Markdown (bolding, lists, headers).
* Brand-aware styling (colors and logos) with CJK-safe fonts.

---

## Supported Topics

The agent is currently optimized for the following domains:

### 1. Developer Tools & Ecosystem
* **Scope:** Languages, SDKs, IDEs (VS Code, Cursor, Windsurf), Debuggers, Profilers.
* **Tooling:** CI/CD tools, DevOps platforms, Version Control, Code Quality/Static Analysis.

### 2. Software Engineering & Architecture
* **Design:** Microservices vs Monolith, System Design patterns, API Design.
* **Operations:** Observability stacks, CI/CD pipelines, Scaling & Reliability strategies.
* **Quality:** Testing strategies (Unit/Integration/Contract/E2E), Security engineering.

### 3. Tech Career, Growth & Strategy
* **Development:** Skill roadmaps, Role comparisons (SWE vs DevOps vs MLE).
* **Market:** Salary trends, Resume feedback, Interview prep.
* **Strategy:** Career transitions, Promotion guidance, Long-term learning plans.

---

## Example Queries by Domain

Below is a comprehensive list of queries the agent can handle, organized by category.

### Developer Tools (20+ Subtopics)

**IDEs & Code Editors**
> "Which Python IDE is best for beginners?"
> "VS Code vs Cursor vs Windsurf — difference in collaboration features?"
> "Which editors run fully offline?"

**AI Coding Assistants**
> "Compare GitHub Copilot, Cursor, Windsurf on reliability."
> "Which AI editor understands large monorepos best?"

**Build Tools & Package Managers**
> "Maven vs Gradle — which is better for large Java projects?"
> "pip vs poetry vs uv — performance & environment isolation?"

**Debugging, Profiling & Testing**
> "Which profilers work best with async Python?"
> "pytest vs unittest — which scales better?"

**CI/CD & DevOps**
> "Compare GitHub Actions, CircleCI, Jenkins, and GitLab CI for Docker deployments."
> "Which CI tool is fastest for PR workflows?"
> "Best tools for Kubernetes cluster GitOps?"
> "Which IaC tools compete with Terraform?"

**Documentation & Version Control**
> "mkdocs vs docusaurus vs Sphinx — pros & cons?"
> "GitFlow vs Trunk-based development — company-size implications?"

### Software Engineering (20+ Subtopics)

**Architecture & API Design**
> "Microservices vs monolith — long-term cost analysis."
> "Event-driven architecture — main risks?"
> "REST vs GraphQL vs gRPC — best fit for mobile apps?"
> "How to design backward-compatible APIs?"

**Testing & Deployment**
> "What balance of unit vs integration tests is ideal for microservices?"
> "Contract testing — when to adopt it?"
> "Zero-downtime deployment strategies?"
> "Best practices for staging → production workflow."

**Observability & Reliability**
> "Prometheus vs Datadog vs OpenTelemetry — differences?"
> "How to design tracing for async systems?"
> "SLOs vs SLIs vs SLAs — practical examples?"
> "How to implement circuit breakers effectively?"

**Performance & Databases**
> "Bottlenecks in Python web frameworks?"
> "Caching layers vs DB sharding trade-offs."
> "Postgres vs Mongo vs DynamoDB — scalability trade-offs."
> "Choosing DBs for event-driven architectures."

**Security & Workflow**
> "OWASP list applied to modern SaaS products."
> "Secure secret rotation strategies."
> "How should teams adopt trunk-based development?"
> "When to enforce code ownership policies?"

### Tech Career & Growth (20+ Subtopics)

**Skills & Role Analysis**
> "What skills does a senior SWE actually need?"
> "Learning path from SWE → DevOps Engineer."
> "Staff engineer expectations at top companies."

**Job Search & Interviews**
> "Which companies value system design the most?"
> "What resume sections matter most for backend roles?"
> "Create a 6-week plan for FAANG interviews."
> "Behavioral interview templates for leadership roles."

**Market Trends & Strategy**
> "AI engineer salary trajectories?"
> "Which regions pay highest for DevOps?"
> "Which specializations stay strong in the next 10 years?"
> "Is AI automation reducing SWE demand?"

---

## Advanced Query Capabilities

With the implementation of the **Knowledge Extraction Layer**, the agent can now answer complex analytical questions that require structured data parsing.

### Filtering & Attributes
> "Show me all free & open-source CI tools you found."
> "Which editors support Python and work offline?"
> "Filter only tools with low maintenance risk."
> "Show only the open-source tools among all those mentioned."
> "Which cloud services offer free tiers with good reliability?"

### Ranking & Sorting
> "Rank all logging platforms by ease of integration."
> "Sort AI coding tools by onboarding difficulty."
> "Rank the CI tools by beginner friendliness."
> "Order the coding editors by learning curve."

### Risk Analysis
> "Compare VS Code, Cursor, Windsurf only by risks."
> "List security risks of all cloud solutions mentioned."
> "Compare all tools only by business risk."
> "Which deployment tools have the highest vendor lock-in risk?"

### Timeline & Change Tracking
> "Summarize GitHub Actions releases over time."
> "What tools have unclear roadmaps or abandoned repos?"
> "List major changes in GitHub Actions from 2019→2024."
> "Which projects appear abandoned (no updates)?"

### Relationship Mapping
> "Which databases integrate with Kafka out-of-the-box?"
> "What tools compete directly with Terraform?"
> "Which observability tools integrate with Kubernetes natively?"

### Multi-Source Consolidation
> "Combine every article and give me the consolidated pros/cons of Kubernetes."
> "List all ML workflow tools you found across previous runs."

---

## Installation

Ensure you have `uv` installed for dependency management.

```bash
# Sync dependencies
uv sync

# Run the backend server
uv run server.py