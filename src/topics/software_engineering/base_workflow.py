# src/topics/software_eng/workflow.py
from __future__ import annotations

import json
from typing import List

from langgraph.graph import StateGraph

from ..root_workflow import RootWorkflow
from .base_prompts import BaseSoftwareEngPrompts
from .base_models import (
    BaseSoftwareEngState,
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
)


class BaseSoftwareEngWorkflow(RootWorkflow[BaseSoftwareEngState]):
    topic_label = "SoftwareEngineering"
    topic_tag = "Base"

    def __init__(self) -> None:
        super().__init__()
        self.state_model = BaseSoftwareEngState
        self.prompts = BaseSoftwareEngPrompts()
        self.workflow = self.build_graph()

    # -------------------------
    # Step 1: interpret query
    # -------------------------
    def step_1_interpret_query(self, state: BaseSoftwareEngState) -> BaseSoftwareEngState:
        # For now, we just log. Later you can add intent classification here.
        self._log(f"Interpreting query: {state.query}")
        return state

    # -------------------------
    # Step 2: plan search strategy + collect sources
    # -------------------------
    def step_2_collect_sources(self, state: BaseSoftwareEngState) -> BaseSoftwareEngState:
        self._log("Collecting multi-pass articles for software engineering topic...")
        merged_content, meta_items = self._multi_pass_articles(state.query)

        # Populate aggregated_markdown
        new_state = state.model_copy(update={"aggregated_markdown": merged_content})

        # Initialize resources with basic title/url from meta
        resources: List[BaseSoftwareEngResourceSummary] = []
        for item in meta_items:
            resources.append(
                BaseSoftwareEngResourceSummary(
                    title=item.get("title") or "(untitled)",
                    url=item.get("url") or "",
                )
            )

        if resources:
            new_state = new_state.model_copy(update={"resources": resources})

        return new_state

    # -------------------------
    # Step 3: summarize resources / extract keywords
    # -------------------------
    def step_3_summarize(self, state: BaseSoftwareEngState) -> BaseSoftwareEngState:
        if not state.aggregated_markdown:
            self._log("No aggregated markdown available; skipping summarization.")
            return state

        self._log("Summarizing aggregated content into keywords / key points...")

        user_msg = self.prompts.tool_extraction_user(
            query=state.query,
            content=state.aggregated_markdown,
        )

        raw_response = self.llm.invoke(
            [
                {"role": "system", "content": self.prompts.TOOL_EXTRACTION_SYSTEM},
                {"role": "user", "content": user_msg},
            ]
        )

        text = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
        lines = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]
        keywords = [line for line in lines if line]

        # Put them both into extracted_keywords and into the first resource key_points
        new_state = state.model_copy(update={"extracted_keywords": keywords})

        if not new_state.resources:
            # Create a synthetic resource if none exist
            synthetic = BaseSoftwareEngResourceSummary(
                title="Aggregated software engineering research",
                url="",
                key_points=keywords,
            )
            new_state = new_state.model_copy(update={"resources": [synthetic]})
        else:
            # Attach key points to the first resource as a simple approach
            first = new_state.resources[0].model_copy(update={"key_points": keywords})
            remaining = new_state.resources[1:]
            new_state = new_state.model_copy(update={"resources": [first, *remaining]})

        return new_state

    # -------------------------
    # Step 4: knowledge extraction
    # -------------------------
    def step_4_extract_knowledge(self, state: BaseSoftwareEngState) -> BaseSoftwareEngState:
        if not state.aggregated_markdown:
            self._log("No aggregated markdown; skipping knowledge extraction.")
            return state

        result = self._extract_knowledge_from_markdown(
            aggregated_markdown=state.aggregated_markdown,
            prompts=self.prompts,
        )
        if result is None:
            return state

        return state.model_copy(update={"knowledge": result})

    # -------------------------
    # Step 5: higher-level analysis / recommendation
    # -------------------------
    def step_5_analyze(self, state: BaseSoftwareEngState) -> BaseSoftwareEngState:
        self._log("Generating software engineering recommendation from resources + knowledge...")

        # Serialize a light-weight view of resources and (optionally) knowledge
        resources_payload = {
            "resources": [r.model_dump() for r in state.resources],
            "knowledge": state.knowledge.model_dump() if state.knowledge else None,
        }
        serialized = json.dumps(resources_payload, ensure_ascii=False)

        user_msg = self.prompts.recommendations_user(
            query=state.query,
            serialized_resources=serialized,
        )

        raw_response = self.llm.with_structured_output(BaseSoftwareEngRecommendation).invoke(
            [
                {"role": "system", "content": self.prompts.RECOMMENDATIONS_SYSTEM},
                {"role": "user", "content": user_msg},
            ]
        )

        recommendation: BaseSoftwareEngRecommendation = raw_response
        return state.model_copy(update={"analysis": recommendation})

    # -------------------------
    # Step 6: generate final markdown report
    # -------------------------
    def step_6_generate_report(self, state: BaseSoftwareEngState) -> BaseSoftwareEngState:
        self._log("Building final markdown report for software engineering topic...")

        parts: List[str] = []

        parts.append(f"# Software Engineering Report\n")
        parts.append(f"## Query\n{state.query}\n")

        if state.resources:
            parts.append("## Key Resources\n")
            for r in state.resources:
                parts.append(f"- **{r.title}** — {r.url}")
            parts.append("")

        if state.extracted_keywords:
            parts.append("## Extracted Key Points\n")
            for k in state.extracted_keywords:
                parts.append(f"- {k}")
            parts.append("")

        if state.knowledge:
            parts.append("## Structured Knowledge (Entities & Risks)\n")
            if state.knowledge.entities:
                parts.append("### Entities\n")
                for e in state.knowledge.entities:
                    type_str = f" ({e.type})" if e.type else ""
                    parts.append(f"- **{e.name}**{type_str}: {e.description or ''}")
            if state.knowledge.risks:
                parts.append("\n### Risks\n")
                for r in state.knowledge.risks:
                    prefix = f"[{r.category}] " if r.category else ""
                    parts.append(f"- {prefix}{r.text}")
            parts.append("")

        if state.analysis:
            parts.append("## Recommendation\n")
            parts.append(f"**Summary**\n{state.analysis.summary}\n")
            if state.analysis.best_practices:
                parts.append("**Best Practices**")
                for bp in state.analysis.best_practices:
                    parts.append(f"- {bp}")
            if state.analysis.pitfalls:
                parts.append("\n**Pitfalls**")
                for p in state.analysis.pitfalls:
                    parts.append(f"- {p}")
            if state.analysis.suggested_action_plan:
                parts.append("\n**Suggested Action Plan (Next 1–4 weeks)**")
                for step in state.analysis.suggested_action_plan:
                    parts.append(f"- {step}")
            if state.analysis.suggested_tools:
                parts.append("\n**Suggested Tools**")
                for t in state.analysis.suggested_tools:
                    parts.append(f"- {t}")
            if state.analysis.applicable_scenarios:
                parts.append("\n**Applicable Scenarios**")
                for s in state.analysis.applicable_scenarios:
                    parts.append(f"- {s}")
            parts.append("")

        final_markdown = "\n".join(parts).strip()
        return state.model_copy(update={"final_markdown": final_markdown})

    # -------------------------
    # Build LangGraph graph
    # -------------------------
    def build_graph(self):
        graph = StateGraph(BaseSoftwareEngState)

        graph.add_node("interpret_query", self.step_1_interpret_query)
        graph.add_node("collect_sources", self.step_2_collect_sources)
        graph.add_node("summarize", self.step_3_summarize)
        graph.add_node("extract_knowledge", self.step_4_extract_knowledge)
        graph.add_node("analyze", self.step_5_analyze)
        graph.add_node("generate_report", self.step_6_generate_report)

        graph.set_entry_point("interpret_query")
        graph.add_edge("interpret_query", "collect_sources")
        graph.add_edge("collect_sources", "summarize")
        graph.add_edge("summarize", "extract_knowledge")
        graph.add_edge("extract_knowledge", "analyze")
        graph.add_edge("analyze", "generate_report")
        graph.set_finish_point("generate_report")

        return graph.compile()
