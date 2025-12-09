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


from .career.resume_tools.workflow import ResumeToolsWorkflow
from .career.job_search.workflow import JobSearchWorkflow
from .career.learning_platforms.workflow import LearningPlatformsWorkflow
from .career.coding_interview.workflow import CodingInterviewPlatformsWorkflow
from .career.system_design.workflow import SystemDesignPlatformsWorkflow
from .career.behavioral_interview.workflow import BehavioralInterviewToolsWorkflow

from .software_engineering.agile import AgileWorkflow
from .software_engineering.architecture_design.workflow import ArchitectureDesignWorkflow
from .software_engineering.cicd import CICDWorkflow
from .software_engineering.code_quality.workflow import CodeQualityWorkflow
# from .software_engineering.code_review.workflow import CodeReviewWorkflow
# from .software_engineering.productivity.workflow import ProductivityWorkflow
# from .software_engineering.project_management.workflow import ProjectManagementWorkflow
from .software_engineering.testing.workflow import TestingWorkflow

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
            "Developer productivity tooling used primarily during local development and coding workflows. "
            "Includes IDEs, editors, debuggers, linters, build tools, local test runners, CI integration plugins, "
            "version control clients, code review / diff tools, and local dev environments like Docker Desktop. "
            "Typical questions: 'VS Code vs JetBrains for Python?', 'Best Git GUI for Mac?', "
            "'Tools to speed up code reviews?', 'What can I use to debug HTTP requests locally?'. "
            "Route here when the user is focused on how an individual developer writes, edits, debugs, tests, "
            "or reviews code on their own machine or in a small team dev workflow. "
            "Do NOT use this for questions about PRODUCTION infrastructure, cloud providers, "
            "hosted SaaS products for business operations, or system architecture questions."
        ),
        workflow_factory=DeveloperToolsWorkflow,
        domain="tools",
    ),
    "saas": TopicConfig(
        key="saas",
        label="SaaS Products",
        description=(
            "Business- or team-oriented SaaS products used to run operations, manage workflows, or support teams. "
            "Includes CRM, ERP, helpdesk, HR & recruiting suites, finance systems, marketing automation, "
            "analytics dashboards, project/portfolio management platforms, and other business process tools. "
            "Examples: Salesforce, HubSpot, Zendesk, Workday, Jira (as business project tracking), Asana, Monday.com. "
            "Typical questions: 'Alternatives to Salesforce for SMBs?', 'Best SaaS for customer support?', "
            "'Which marketing automation platforms integrate well with HubSpot?'. "
            "Use this when the focus is on a hosted SaaS product that primarily supports business workflows, "
            "sales, operations, or organizational processes. "
            "Do NOT use this for consumer apps, payment/checkout products (→ E-Commerce & Fintech), "
            "or dev/infra platforms that are mainly APIs or cloud providers."
        ),
        workflow_factory=SaaSWorkflow,
        domain="tools",
    ),
    "api": TopicConfig(
        key="api",
        label="API Platforms",
        description=(
            "Platforms whose MAIN product is an API, SDK, or webhook-based integration. "
            "Includes payment APIs, SMS / email APIs, authentication APIs, search APIs, maps/geo APIs, "
            "embedding/vector APIs, and other programmable services consumed directly by developers. "
            "Examples: Stripe API, Twilio, SendGrid, Algolia, Mapbox, Clerk, Supabase Auth. "
            "Typical questions: 'Stripe vs Braintree for payments?', 'Best SMS APIs for global coverage?', "
            "'Good APIs for address validation?', 'Which email API works best with Node?'. "
            "Route here when the user is focused on integrating a PROGRAMMABLE API into their own system/app. "
            "If the question is more about general SaaS usage by non-developers, use SaaS Products instead. "
            "If the question is about complete cloud providers (AWS, GCP) or infrastructure, use Cloud & Infrastructure."
        ),
        workflow_factory=APIWorkflow,
        domain="tools",
    ),
    "ai_ml": TopicConfig(
        key="ai_ml",
        label="AI & ML Platforms",
        description=(
            "AI- and ML-focused platforms, tools, and infrastructure. Includes LLM providers, model hosting, "
            "fine-tuning services, vector databases, feature stores, ML experiment tracking, and MLOps platforms. "
            "Examples: OpenAI, Anthropic, Cohere, Vertex AI, SageMaker, Hugging Face Hub, Pinecone, Weaviate, "
            "Qdrant, LangChain-based platforms, and MLops tools like MLflow. "
            "Typical questions: 'OpenAI vs Anthropic for chatbots?', 'Best vector DB for semantic search?', "
            "'How does Pinecone compare to Weaviate?', 'Platforms to host custom fine-tuned models?'. "
            "Use this when the user is specifically focused on AI/ML capabilities, model lifecycle, embeddings, "
            "vector search, or training/inference infrastructure. "
            "Do NOT use this for generic analytics dashboards or BI tools (→ SaaS Products) "
            "or for standard databases without AI-specific context (→ Databases & Data Platforms)."
        ),
        workflow_factory=AIWorkflow,
        domain="tools",
    ),
    "security": TopicConfig(
        key="security",
        label="Security & Identity",
        description=(
            "Security-, auth-, and identity-focused platforms and tools. "
            "Includes authentication/authorization providers, IAM, SSO, OAuth/OIDC, MFA, PAM, zero-trust systems, "
            "WAFs, DDoS protection, bot/fraud detection, SAST/DAST, dependency scanning, and general security tooling. "
            "Examples: Auth0, Okta, Azure AD, Cloudflare Security, Snyk, Dependabot, Prisma Cloud, Datadog Security. "
            "Typical questions: 'Auth0 vs Okta?', 'How to choose an SSO provider?', "
            "'Tools to scan dependencies for vulnerabilities?', 'Best WAF for small SaaS startup?'. "
            "Route here when the main concern is identity, authentication, access control, or security posture. "
            "Do NOT use this for pure payment platforms (→ E-Commerce & Fintech) or general cloud providers "
            "unless the question is explicitly about their security products."
        ),
        workflow_factory=SecurityWorkflow,
        domain="tools",
    ),
    "cloud": TopicConfig(
        key="cloud",
        label="Cloud & Infrastructure",
        description=(
            "Cloud providers and infrastructure platforms used to run applications and services in production. "
            "Includes compute (VMs, containers, serverless), storage (object, block, file), networking, "
            "managed Kubernetes, container orchestration, load balancers, observability/monitoring, and infra-as-code. "
            "Examples: AWS, Azure, GCP, DigitalOcean, Render, Fly.io, Heroku, Vercel, Netlify (deployment angle), "
            "Kubernetes platforms, Terraform Cloud, Pulumi, observability stacks like Datadog/New Relic (infra focus). "
            "Typical questions: 'AWS vs GCP for a small startup?', 'Best platform to host a containerized app?', "
            "'Render vs Fly.io vs Railway?', 'Should I use serverless or Kubernetes for this workload?'. "
            "Use this when the user is focused on DEPLOYMENT, SCALING, runtime infrastructure, or production hosting. "
            "Do NOT use this for local developer tooling (→ Developer Tools) or for pure business SaaS apps (→ SaaS Products)."
        ),
        workflow_factory=CloudWorkflow,
        domain="tools",
    ),
    "database": TopicConfig(
        key="database",
        label="Databases & Data Platforms",
        description=(
            "Databases and data platforms for storing, querying, and analyzing data. "
            "Includes OLTP databases, OLAP/data warehouses, time-series DBs, key-value stores, search engines, "
            "data lakes, lakehouses, and managed database services. "
            "Examples: Postgres, MySQL, MariaDB, SQL Server, Oracle, MongoDB, Redis, Cassandra, DynamoDB, "
            "Elasticsearch/OpenSearch, ClickHouse, Snowflake, BigQuery, Redshift, Databricks. "
            "Typical questions: 'Postgres vs MySQL for a fintech app?', 'Snowflake vs BigQuery?', "
            "'Best time-series DB for monitoring metrics?', 'How to choose between MongoDB and DynamoDB?'. "
            "Route here when the focus is on data storage/query engines, indexing strategies, database ecosystems, "
            "and trade-offs between different DB technologies. "
            "Do NOT use this for vector DBs used primarily for embeddings (→ AI & ML Platforms) "
            "or for generic file storage/sync (→ File Storage & Sync)."
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
            "Consumer-facing apps whose primary purpose is social interaction, dating, entertainment, "
            "short-form content feeds, or lifestyle communities. "
            "Examples: Tinder, Bumble, Hinge, Instagram, TikTok, Snapchat, X/Twitter, Reddit, BeReal. "
            "Typical questions: 'Alternatives to Tinder?', 'Which apps are best for hobby communities?', "
            "'Social apps where I can share short videos?'. "
            "Use this when the main user goal is social interaction, discovery, or entertainment. "
            "Do NOT use this for payment apps (Venmo, Cash App → E-Commerce & Fintech) "
            "or pure messaging/chat tools without content feeds (WhatsApp, Telegram → Messaging & Communication)."
        ),
        workflow_factory=ConsumerAndSocialWorkflow,
        domain="tools",
    ),
    "content_and_website": TopicConfig(
        key="content_and_website",
        label="Content & Website Platforms",
        description=(
            "Tools and platforms focused on content publishing and website creation. "
            "Includes CMSs, blogging engines, static site generators (hosted products), "
            "website builders, landing page builders, and hosted publishing platforms. "
            "Examples: WordPress.com, Ghost(Pro), Wix, Squarespace, Webflow, Medium-like platforms, "
            "Carrd, Framer (website angle). "
            "Typical questions: 'Webflow vs Squarespace for a portfolio?', 'Alternatives to WordPress for blogging?', "
            "'Best platform to build a marketing site without coding?'. "
            "Route here when the main goal is publishing content or building marketing/personal sites. "
            "Do NOT use this for dev-focused static site build tools (e.g. Hugo CLI) unless user is clearly treating "
            "them as hosted website platforms for non-devs."
        ),
        workflow_factory=ContentAndWebsiteWorkflow,
        domain="tools",
    ),
    "design": TopicConfig(
        key="design",
        label="Design & Creative Tools",
        description=(
            "Visual design, UI/UX, prototyping, and creative content tools. "
            "Includes vector graphics, raster graphics, UI design tools, design systems, prototyping, motion design, "
            "and lightweight design platforms used by product/design teams. "
            "Examples: Figma, Sketch, Adobe XD, Photoshop, Illustrator, Canva, Affinity Designer, Framer (design angle). "
            "Typical questions: 'Figma vs Sketch for team collaboration?', 'Best tools for social media graphics?', "
            "'How does Canva compare to Adobe Express?'. "
            "Use this when the primary activity is visual design, creative production, or prototyping UI flows."
        ),
        workflow_factory=DesignWorkflow,
        domain="tools",
    ),
    "e_commerce": TopicConfig(
        key="e_commerce",
        label="E-Commerce & Fintech / Payments",
        description=(
            "Platforms and tools primarily about selling, checkout, and payments (B2C or B2B). "
            "Includes e-commerce platforms, online store builders, checkout systems, subscription billing, "
            "payment processors, POS, wallets, BNPL, and P2P money transfer apps. "
            "Examples: Shopify, WooCommerce, BigCommerce, Stripe, Adyen, Braintree, PayPal, Venmo, Cash App, Klarna. "
            "Typical questions: 'Shopify vs WooCommerce?', 'Stripe vs PayPal for SaaS billing?', "
            "'Alternatives to Venmo for P2P payments?'. "
            "Route here whenever the main purpose is **paying, getting paid, or running a store/checkout**, "
            "even if the product has some social feed or messaging features. "
            "Do NOT use this for generic CRMs or business SaaS that are not primarily payment/checkout focused (→ SaaS Products)."
        ),
        workflow_factory=ECommerceWorkflow,
        domain="tools",
    ),
    "file_storage": TopicConfig(
        key="file_storage",
        label="File Storage & Sync",
        description=(
            "Cloud storage, file syncing, sharing, and backup tools. "
            "Includes personal and team file storage, collaboration via shared folders, and backup/archive services. "
            "Examples: Dropbox, Google Drive, OneDrive, Box, iCloud Drive, pCloud, Backblaze (backup angle). "
            "Typical questions: 'Dropbox vs Google Drive for a small team?', 'Alternatives to Box for enterprise?', "
            "'Best way to sync large media files across devices?'. "
            "Use this when the main focus is storing, syncing, backing up, or sharing files. "
            "Do NOT use this for knowledge-base style tools where structure/notes/tasks dominate (→ Productivity & Organization)."
        ),
        workflow_factory=FileStorageWorkflow,
        domain="tools",
    ),
    "messaging": TopicConfig(
        key="messaging",
        label="Messaging & Communication",
        description=(
            "Real-time communication and messaging platforms used by individuals or teams. "
            "Includes chat apps, team collaboration tools, community chat servers, and email-like messaging products. "
            "Examples: WhatsApp, Telegram, Signal, Slack, Microsoft Teams, Discord, Mattermost. "
            "Typical questions: 'Slack vs Teams?', 'Alternatives to WhatsApp for secure messaging?', "
            "'Which tools are best for hosting a developer community chat?'. "
            "Route here when the primary activity is communication (1:1 or group chat, channels, calls). "
            "Do NOT use this for social feed–heavy consumer apps (→ Consumer & Social Apps) "
            "or project/knowledge tools where messaging is secondary (→ Productivity & Organization)."
        ),
        workflow_factory=MessagingWorkflow,
        domain="tools",
    ),
    "productivity": TopicConfig(
        key="productivity",
        label="Productivity & Organization",
        description=(
            "Tools for personal or team productivity, knowledge management, planning, and organization. "
            "Includes note-taking apps, personal task managers, calendars, knowledge bases, "
            "kanban boards, lightweight project planners, and integrated productivity suites. "
            "Examples: Notion, Evernote, Obsidian, Roam, Todoist, Things, ClickUp (productivity angle), Asana (task angle). "
            "Typical questions: 'Notion vs Obsidian for personal knowledge management?', "
            "'Best apps for managing tasks across work and personal life?', "
            "'Alternatives to Trello for small teams?'. "
            "Use this when the focus is on organizing information, tasks, or projects rather than real-time chat "
            "(→ Messaging & Communication) or pure business ops SaaS (→ SaaS Products)."
        ),
        workflow_factory=ProductivityWorkflow,
        domain="tools",
    ),
    "transportation": TopicConfig(
        key="transportation",
        label="Transportation & Mobility",
        description=(
            "Apps and platforms that move people or goods in the physical world. "
            "Includes ride-sharing, taxi-hailing, micromobility (scooters, bikes), car-sharing, "
            "delivery-as-transport, and mobility services. "
            "Examples: Uber, Lyft, Bolt, Didi, Grab, FreeNow, Lime, Bird, Zipcar, Gojek. "
            "Typical questions: 'Uber alternatives in Europe?', 'Best scooter-sharing apps?', "
            "'Apps for car-sharing in big cities?'. "
            "Route here when the core value is transportation/mobility. "
            "Do NOT use this for pure payment wallets or banking apps (→ E-Commerce & Fintech)."
        ),
        workflow_factory=TransportationWorkflow,
        domain="tools",
    ),

    # ==== Career domain ====
    "resume_tools": TopicConfig(
        key="resume_tools",
        label="Resume Optimization & ATS Tools",
        description=(
            "Tools that help create, analyze, or optimize resumes/CVs for tech roles and ensure they pass ATS filters. "
            "Includes resume builders, ATS keyword checkers, job description matchers, and AI-based resume reviewers. "
            "Examples: Resume.io, Teal, Jobscan, standardresume.io, AI-based resume critique tools. "
            "Typical questions: 'Best tools to check my resume against a job description?', "
            "'Alternatives to Jobscan?', 'Where can I get an AI review of my resume?'. "
            "Use this when the user is focused on improving resume content/format or optimizing for ATS."
        ),
        workflow_factory=ResumeToolsWorkflow,
        domain="career",
    ),
    "job_search": TopicConfig(
        key="job_search",
        label="Job Search Platforms & Market Analysis",
        description=(
            "Job boards and platforms for finding roles, plus tools that provide market/salary insights. "
            "Includes general job sites, tech-focused job boards, remote work platforms, and compensation data tools. "
            "Examples: LinkedIn Jobs, Indeed, Glassdoor, Levels.fyi, Hired, Wellfound (AngelList Talent), Otta. "
            "Typical questions: 'Best sites for remote software engineer jobs?', "
            "'Alternatives to LinkedIn Jobs?', 'Where can I see salary bands for FAANG-like companies?'. "
            "Use this when the focus is discovering job opportunities or understanding the job market, "
            "not on skill-building or interview practice."
        ),
        workflow_factory=JobSearchWorkflow,
        domain="career",
    ),
    "learning_platform": TopicConfig(
        key="learning_platform",
        label="Learning Platforms & Skill Roadmaps",
        description=(
            "Online platforms and resources for learning programming, data, devops, or other technical skills, "
            "plus high-level skill roadmaps and curricula. "
            "Includes MOOC platforms, bootcamps, course marketplaces, curated learning paths, and structured curricula. "
            "Examples: Coursera, edX, Udemy, Pluralsight, Frontend Masters, LeetCode (learning side), "
            "Bootcamps like App Academy or Lambda School, roadmap.sh (conceptually). "
            "Typical questions: 'Best platform to learn Go as a backend engineer?', "
            "'How to build a learning path for ML?', 'Alternatives to Udemy for deep backend courses?'. "
            "Use this when the user is focused on learning resources/paths rather than immediate job search "
            "or interview practice for a specific process."
        ),
        workflow_factory=LearningPlatformsWorkflow,
        domain="career",
    ),
    "coding_interview": TopicConfig(
        key="coding_interview",
        label="Coding Interview Platforms",
        description=(
            "Platforms specifically focused on coding interview practice, coding challenges, and mock interviews. "
            "Includes algorithmic problem sites, online judges, and coding-interview prep tools. "
            "Examples: LeetCode, HackerRank, CodeSignal, Codility, AlgoExpert. "
            "Typical questions: 'LeetCode vs HackerRank?', 'Best platforms to practice coding interviews?', "
            "'Where can I simulate timed coding interviews?'. "
            "Use this when the user is clearly talking about coding interview preparation or coding challenges. "
            "If the question is about general learning courses, route to Learning Platforms & Skill Roadmaps instead."
        ),
        workflow_factory=CodingInterviewPlatformsWorkflow,
        domain="career",
    ),
    "system_design": TopicConfig(
        key="system_design",
        label="System Design Interview Platforms",
        description=(
            "Platforms and resources that help candidates prepare for SYSTEM DESIGN INTERVIEWS, "
            "mock interviews, and interview-style system design practice. "
            "Examples: Exponent, Educative.io system design courses, ByteByteGo, Grokking the System Design Interview. "
            "Typical questions: 'Best resources to prepare for system design interviews?', "
            "'ByteByteGo vs Grokking?', 'Where can I get mock system design interviews?'. "
            "IMPORTANT: This topic is about INTERVIEW PREPARATION, not actual real-world architecture for a running system. "
            "If the user asks things like 'How should I design a system that supports 10k rps with eventual consistency?', "
            "that is a real-world architecture question and should go to Architecture Design Suggestions instead."
        ),
        workflow_factory=SystemDesignPlatformsWorkflow,
        domain="career",
    ),
    "behavioral_interview": TopicConfig(
        key="behavioral_interview",
        label="Behavioral Interview & Coaching Tools",
        description=(
            "Tools and platforms that help candidates prepare for behavioral interviews, soft skills, "
            "and career coaching. Includes behavioral question banks, mock interview platforms, "
            "AI-based behavioral interview coaches, and general tech career coaching tools. "
            "Examples: interview coaching platforms, Pramp (behavioral side), AI practice apps for soft skills. "
            "Typical questions: 'Apps to practice behavioral interview questions?', "
            "'Tools that help me improve my STAR stories?', "
            "'Where can I get coaching for senior engineer interviews?'. "
            "Use this when the focus is on behavioral/soft-skills preparation, not technical or coding questions."
        ),
        workflow_factory=BehavioralInterviewToolsWorkflow,
        domain="career",
    ),

    # ==== Software engineering domain ====
    "architecture_design": TopicConfig(
        key="architecture_design",
        label="Architecture Design Suggestions",
        description=(
            "Real-world software architecture and system design guidance for building or evolving systems. "
            "Includes questions about microservices vs monoliths, event-driven vs request/response, "
            "synchronous vs asynchronous flows, scalability patterns, consistency models, and reliability strategies. "
            "Examples of queries: 'How should I design a system that supports 10k RPS with eventual consistency?', "
            "'Should I use CQRS and event sourcing for this domain?', "
            "'How do I design a multi-tenant SaaS architecture?', "
            "'What architecture works for a real-time chat app at scale?'. "
            "IMPORTANT: Route here when the user is designing or improving a system's architecture in a real environment. "
            "If the question is specifically about which INTERVIEW PREP resources to use, "
            "send it to System Design Interview Platforms instead."
        ),
        workflow_factory=ArchitectureDesignWorkflow,
        domain="software_engineering",
    ),
    "code_quality": TopicConfig(
        key="code_quality",
        label="Code Quality Suggestions",
        description=(
            "Improving code quality in existing or new codebases. "
            "Includes refactoring strategies, enforcing coding standards, static analysis, linters, "
            "code smells, technical debt management, and patterns for writing maintainable, testable code. "
            "Typical questions: 'How can I improve the quality of a legacy Python codebase?', "
            "'What tools should I use for static analysis in TypeScript?', "
            "'How do I reduce code duplication and improve readability?', "
            "'How to introduce code style checks (Prettier/ESLint) into an existing project?'. "
            "Use this when the focus is on code correctness, maintainability, clarity, and best practices at the code level."
        ),
        workflow_factory=CodeQualityWorkflow,
        domain="software_engineering",
    ),
    "testing": TopicConfig(
        key="testing",
        label="Testing",
        description=(
            "Testing strategies, tools, and frameworks across unit, integration, E2E, performance, and reliability tests. "
            "Includes test frameworks, test runners, mocking/stubbing libraries, coverage tools, and design of test suites. "
            "Examples: Jest, Vitest, JUnit, pytest, Cypress, Playwright, Selenium, k6, Locust. "
            "Typical questions: 'How should I structure my test suite for a React app?', "
            "'Jest vs Vitest?', 'Best way to test async workflows?', "
            "'How can I introduce E2E tests into a legacy system?'. "
            "Route here when the user is focused on testing strategy, test tooling, or improving test coverage and reliability."
        ),
        workflow_factory=TestingWorkflow,
        domain="software_engineering",
    ),
    "agile": TopicConfig(
        key="agile",
        label="Agile Tools",
        description=(
            "Agile / Scrum / Kanban practices and the tools that support them. "
            "Includes sprint planning tools, backlog management, story tracking, burndown charts, and agile workflows. "
            "Examples: Jira (agile workflows), Trello, Clubhouse/Shortcut, Azure DevOps Boards, Linear. "
            "Typical questions: 'Tools that work well for Scrum teams?', "
            "'How to manage a Kanban board for an ops team?', "
            "'Alternatives to Jira for agile project management?'. "
            "Use this when the focus is on process, iteration, and agile team coordination rather than pure task management "
            "for individuals (→ Productivity & Organization)."
        ),
        workflow_factory=AgileWorkflow,
        domain="software_engineering",
    ),
    "cicd": TopicConfig(
        key="cicd",
        label="CICD Tools",
        description=(
            "Continuous Integration and Continuous Delivery/Deployment tooling and practices. "
            "Includes CI pipelines, build servers, deployment automation, artifact repositories, "
            "and release orchestration platforms. "
            "Examples: GitHub Actions, GitLab CI, CircleCI, Jenkins, Argo CD, Spinnaker, Travis CI. "
            "Typical questions: 'GitHub Actions vs GitLab CI?', 'How to design a CI/CD pipeline for a monorepo?', "
            "'Best tools to manage blue-green or canary deployments?', "
            "'How do I set up CI for a Python/Node mixed repo?'. "
            "Route here when the core concern is automating build/test/deploy workflows and release pipelines."
        ),
        workflow_factory=CICDWorkflow,
        domain="software_engineering",
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
