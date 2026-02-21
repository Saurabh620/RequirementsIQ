"""
Utility: Keyword-based domain classifier.
Detects the most likely industry domain from input text — no LLM call needed.
"""
import re
from collections import Counter

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "bfsi": [
        "bank", "banking", "loan", "credit", "debit", "insurance", "premium",
        "policy", "investment", "portfolio", "kyc", "aml", "neft", "rtgs",
        "swift", "ifsc", "ledger", "reconciliation", "treasury", "forex",
        "mutual fund", "broker", "compliance", "rbi", "sebi", "irdai",
        "nbfc", "fintech", "payment gateway", "upi", "emi", "mortgage"
    ],
    "healthcare": [
        "patient", "hospital", "doctor", "clinic", "diagnosis", "treatment",
        "ehr", "emr", "prescription", "pharmacy", "medical", "health record",
        "hipaa", "hl7", "fhir", "radiology", "lab report", "appointment",
        "telemedicine", "nursing", "ward", "discharge", "icd", "cpt",
        "insurance claim", "prior authorization", "provider", "payer"
    ],
    "saas": [
        "subscription", "tenant", "multi-tenant", "api", "dashboard",
        "onboarding", "billing", "stripe", "plan", "free tier", "pro tier",
        "webhook", "integration", "oauth", "sso", "saml", "workspace",
        "organization", "seat", "usage limit", "rate limit", "sdk",
        "marketplace", "app store", "churn", "mrr", "arr", "saas"
    ],
}


def classify_domain(text: str) -> str:
    """
    Returns the most likely domain: 'bfsi' | 'healthcare' | 'saas' | 'generic'.
    Uses keyword frequency analysis.
    """
    text_lower = text.lower()
    scores: Counter = Counter()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
            scores[domain] += count

    if not scores or scores.most_common(1)[0][1] == 0:
        return "generic"

    best_domain, best_score = scores.most_common(1)[0]

    # Require at least 2 keyword hits to confidently classify
    if best_score < 2:
        return "generic"

    return best_domain
