import json
from typing import Any, Dict, List
from pydantic import BaseModel

def _format_career_action_plan_doc(data: Dict[str, Any]) -> str:
    goal_summary: str = data.get("goal_summary") or ""
    main_theme: str = data.get("main_theme") or ""
    steps: List[Dict[str, Any]] = data.get("steps") or []
    risks: List[str] = data.get("risks") or []
    success_metrics: List[str] = data.get("success_metrics") or []

    lines: List[str] = []

    lines.append("## Career Action Plan")
    lines.append("")

    lines.append("### Goal summary:")
    lines.append(goal_summary or "No goal summary provided.")
    lines.append("")

    lines.append("### Main theme:")
    lines.append(main_theme or "No main theme provided.")
    lines.append("")

    lines.append("### Steps:")
    if not steps:
        lines.append("No steps were generated.")
    else:
        for idx, step in enumerate(steps, start=1):
            title = step.get("title") or f"Step {idx}"
            description = step.get("description") or ""
            category = step.get("category") or ""
            estimated_time = step.get("estimated_time")
            resources: List[str] = step.get("resources") or []
            outcome = step.get("concrete_outcome")

            lines.append(f"- Step {idx}: {title}")
            if category:
                lines.append(f"  Category: {category}")
            if estimated_time:
                lines.append(f"  Estimated time: {estimated_time}")
            if description:
                lines.append(f"  Details: {description}")
            if resources:
                lines.append("  Resources:")
                for r in resources:
                    lines.append(f"    - {r}")
            if outcome:
                lines.append(f"  Outcome: {outcome}")
            lines.append("")

    lines.append("### Risks & pitfalls:")
    if risks:
        for r in risks:
            lines.append(f"- {r}")
    else:
        lines.append("- No risks listed.")
    lines.append("")

    lines.append("### Success metrics:")
    if success_metrics:
        for m in success_metrics:
            lines.append(f"- {m}")
    else:
        lines.append("- No success metrics defined.")
    lines.append("")

    return "\n".join(lines)

#
def _format_se_recommendation_doc(data: Dict[str, Any]) -> str:
    summary: str = data.get("summary") or ""
    best_practices: List[str] = data.get("best_practices") or []
    pitfalls: List[str] = data.get("pitfalls") or []
    action_plan: List[str] = data.get("suggested_action_plan") or []
    suggested_tools: List[str] = data.get("suggested_tools") or []
    applicable_scenarios: List[str] = data.get("applicable_scenarios") or []

    lines: List[str] = []

    lines.append("## Software Engineering Recommendation")
    lines.append("")

    lines.append("### Summary:")
    lines.append(summary or "No summary provided.")
    lines.append("")

    lines.append("### Best practices:")
    if best_practices:
        for bp in best_practices:
            lines.append(f"- {bp}")
    else:
        lines.append("- No best practices listed.")
    lines.append("")

    lines.append("### Pitfalls:")
    if pitfalls:
        for p in pitfalls:
            lines.append(f"- {p}")
    else:
        lines.append("- No pitfalls listed.")
    lines.append("")

    lines.append("### Suggested action plan (1–4 weeks):")
    if action_plan:
        for idx, step in enumerate(action_plan, start=1):
            lines.append(f"{idx}. {step}")
    else:
        lines.append("No action plan provided.")
    lines.append("")

    if suggested_tools:
        lines.append("### Suggested tools:")
        for t in suggested_tools:
            lines.append(f"- {t}")
        lines.append("")

    if applicable_scenarios:
        lines.append("### Applicable scenarios:")
        for s in applicable_scenarios:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)


def _analysis_to_dict(analysis: Any) -> Dict[str, Any]:
    """Normalize Pydantic models and dicts to a dict."""
    if isinstance(analysis, BaseModel):
        return analysis.model_dump()
    if isinstance(analysis, dict):
        return analysis
    return {}


def _extract_json_from_string(text: str) -> Dict[str, Any] | None:
    """
    Try hard to extract a JSON object from a string that may contain
    markdown fences or extra commentary.
    """
    # First try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Strip markdown-style code fences if present
    # e.g. ```json\n{...}\n``` or ```\n{...}\n```
    if "```" in text:
        # take content between the first and last ```
        first = text.find("```")
        last = text.rfind("```")
        if first != -1 and last != -1 and last > first:
            inner = text[first + 3 : last]
            # strip potential language tag: ```json
            inner = inner.lstrip("json").lstrip("JSON").strip()
            try:
                parsed = json.loads(inner)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    # As a last resort, extract the substring from first '{' to last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    return None


def _format_tool_recommendation_doc(data: Dict[str, Any]) -> str:
    primary_choice = data.get("primary_choice")
    backup_options: List[str] = data.get("backup_options") or []
    summary: str = data.get("summary") or ""
    selection_criteria: List[str] = data.get("selection_criteria") or []
    tradeoffs_raw = data.get("tradeoffs") or []
    steps: List[str] = data.get("step_by_step_decision_guide") or []

    lines: List[str] = []

    lines.append("## Tool / Service Recommendation")
    lines.append("")

    # Primary choice
    lines.append("### Primary choice:")
    if primary_choice:
        lines.append(f"- Recommended tool: {primary_choice}")
    else:
        lines.append("- No single clear primary choice identified.")
    # lines.append("")

    # Backup options
    lines.append("### Backup options:")
    if backup_options:
        for opt in backup_options:
            lines.append(f"- {opt}")
    else:
        lines.append("- No backup options suggested.")
    # lines.append("")

    # Summary
    lines.append("### Summary:")
    lines.append(summary or "No summary provided.")
    lines.append("")

    # Selection criteria
    lines.append("### Selection criteria:")
    if selection_criteria:
        for crit in selection_criteria:
            lines.append(f"- {crit}")
    else:
        lines.append("- No explicit criteria listed.")
    lines.append("")

    # Trade-offs (handle both list[str] and list[dict])
    lines.append("### Trade-offs:")
    if isinstance(tradeoffs_raw, list) and tradeoffs_raw:
        if isinstance(tradeoffs_raw[0], dict):
            # list of {aspect, description}
            for t in tradeoffs_raw:
                aspect = t.get("aspect") or "Trade-off"
                desc = t.get("description") or ""
                lines.append(f"- **{aspect}**: {desc}")
        else:
            # assume list of strings
            for t in tradeoffs_raw:
                lines.append(f"- {t}")
    else:
        lines.append("- No trade-offs captured.")
    lines.append("")

    # Step-by-step decision guide
    lines.append("### Step-by-step decision guide:")
    if steps:
        for idx, step in enumerate(steps, start=1):
            lines.append(f"{idx}. {step}")
    else:
        lines.append("No decision guide steps provided.")
    lines.append("")

    return "\n".join(lines)


def _format_generic_analysis_doc(data: Dict[str, Any]) -> str:
    """
    Fallback that mirrors your old 'summary / best_practices / pitfalls / action_plan' layout.
    """
    lines: List[str] = []

    summary = data.get("summary") or data.get("description")
    if summary:
        lines.append(f"Summary:\n{summary}\n")

    best_practices = data.get("best_practices") or data.get("tips")
    if best_practices:
        lines.append("Best Practices:")
        for idx, bp in enumerate(best_practices, 1):
            lines.append(f"{idx}. {bp}")
        lines.append("")

    pitfalls = data.get("pitfalls")
    if pitfalls:
        lines.append("Pitfalls / Risks:")
        for idx, pf in enumerate(pitfalls, 1):
            lines.append(f"{idx}. {pf}")
        lines.append("")

    action_plan = data.get("suggested_action_plan") or data.get("action_plan")
    if action_plan:
        lines.append("Suggested Action Plan:")
        for idx, step in enumerate(action_plan, 1):
            lines.append(f"{idx}. {step}")
        lines.append("")

    if not lines:
        # nothing matched, just dump it
        return json.dumps(data, indent=2, ensure_ascii=False)

    return "\n".join(lines)


def to_document(analysis: Any) -> str:
    """
    Central formatter for *all* analysis outputs.

    - If analysis is a JSON string → extract/parse JSON and pretty-print.
    - If it's a Pydantic model or dict → format by shape.
    - If it's plain text → return as-is.
    """

    # Case A: string -> try to extract JSON, otherwise return as text
    if isinstance(analysis, str):
        data = _extract_json_from_string(analysis)
        if data is None:
            # Just plain text or unusable JSON → keep old behavior
            return analysis
    else:
        # Non-string: normalize to dict
        data = _analysis_to_dict(analysis)
        if not data:
            return str(analysis)

    keys = set(data.keys())

    # Tool comparison recommendation
    if {"primary_choice", "backup_options", "step_by_step_decision_guide"}.issubset(keys):
        return _format_tool_recommendation_doc(data)

    # Career action plan
    if {"goal_summary", "main_theme", "steps"}.issubset(keys):
        return _format_career_action_plan_doc(data)

    # Software engineering recommendation
    if {"summary", "best_practices", "pitfalls", "suggested_action_plan"}.issubset(keys):
        return _format_se_recommendation_doc(data)

    # Fallback to generic layout
    return _format_generic_analysis_doc(data)
