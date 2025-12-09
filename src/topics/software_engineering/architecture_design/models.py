from ..base_models import (
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
    BaseSoftwareEngState,
)


class ArchitectureDesignResource(BaseSoftwareEngResourceSummary):
    # What you already had
    architectural_patterns: list[str] = []
    system_components: list[str] = []
    tradeoffs: list[str] = []

    # New: richer extraction so we can support more question types
    data_flow_patterns: list[str] = []          # e.g. CQRS, event-sourcing, ETL, CDC
    data_storage_patterns: list[str] = []       # SQL/NoSQL choices, partitioning, sharding, etc.
    integration_patterns: list[str] = []        # API gateway, BFF, messaging, webhooks, etc.
    deployment_models: list[str] = []           # k8s, serverless, monolith, on-prem, hybrid cloud
    scaling_strategies: list[str] = []          # horizontal/vertical scaling, caching, queues
    reliability_practices: list[str] = []       # retries, circuit breakers, SLOs, DR, etc.
    security_and_compliance: list[str] = []     # authN/Z, PII/PHI, GDPR/HIPAA, network isolation
    performance_bottlenecks: list[str] = []     # hotspots, shared DB, chatty services, etc.
    cost_considerations: list[str] = []         # infra cost, managed vs self-hosted, over-provisioning
    constraints_and_context: list[str] = []     # team size, tech stack, SLAs, legacy constraints


class ArchitectureDesignRecommendation(BaseSoftwareEngRecommendation):
    # Existing fields
    key_arch_decisions: list[str] = []
    scalability_considerations: list[str] = []
    reliability_strategies: list[str] = []

    # New high-level “what kind of question is this?”
    question_type: str | None = None
    # e.g. "greenfield_design", "review_existing", "migration",
    #      "scalability_reliability", "cost_optimization", "comparison"

    # New: structure your answers more explicitly
    suggested_architecture_overview: list[str] = []       # high-level topology, patterns
    component_and_boundary_guidance: list[str] = []       # service boundaries, BFFs, modules
    data_and_storage_guidance: list[str] = []             # DB choices, schema/partitioning tips
    integration_and_api_guidance: list[str] = []          # sync vs async, API gateway, events
    migration_or_refactor_plan: list[str] = []            # phased rollout, strangler fig, feature flags
    risk_and_tradeoff_notes: list[str] = []               # tech debt, complexity, failure modes
    observability_and_ops: list[str] = []                 # logs, metrics, traces, alerts
    cost_and_efficiency_tips: list[str] = []              # right-sizing, managed services, caching
    short_decision_summary: list[str] = []                # “pick X over Y because…”
    next_steps: list[str] = []                            # concrete steps user can take in ~1 week


class ArchitectureDesignState(BaseSoftwareEngState):
    resources: list[ArchitectureDesignResource] = []
    analysis: ArchitectureDesignRecommendation | None = None
