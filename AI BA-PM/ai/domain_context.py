"""
AI Layer: Domain Context Injector
Provides domain-specific system context strings for prompt injection.
"""

DOMAIN_CONTEXTS: dict[str, str] = {
    "bfsi": """
DOMAIN CONTEXT — BFSI (Banking, Financial Services, Insurance):
- Regulatory compliance requirements: RBI, SEBI, IRDAI guidelines must be surfaced
- Mandatory: audit trails, data sovereignty, PII protection
- Common integrations: Core Banking Systems (CBS), SWIFT, payment gateways, UPI
- Always flag: missing KYC/AML flows, missing regulatory approval workflows
- Security: encryption at rest and in transit is non-negotiable in this domain
- Risk: Compliance risk and data privacy risk are automatically HIGH severity
""".strip(),

    "healthcare": """
DOMAIN CONTEXT — Healthcare IT:
- HIPAA compliance is mandatory; flag any missing privacy controls as HIGH severity gaps
- HL7/FHIR integration standards apply if EHR/EMR systems are mentioned
- Patient data de-identification is a regulatory requirement, not optional
- Audit logging of all PHI (Protected Health Information) access is mandatory
- Disaster recovery: RTO/RPO must be explicitly defined for clinical systems
- Always flag: missing consent management, missing data retention policy
""".strip(),

    "saas": """
DOMAIN CONTEXT — SaaS Product:
- Multi-tenancy and data isolation are core architectural requirements
- Subscription lifecycle must be covered: trial, activation, upgrade, downgrade, churn
- API rate limiting and webhook infrastructure are standard expectations
- SSO/SAML integration is expected by enterprise customers; flag if missing
- GDPR/data residency requirements must be surfaced for EU market products
- Always flag: missing admin role, missing audit log, missing data export capability
""".strip(),

    "generic": """
DOMAIN CONTEXT — General Software Project:
- Apply standard software engineering best practices
- Flag missing security requirements, performance criteria, and admin workflows
- Ensure authentication, authorization, and session management are covered
- Data backup and recovery requirements should be stated
""".strip(),
}


def get_domain_context(domain: str) -> str:
    """Return the domain-specific context string for prompt injection."""
    return DOMAIN_CONTEXTS.get(domain.lower(), DOMAIN_CONTEXTS["generic"])
