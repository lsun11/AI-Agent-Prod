# src/topics/security/base_models.py
from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class SecurityCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model specialized for security / auth / identity providers:
    - SSO
    - IAM
    - bot/fraud detection
    - security monitoring, etc.
    """

    # What security domains it's focused on (e.g., "SSO", "IAM", "WAF", "bot protection")
    security_focus_areas: List[str] = Field(default_factory=list)

    # Compliance / certifications (e.g., "SOC2", "ISO27001", "HIPAA")
    compliance_certifications: List[str] = Field(default_factory=list)

    # Built-in MFA support (e.g., "TOTP", "SMS", "WebAuthn")
    mfa_methods_supported: List[str] = Field(default_factory=list)

    # Whether it includes risk-based or adaptive security features
    risk_based_auth: Optional[bool] = None


class SecurityCompanyInfo(BaseCompanyInfo):
    """
    Security / identity provider info model.
    Extends BaseCompanyInfo with security-centric metadata.
    """

    # Whether SSO/SAML is supported
    sso_supported: Optional[bool] = None

    # Whether directory sync (SCIM, LDAP, etc.) is available
    directory_sync_supported: Optional[bool] = None

    # Whether it provides audit logs / security event streaming
    audit_logs_available: Optional[bool] = None


class SecurityResearchState(BaseResearchState):
    """
    Research state for security/auth/identity service comparisons.
    """
    pass
