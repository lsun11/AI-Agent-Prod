# src/diagrams/flowchart_render.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

from graphviz import Digraph

from .flowchart_models import FlowchartSpec, FlowNode, FlowEdge


def _node_shape(kind: str) -> str:
    """Map node kind to GraphViz shape."""
    kind = (kind or "").lower()
    if kind == "start":
        return "oval"
    if kind == "end":
        return "oval"
    if kind == "decision":
        return "diamond"
    return "box"


def flowchart_to_graphviz(spec: FlowchartSpec) -> Digraph:
    dot = Digraph(format="png")
    dot.attr(rankdir="TB")  # top -> bottom

    if spec.title:
        dot.attr(label=spec.title, labelloc="t", fontsize="14")

    # Nodes
    for node in spec.nodes:
        shape = _node_shape(node.kind)
        dot.node(node.id, label=node.label, shape=shape)

    # Edges
    for edge in spec.edges:
        attrs = {}
        if edge.label:
            attrs["label"] = edge.label
        dot.edge(edge.source, edge.target, **attrs)

    return dot


def render_flowchart_png(
    spec: FlowchartSpec,
    output_dir: Path,
    filename_prefix: str = "flowchart",
) -> Optional[Path]:
    """
    Render a FlowchartSpec to a PNG file and return the path.

    output_dir will be created if needed.
    """
    print("@@@@@@@@@@@@@@@@@@@Rendering flowchart PNG...")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        dot = flowchart_to_graphviz(spec)

        # graphviz.render returns the path including extension
        output_path_str = dot.render(
            filename=filename_prefix,
            directory=str(output_dir),
            cleanup=True,  # remove intermediate .dot
        )
        return Path(output_path_str)
    except Exception as e:
        print("Error rendering flowchart PNG:", e)
        return None
