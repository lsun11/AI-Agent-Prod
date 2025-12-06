# src/diagrams/flowchart_models.py
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class FlowNode(BaseModel):
    """One box in the flowchart."""
    id: str = Field(description="Stable node id, e.g. 'start', 'step_1'")
    label: str = Field(description="Short human-readable label")
    kind: str = Field(
        default="step",
        description="One of: 'start', 'step', 'decision', 'end'",
    )


class FlowEdge(BaseModel):
    """Directed arrow between nodes."""
    source: str = Field(description="source node id")
    target: str = Field(description="target node id")
    label: Optional[str] = Field(
        default=None,
        description="Optional edge label, e.g. 'yes', 'no'",
    )


class FlowchartSpec(BaseModel):
    """
    Generic flowchart representation.

    - nodes: each step / decision
    - edges: arrows showing order or branching
    """
    title: Optional[str] = None
    nodes: List[FlowNode] = Field(default_factory=list)
    edges: List[FlowEdge] = Field(default_factory=list)
