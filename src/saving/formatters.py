# src/saving/formatters.py
from typing import Any, Iterable, List
import re
from pydantic import BaseModel
from ..format_text import to_document
from .highlight import ai_highlight


def _get_items_from_result(result: Any) -> Iterable[Any]:
    """
    Try to extract a list of 'items' from any kind of result model.
    """
    if hasattr(result, "companies") and getattr(result, "companies", None):
        return result.companies

    if hasattr(result, "resources") and getattr(result, "resources", None):
        return result.resources

    if hasattr(result, "items") and getattr(result, "items", None):
        return result.items

    return []


def format_result_text(query: str, result: Any) -> str:
    lines: List[str] = []

    lines.append(f"📊 Results for: {query}. Click a bubble to open the links")

    items = list(_get_items_from_result(result))

    if not items:
        lines.append("")
        summary = getattr(result, "analysis", None) or getattr(result, "summary", None)
        if summary:
            lines.append("Summary / Analysis:")
            lines.append("-" * 40)
            lines.append(str(summary))
        else:
            lines.append("(No structured items were returned.)")
        return "\n".join(lines)

    for i, item in enumerate(items, 1):
        name = getattr(item, "name", None) or getattr(item, "title", None) or f"Item {i}"
        lines.append(f"\n{i}. 🏢 **{name}**")

        website = getattr(item, "website", None) or getattr(item, "url", None)
        if website:
            lines.append(f"   🌐 Website: {website}")

        if hasattr(item, "pricing_model"):
            pricing_model = getattr(item, "pricing_model", None)
            if pricing_model is not None:
                lines.append(f"   💰 Pricing: {pricing_model}")

        if hasattr(item, "pricing_details"):
            pricing_details = getattr(item, "pricing_details", None)
            if pricing_details:
                lines.append(f"   💰 Pricing Details: {pricing_details}")

        if hasattr(item, "is_open_source"):
            is_open = getattr(item, "is_open_source", None)
            if is_open is not None:
                lines.append(f"   📖 Open Source: {is_open}")

        tech_stack = getattr(item, "tech_stack", None)
        if tech_stack:
            lines.append(f"   🛠️ Tech Stack: {', '.join(tech_stack[:5])}")

        competitors = getattr(item, "competitors", None)
        if competitors:
            lines.append(f"   🤼 Competitors: {', '.join(competitors[:5])}")

        language_support = getattr(item, "language_support", None)
        if language_support:
            lines.append(f"   💻 Language Support: {', '.join(language_support[:5])}")

        if hasattr(item, "api_available"):
            api_available = getattr(item, "api_available", None)
            if api_available is not None:
                api_status = "✔ Available" if api_available else "✘ Not Available"
                lines.append(f"   🔌 API: {api_status}")

        integration_caps = getattr(item, "integration_capabilities", None)
        if integration_caps:
            lines.append(f"   🔗 Integrations: {', '.join(integration_caps[:4])}")

        target_users = getattr(item, "target_users", None)
        if target_users:
            lines.append(f"   👤 Target users: {', '.join(target_users[:4])}")

        primary_use_cases = getattr(item, "primary_use_cases", None)
        if primary_use_cases:
            lines.append(f"   Primary use cases: {', '.join(primary_use_cases[:4])}")

        category = getattr(item, "category", None)
        if category:
            lines.append(f"   📦 Category: {category}")

        tags = getattr(item, "tags", None)
        if tags:
            lines.append(f"   🏷️ Tags: {', '.join(tags[:8])}")

        difficulty = getattr(item, "difficulty", None)
        if difficulty:
            lines.append(f"   📈 Difficulty: {difficulty}")

        if hasattr(item, "free_tier_available"):
            free_tier = getattr(item, "free_tier_available", None)
            if free_tier is not None:
                lines.append(f"   🆓 Free tier available: {free_tier}")

        regions_coverage = getattr(item, "regions_coverage", None)
        if regions_coverage:
            lines.append(f"   🌍 Regions / coverage: {regions_coverage}")

        if hasattr(item, "managed_kubernetes_available"):
            mk = getattr(item, "managed_kubernetes_available", None)
            if mk is not None:
                lines.append(f"   ☸️ Managed Kubernetes: {mk}")

        service_types = getattr(item, "service_types", None)
        if service_types:
            lines.append(f"   🚗 Service types: {', '.join(service_types[:5])}")

        city_coverage = getattr(item, "city_coverage", None)
        if city_coverage:
            lines.append(f"   🌆 City / region coverage: {city_coverage}")

        pricing_model_transport = getattr(item, "pricing_model_transport", None)
        if pricing_model_transport:
            lines.append(f"   💰 Transport pricing: {pricing_model_transport}")

        lines.append("")

        core_fields = {
            "name", "title", "website", "url",
            "pricing_model", "pricing_details", "is_open_source",
            "tech_stack", "competitors", "api_available",
            "language_support", "integration_capabilities",
            "category", "tags", "difficulty", "description", "summary",
        }
        ui_fields = {"primary_color", "brand_colors", "logo_url"}

        if isinstance(item, BaseModel):
            field_names = item.model_fields.keys()
        else:
            field_names = item.__dict__.keys()

        for field_name in field_names:
            if field_name in core_fields or field_name in ui_fields:
                continue
            if field_name.startswith("_"):
                continue

            value = getattr(item, field_name, None)
            if value in (None, [], {}):
                continue

            label = field_name.replace("_", " ").capitalize()

            if isinstance(value, list):
                rendered = ", ".join(str(v) for v in value[:8])
            else:
                rendered = str(value)

            lines.append(f"   🔧 {label}: {rendered}")

        lines.append("")

    analysis = getattr(result, "analysis", None) or getattr(result, "summary", None)
    if analysis is not None:
        lines.append("**Recommendations / Analysis:**")
        lines.append("-" * 40)
        if isinstance(analysis, str):
            lines.append(to_document(analysis))
        else:
            formatted = to_document(analysis)
            lines.append(formatted)

    analysis_text = "\n".join(lines)
    highlighted = ai_highlight(analysis_text)
    return highlighted
