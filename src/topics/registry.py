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
from .tools.e_commerce.workflow import ECommerceWorkflow
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
            "IDEs, editors, debuggers, build tools, CI/CD, developer productivity tooling, "
            "version control clients, code review tools, and local dev environments. "
            "NOT for cloud platforms, databases, or generic SaaS products."
        ),
        workflow_factory=DeveloperToolsWorkflow,
        domain="tools",
    ),
    "saas": TopicConfig(
        key="saas",
        label="SaaS Products",
        description=(
            "Business / B2B SaaS products: CRM, ERP, helpdesk, HR, finance suites, "
            "marketing automation, analytics dashboards, and business operations platforms. "
            "Think Salesforce, HubSpot, Zendesk, Workday. "
            "NOT for consumer wallets or P2P payment apps (those go to E-Commerce & Fintech)."
        ),
        workflow_factory=SaaSWorkflow,
        domain="tools",
    ),
    "api": TopicConfig(
        key="api",
        label="API Platforms",
        description=(
            "Platforms whose main product is an API/SDK: REST / GraphQL APIs, webhooks, "
            "API gateways, developer platforms exposed primarily via API. "
            "Use for questions like 'Stripe API vs Braintree API' or 'Best SMS APIs'."
        ),
        workflow_factory=APIWorkflow,
        domain="tools",
    ),
    "ai_ml": TopicConfig(
        key="ai_ml",
        label="AI & ML Platforms",
        description=(
            "LLM providers, ML platforms, model hosting, vector DBs, embeddings, "
            "fine-tuning services, and AI infrastructure. "
            "Use for topics like OpenAI vs Anthropic, Pinecone vs Weaviate, MLops platforms, etc."
        ),
        workflow_factory=AIWorkflow,
        domain="tools",
    ),
    "security": TopicConfig(
        key="security",
        label="Security & Identity",
        description=(
            "Auth, identity, IAM, SSO, OAuth/OIDC, MFA, zero trust, WAF, bot/fraud detection, "
            "and security tooling. Examples: Auth0, Okta, Cloudflare Security, Snyk. "
            "NOT for generic cloud providers or payment wallets."
        ),
        workflow_factory=SecurityWorkflow,
        domain="tools",
    ),
    "cloud": TopicConfig(
        key="cloud",
        label="Cloud & Infrastructure",
        description=(
            "Cloud providers and infrastructure: compute, storage, networking, serverless, "
            "managed Kubernetes, and infra platforms (AWS, Azure, GCP, DigitalOcean, Fly.io, etc.). "
            "Also includes DevOps infra tools that are primarily about runtime/infra, not app-level SaaS."
        ),
        workflow_factory=CloudWorkflow,
        domain="tools",
    ),
    "database": TopicConfig(
        key="database",
        label="Databases & Data Platforms",
        description=(
            "SQL/NoSQL databases, data warehouses, OLTP/OLAP engines, data lakes, and managed database services. "
            "Use for questions like 'Postgres vs MySQL', 'Snowflake vs BigQuery', 'best time-series DBs'."
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
            "Consumer-facing apps whose primary purpose is social interaction, dating, content feeds, "
            "or lifestyle communities. Examples: Tinder, Bumble, Instagram, TikTok, X/Twitter, Reddit. "
            "NOT for payment / money-transfer apps (Venmo, Cash App, PayPal → E-Commerce & Fintech). "
            "NOT for pure messaging/chat tools (WhatsApp, Telegram, Slack → Messaging & Communication)."
        ),
        workflow_factory=ConsumerAndSocialWorkflow,
        domain="consumer",
    ),
    "content_and_website": TopicConfig(
        key="content_and_website",
        label="Content & Website Platforms",
        description=(
            'Content management systems, blogging platforms, website builders, and publishing tools. '
            "Examples: WordPress, Ghost, Wix, Squarespace, Webflow, Medium-like platforms."
        ),
        workflow_factory=ContentAndWebsiteWorkflow,
        domain="consumer",
    ),
    "design": TopicConfig(
        key="design",
        label="Design & Creative Tools",
        description=(
            "UI/UX design tools, graphic design platforms, prototyping tools, and creative software. "
            "Examples: Figma, Sketch, Adobe XD, Photoshop, Illustrator, Canva. "
            "Use for design tooling, creative workflows, and collaborative design systems."
        ),
        workflow_factory=DesignWorkflow,
        domain="creative",
    ),
    "e_commerce": TopicConfig(
        key="e_commerce",
        label="E-Commerce & Fintech / Payments",
        description=(
            "E-commerce platforms, online store builders, checkout systems, and **consumer or business "
            "payment tools**. This includes payment processors, wallets, and P2P money transfer apps. "
            "Examples: Shopify, WooCommerce, Stripe, Adyen, Braintree, PayPal, Venmo, Cash App, Klarna. "
            "Use this for anything primarily about **paying, getting paid, checkout, or online selling**, "
            "even if the app has a social feed (e.g. Venmo)."
        ),
        workflow_factory=ECommerceWorkflow,
        domain="commerce",
    ),
    "file_storage": TopicConfig(
        key="file_storage",
        label="File Storage & Sync",
        description=(
            "Cloud storage, file synchronization and sharing tools, backup solutions, and team file "
            "collaboration platforms. Examples: Dropbox, Google Drive, OneDrive, Box, iCloud Drive. "
            "Use when the main focus is storing/syncing files, not general productivity or messaging."
        ),
        workflow_factory=FileStorageWorkflow,
        domain="tools",
    ),
    "messaging": TopicConfig(
        key="messaging",
        label="Messaging & Communication",
        description=(
            "Messaging apps and communication platforms: chat apps, team messaging, email-like tools, "
            "and real-time collaboration. Examples: WhatsApp, Telegram, Signal, Slack, Microsoft Teams, "
            "Discord. Use when the primary purpose is **communication**, not social feed or payments."
        ),
        workflow_factory=MessagingWorkflow,
        domain="communication",
    ),
    "productivity": TopicConfig(
        key="productivity",
        label="Productivity & Organization",
        description=(
            "Note-taking apps, personal task managers, knowledge bases, calendars, and productivity suites. "
            "Examples: Notion, Evernote, Todoist, Obsidian, Roam, ClickUp (solo/team productivity angle). "
            "Use when the core purpose is organizing work or personal information, not primarily messaging or sales."
        ),
        workflow_factory=ProductivityWorkflow,
        domain="productivity",
    ),
    "transportation": TopicConfig(
        key="transportation",
        label="Transportation & Mobility",
        description=(
            "Ride-share, taxi-hailing, micromobility, delivery-as-transport, and mobility apps/platforms. "
            "Examples: Uber, Lyft, Bolt, Didi, Grab, scooter/bike-sharing apps. "
            "Use for queries like 'Uber alternatives', 'best ride-share apps in Europe', etc. "
            "NOT for pure payment or wallet apps (those belong to E-Commerce & Fintech)."
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
