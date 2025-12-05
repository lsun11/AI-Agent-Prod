# src/models/knowledge_extraction.py
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str = Field(..., description="Canonical name of the entity.")
    type: Optional[str] = Field(
        default=None,
        description="Type of entity, e.g. 'company', 'product', 'tool', 'api', 'concept'.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Short human-readable description of this entity.",
    )


class Relationship(BaseModel):
    source: str = Field(..., description="Name of the source entity.")
    target: str = Field(..., description="Name of the target entity.")
    type: str = Field(
        ...,
        description="Relationship type, e.g. 'offers', 'competes_with', 'integrates_with', 'depends_on'.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional explanation or context for the relationship.",
    )


class ProConItem(BaseModel):
    entity: Optional[str] = Field(
        default=None,
        description="Entity this item refers to, e.g. product/tool name.",
    )
    aspect: Optional[str] = Field(
        default=None,
        description="Feature or aspect (e.g., 'performance', 'pricing', 'DX').",
    )
    text: str = Field(..., description="The actual pro or con statement.")


class RiskItem(BaseModel):
    entity: Optional[str] = Field(
        default=None,
        description="Entity this risk is about (tool, vendor, approach).",
    )
    category: Optional[
        Literal[
            "technical",
            "integration",
            "security",
            "compliance",
            "maintainability",
            "business",
            "reliability",
            "other",
        ]
    ] = Field(
        default="other",
        description="High-level risk category.",
    )
    text: str = Field(..., description="Description of the risk.")
    severity: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        default=None, description="Optional severity level."
    )


class TimelineItem(BaseModel):
    date: Optional[str] = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) or approximate text (e.g. 'Q1 2024').",
    )
    event: str = Field(..., description="Short description of the event.")
    entity: Optional[str] = Field(
        default=None, description="Entity associated with this event, if any."
    )
    source: Optional[str] = Field(
        default=None, description="URL or document identifier for this event."
    )


class KnowledgeExtractionResult(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    pros: List[ProConItem] = Field(default_factory=list)
    cons: List[ProConItem] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    timeline: List[TimelineItem] = Field(default_factory=list)
