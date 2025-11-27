# src/topics/registry.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any


from .tools.developer_tools.workflow import DeveloperToolsWorkflow
from .tools.saas.workflow import SaaSWorkflow
from .tools.api.workflow import APIWorkflow
from .tools.ai_ml.workflow import AIWorkflow
from .tools.security.workflow import SecurityWorkflow
from .tools.cloud.workflow import CloudWorkflow
from .tools.database.workflow import DatabaseWorkflow




@dataclass
class TopicConfig:
    """
    Generic description of a research topic.

    key: internal key used in requests and routing.
    label: human-friendly label (for UI, logs, etc.).
    description: short text to explain what this topic covers.
    workflow_factory: function/class that returns a workflow instance.
    domain: optional logical domain (e.g. 'cs', 'finance', 'bio', etc.)
    """
    key: str
    label: str
    description: str
    workflow_factory: Callable[[], Any]
    domain: str = "cs"


TOPIC_CONFIGS: Dict[str, TopicConfig] = {
    "developer_tools": TopicConfig(
        key="developer_tools",
        label="Developer Tools",
        description="IDEs, editors, debuggers, build tools, CI/CD, and developer productivity tooling.",
        workflow_factory=DeveloperToolsWorkflow,
        domain="tools", # domain="cs",
    ),
    "saas": TopicConfig(
        key="saas",
        label="SaaS Products",
        description="Hosted subscription software (B2B/B2C SaaS apps, CRM, helpdesk, collaboration tools, etc.).",
        workflow_factory=SaaSWorkflow,
        domain="tools", # domain="cs",
    ),
    "api": TopicConfig(
        key="api",
        label="API Platforms",
        description="Platforms whose main product is an API/SDK: REST/GraphQL APIs, webhooks, API gateways, etc.",
        workflow_factory=APIWorkflow,
        domain="tools", # domain="cs",
    ),
    "ai_ml": TopicConfig(
        key="ai_ml",
        label="AI & ML Platforms",
        description="LLM providers, ML platforms, model hosting, vector DBs, embeddings, fine-tuning, AI infra.",
        workflow_factory=AIWorkflow,
        domain="tools", # domain="cs",
    ),
    "security": TopicConfig(
        key="security",
        label="Security & Identity",
        description="Auth, identity, IAM, SSO, OAuth/OIDC, MFA, zero trust, WAF, bot/fraud detection, security tools.",
        workflow_factory=SecurityWorkflow,
        domain="tools", # domain="cs",
    ),
    "cloud": TopicConfig(
        key="cloud",
        label="Cloud & Infrastructure",
        description="Cloud providers and infra: compute, storage, networking, serverless, managed Kubernetes, etc.",
        workflow_factory=CloudWorkflow,
        domain="tools", # domain="cs",
    ),
    "database": TopicConfig(
        key="database",
        label="Databases & Data Platforms",
        description="SQL/NoSQL DBs, data warehouses, OLTP/OLAP engines, and managed database services.",
        workflow_factory=DatabaseWorkflow,
        domain="tools", # domain="cs",
    ),
}


def build_workflows() -> Dict[str, Any]:
    """
    Instantiate one workflow per topic key.
    If you want lazy creation later, you can change this to return a factory.
    """
    return {key: cfg.workflow_factory() for key, cfg in TOPIC_CONFIGS.items()}

def get_topic_labels() -> Dict[str, str]:
    """
    Returns: { topic_key: label }
    """
    return {key: cfg.label for key, cfg in TOPIC_CONFIGS.items()}

def get_topic_descriptions() -> Dict[str, str]:
    """
    Returns: { topic_key: description }
    Used by the LLM router; no server hard-coding needed.
    """
    return {key: cfg.description for key, cfg in TOPIC_CONFIGS.items()}
