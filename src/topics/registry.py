# src/topics/registry.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any

# Core / original CS-tool topics
from .tools.developer_tools.workflow import DeveloperToolsWorkflow
from .tools.saas.workflow import SaaSWorkflow
from .tools.api.workflow import APIWorkflow
from .tools.ai_ml.workflow import AIWorkflow
from .tools.security.workflow import SecurityWorkflow
from .tools.cloud.workflow import CloudWorkflow
from .tools.database.workflow import DatabaseWorkflow

# New, broader consumer / app-centric topics
from .tools.consumer_and_social.workflow import ConsumerAndSocialWorkflow
from .tools.content_and_website.workflow import ContentAndWebsiteWorkflow
from .tools.design.workflow import DesignWorkflow
from .tools.e_commerce.workflow import EcommerceWorkflow
from .tools.file_storage.workflow import FileStorageWorkflow
from .tools.messaging.workflow import MessagingWorkflow
from .tools.productivity.workflow import ProductivityWorkflow
from .tools.transportation.workflow import TransportationWorkflow


@dataclass
class TopicConfig:
    """
    Generic description of a research topic.

    key: internal key used in requests and routing.
    label: human-friendly label (for UI, logs, etc.).
    description: short text to explain what this topic covers.
    workflow_factory: function/class that returns a workflow instance.
    domain: optional logical domain (e.g. 'cs', 'finance', 'consumer', etc.)
    """

    key: str
    label: str
    description: str
    workflow_factory: Callable[[], Any]
    domain: str = "tools"


TOPIC_CONFIGS: Dict[str, TopicConfig] = {
    # ------------------------------------------------------------------
    # 1) Core developer / infra / API / data topics
    # ------------------------------------------------------------------
    "developer_tools": TopicConfig(
        key="developer_tools",
        label="Developer Tools",
        description=(
            "IDEs, editors, debuggers, build tools, CI/CD, and developer productivity tooling."
        ),
        workflow_factory=DeveloperToolsWorkflow,
        domain="tools",
    ),
    "saas": TopicConfig(
        key="saas",
        label="SaaS Products",
        description=(
            "Hosted subscription software (B2B/B2C SaaS apps, CRM, helpdesk, collaboration tools, etc.)."
        ),
        workflow_factory=SaaSWorkflow,
        domain="tools",
    ),
    "api": TopicConfig(
        key="api",
        label="API Platforms",
        description=(
            "Platforms whose main product is an API/SDK: REST/GraphQL APIs, webhooks, API gateways, etc."
        ),
        workflow_factory=APIWorkflow,
        domain="tools",
    ),
    "ai_ml": TopicConfig(
        key="ai_ml",
        label="AI & ML Platforms",
        description=(
            "LLM providers, ML platforms, model hosting, vector DBs, embeddings, fine-tuning, and AI infrastructure."
        ),
        workflow_factory=AIWorkflow,
        domain="tools",
    ),
    "security": TopicConfig(
        key="security",
        label="Security & Identity",
        description=(
            "Auth, identity, IAM, SSO, OAuth/OIDC, MFA, zero trust, WAF, bot/fraud detection, and security tooling."
        ),
        workflow_factory=SecurityWorkflow,
        domain="tools",
    ),
    "cloud": TopicConfig(
        key="cloud",
        label="Cloud & Infrastructure",
        description=(
            "Cloud providers and infrastructure: compute, storage, networking, serverless, managed Kubernetes, etc."
        ),
        workflow_factory=CloudWorkflow,
        domain="tools",
    ),
    "database": TopicConfig(
        key="database",
        label="Databases & Data Platforms",
        description=(
            "SQL/NoSQL databases, data warehouses, OLTP/OLAP engines, and managed database services."
        ),
        workflow_factory=DatabaseWorkflow,
        domain="tools",
    ),

    # ------------------------------------------------------------------
    # 2) Broader consumer / product categories
    # ------------------------------------------------------------------
    "consumer_and_social": TopicConfig(
        key="consumer_and_social",
        label="Consumer & Social Apps",
        description=(
            "Consumer-facing apps such as dating apps, social networks, ride-hailing companions, "
            "and lifestyle services (e.g. Tinder, Instagram-style products)."
        ),
        workflow_factory=ConsumerAndSocialWorkflow,
        domain="consumer",
    ),
    "content_and_website": TopicConfig(
        key="content_and_website",
        label="Content & Website Platforms",
        description=(
            "Content management systems, blogging platforms, website builders, and tools for hosting "
            "or publishing online content."
        ),
        workflow_factory=ContentAndWebsiteWorkflow,
        domain="consumer",
    ),
    "design": TopicConfig(
        key="design",
        label="Design & Creative Tools",
        description=(
            "UI/UX design tools, graphic design platforms, prototyping tools, and collaborative design systems "
            "(e.g. Figma-like products)."
        ),
        workflow_factory=DesignWorkflow,
        domain="creative",
    ),
    "e_commerce": TopicConfig(
        key="e_commerce",
        label="E-Commerce & Online Stores",
        description=(
            "E-commerce platforms, shopping carts, online marketplaces, and retail tooling for selling products "
            "and services online."
        ),
        workflow_factory=EcommerceWorkflow,
        domain="commerce",
    ),
    "file_storage": TopicConfig(
        key="file_storage",
        label="File Storage & Sync",
        description=(
            "Cloud storage, file synchronization/sharing tools, backup solutions, and team file collaboration "
            "platforms (e.g. Dropbox-style services)."
        ),
        workflow_factory=FileStorageWorkflow,
        domain="tools",
    ),
    "messaging": TopicConfig(
        key="messaging",
        label="Messaging & Communication",
        description=(
            "Messaging apps and communication platforms: chat apps, team messaging, email-like tools, "
            "and real-time collaboration (e.g. WhatsApp, Slack-style tools)."
        ),
        workflow_factory=MessagingWorkflow,
        domain="communication",
    ),
    "productivity": TopicConfig(
        key="productivity",
        label="Productivity & Organization",
        description=(
            "Note-taking apps, personal/task management tools, knowledge bases, and productivity suites "
            "(e.g. Notion, Evernote, Todoist)."
        ),
        workflow_factory=ProductivityWorkflow,
        domain="productivity",
    ),
    "transportation": TopicConfig(
        key="transportation",
        label="Transportation & Mobility",
        description=(
            "Ride-share, taxi-hailing, micromobility, and transportation apps/platforms (e.g. Uber, Lyft, "
            "scooter/bike-sharing apps)."
        ),
        workflow_factory=TransportationWorkflow,
        domain="consumer",
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
