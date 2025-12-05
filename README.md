AI Agent Researcher & Document Generator

Multi-Source AI Research Pipeline • Structured Knowledge Extraction • PDF/PPTX/DOCX Output

📌 Overview

This repository contains an advanced AI-powered research assistant that transforms raw user queries into structured, presentation-ready research reports across multiple technical domains:

🔎 Intelligent topic classification

🌐 Multi-source web research (multi-pass Firecrawl search + deep scraping)

🧠 Knowledge extraction (entities, relationships, pros/cons, risks, timeline)

🧩 Topic-specific LangGraph workflows

🎨 LLM-based layout engine for structured Markdown + comparison tables

📄 Multi-format export: PDF, DOCX, PPTX, TXT

💬 Streaming chat interface (FastAPI + SSE)

🌏 English & Chinese support with CJK-safe PDF rendering

This agent produces reports that normally require hours of Google searching, reading articles, comparing tools, and assembling documents. Now it is done automatically in seconds.

✨ What’s New (Major Enhancements)
🟦 1. Multi-Source, Multi-Pass Web Research

The agent now performs:

Multiple Firecrawl search passes

Automatic deduplication of pages

Optional deep scraping of official product websites

Smart content merging

This produces dramatically stronger research coverage and reduces hallucination.

🟪 2. Shared RootWorkflow + Topic Workflows

All topics inherit:

Firecrawl utilities

Multi-source normalization + content aggregation

Logging

LLM switching

Knowledge extraction helpers

Topic workflows only implement:

Resource summarization

Aggregated markdown builder

Final recommendation generator

This makes the system both extensible and uniform across topics.

🟩 3. Global Knowledge Extraction Layer (NEW!)

A new shared component (RootPrompts + RootWorkflow) performs:

Entity extraction (tools, companies, APIs, cloud services, concepts)

Relationship extraction (integrates_with, depends_on, competes_with…)

Pros / Cons per entity

Risk classification (business, technical, maintainability, security)

Timelines (major releases, roadmap events, changes)

Structured output is stored in each topic’s state.knowledge.

This unlocks entirely new categories of reasoning:

Queryable attributes (filter all free open-source tools)

Cross-entity comparisons

Risk analysis

Sorting and ranking

Timeline-based conclusions

Relationship graphs

This is a major functional upgrade.

🟧 4. Richer Document Generation

The LLM layout engine now:

Generates comparison tables automatically

Creates multi-slide presentations

Properly renders Markdown (bold, lists, headings)

Uses CJK-safe fonts and theme-consistent PDF styling

Supports brand colors and logos scraped from websites

🧭 Supported Major Topics
1. Developer Tools & Ecosystem

Examples:

Languages & SDKs

IDEs (VS Code, Cursor, Windsurf…)

Debuggers / Profilers

CI/CD tools

DevOps platforms

Version control workflows

Code quality & static analysis

2. Software Engineering & Architecture

Examples:

Microservices vs monolith trade-offs

Testing strategies (unit / integration / contract / E2E)

CI/CD pipelines

System design patterns

Observability stack

Refactoring patterns & maintainability

Scaling & reliability

Security / privacy engineering

3. Tech Career, Growth & Strategy

Examples:

Skill roadmaps

Role comparisons (SWE vs DevOps vs MLE)

Salary/market trend analysis

Resume feedback

Interview preparation

Career transitions

Promotion guidance

Learning plans with timelines

🔥 New Question Types Now Possible With Knowledge Extraction
🟦 Filtering & Attribute Queries

“Show me all free & open-source CI tools you found.”

“Which editors support Python and work offline?”

“Filter only tools with low maintenance risk.”

🟩 Ranking & Sorting

“Rank all logging platforms by ease of integration.”

“Sort AI coding tools by onboarding difficulty.”

🟧 Risk-Only Queries

“Compare VS Code, Cursor, Windsurf only by risks.”

“List security risks of all cloud solutions mentioned.”

🟥 Timeline & Change Tracking

“Summarize GitHub Actions releases over time.”

“What tools have unclear roadmaps or abandoned repos?”

🟨 Relationship-Driven Questions

“Which databases integrate with Kafka out-of-the-box?”

“What tools compete directly with Terraform?”

🟪 Multi-Source Fact Consolidation

“Combine every article and give me the consolidated pros/cons of Kubernetes.”

“List all ML workflow tools you found across previous runs.”

📘 Comprehensive Question Examples

(Organized by major topic, with 20+ subtopics, plus knowledge extraction–enabled examples.)

🟦 1. Developer Tools (20+ subtopics)
IDEs / Code Editors

“Which Python IDE is best for beginners?”

“VS Code vs Cursor vs Windsurf — difference in collaboration features?”

“Which editors run fully offline?”

AI Coding Assistants

“Compare GitHub Copilot, Cursor, Windsurf on reliability.”

“Which AI editor understands large monorepos best?”

Build Tools

“Maven vs Gradle — which is better for large Java projects?”

Package Managers

“pip vs poetry vs uv — performance & environment isolation?”

Debugging & Profiling

“Which profilers work best with async Python?”

CI/CD Tools

“Compare GitHub Actions, CircleCI, Jenkins, and GitLab CI for Docker deployments.”

“Which CI tool is fastest for PR workflows?”

Testing Frameworks

“pytest vs unittest — which scales better?”

Documentation Tools

“mkdocs vs docusaurus vs Sphinx — pros & cons?”

Version Control / Git Workflows

“GitFlow vs Trunk-based development — company-size implications?”

DevOps Toolchains

“Best tools for Kubernetes cluster GitOps?”

“Which IaC tools compete with Terraform?”

🟩 2. Software Engineering (20+ subtopics)
Architecture Patterns

“Microservices vs monolith — long-term cost analysis.”

“Event-driven architecture — main risks?”

API Design

“REST vs GraphQL vs gRPC — best fit for mobile apps?”

“How to design backward-compatible APIs?”

Testing Strategies

“What balance of unit vs integration tests is ideal for microservices?”

“Contract testing — when to adopt it?”

CI/CD & Deployment

“Zero-downtime deployment strategies?”

“Best practices for staging → production workflow.”

Observability

“Prometheus vs Datadog vs OpenTelemetry — differences?”

“How to design tracing for async systems?”

Reliability

“SLOs vs SLIs vs SLAs — practical examples?”

“How to implement circuit breakers effectively?”

Performance

“Bottlenecks in Python web frameworks?”

“Caching layers vs DB sharding trade-offs.”

Security

“OWASP list applied to modern SaaS products.”

“Secure secret rotation strategies.”

Databases

“Postgres vs Mongo vs DynamoDB — scalability trade-offs.”

“Choosing DBs for event-driven architectures.”

Dev Workflow & Team Practices

“How should teams adopt trunk-based development?”

“When to enforce code ownership policies?”

🟨 3. Tech Career & Growth (20+ subtopics)
Skill Growth

“What skills does a senior SWE actually need?”

“Learning path from SWE → DevOps Engineer.”

Job Search

“Which companies value system design the most?”

“What resume sections matter most for backend roles?”

Salary & Market Trends

“AI engineer salary trajectories?”

“Which regions pay highest for DevOps?”

Promotions & Performance

“How to write strong promotion packets?”

“Staff engineer expectations at top companies.”

Interview Prep

“Create a 6-week plan for FAANG interviews.”

“Behavioral interview templates for leadership roles.”

Role Transitions

“SWE → ML Engineer: required projects & timeline.”

“Cloud Engineer → SRE roadmap.”

Long-Term Strategy

“Which specializations stay strong in the next 10 years?”

“Is AI automation reducing SWE demand?”

🔥 Advanced Questions (Only Possible With New Knowledge Extraction)

These were not answerable before. Now they are trivial for your agent.

Entity Filtering

“Show only the open-source tools among all those mentioned.”

“Which cloud services offer free tiers with good reliability?”

Multi-Entity Risk Analysis

“Compare all tools only by business risk.”

“Which deployment tools have the highest vendor lock-in risk?”

Relationship Queries

“Which observability tools integrate with Kubernetes natively?”

“What competes directly with Terraform?”

Sorted Rankings

“Rank the CI tools by beginner friendliness.”

“Order the coding editors by learning curve.”

Timeline Questions

“List major changes in GitHub Actions from 2019→2024.”

“Which projects appear abandoned (no updates)?”

Cross-Run Consolidation

(if you add long-term memory)

“Across all your past research runs, list every free AI coding tool.”

“Summarize risks across all database comparisons you’ve done before.”

🧱 Architecture Overview

(kept from your original README but now improved)

See the main file for full details.
Key components:

RootWorkflow
Multi-pass research + scraping + knowledge extraction + logging

TopicWorkflows
Developer Tools / Software Engineering / Career

RootPrompts
Shared prompting layer for knowledge extraction

Layout LLM
Converts raw analysis into beautiful Markdown + slides

Export Engine
PDF / DOCX / PPTX / TXT with CJK support

📦 Installation
uv sync
uv run server.py


Serve frontend from frontend/.