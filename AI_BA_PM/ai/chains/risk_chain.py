"""
AI Chain: Risk Engine
Generates a structured risk register across 6 risk categories.
"""
import json
import time
from pydantic import BaseModel, ValidationError
from typing import Optional
from config import settings
from ai.llm_client import get_llm_client, get_model_name

PROMPT_VERSION = "risk_v1"

SYSTEM_PROMPT = """\
You are a technical risk assessor for software projects in the {domain} domain.
Analyze the requirements and generate a comprehensive risk register.

Evaluate risks across these 6 categories:
1. Technical — Architecture complexity, technology choices, integrations
2. Dependency — Third-party services, vendor lock-in, external APIs
3. Compliance — Regulatory, legal, audit requirements
4. DataPrivacy — PII handling, GDPR, data breach exposure
5. Integration — System integration complexity, API failures
6. Timeline — Scope creep, estimation accuracy, resource gaps

PROBABILITY and IMPACT scale: H (High), M (Medium), L (Low)
Risk Score = Probability × Impact (HH = Critical, HM/MH = High, MM = Medium, LM/ML/LL = Low)

OUTPUT RULES:
- Respond ONLY with valid JSON matching the schema below.
- Be specific to the requirements provided, not generic.
- Mitigation_strategy must be actionable.

JSON SCHEMA:
{{
  "risks": [
    {{
      "category": "Technical|Dependency|Compliance|DataPrivacy|Integration|Timeline",
      "title": "string",
      "description": "string",
      "probability": "H|M|L",
      "impact": "H|M|L",
      "risk_score": "Critical|High|Medium|Low",
      "mitigation_strategy": "string"
    }}
  ]
}}"""

USER_PROMPT = """\
Domain: {domain}
Requirements context:
{requirements_summary}

Generate risk register JSON:"""


class Risk(BaseModel):
    category: str
    title: str
    description: str
    probability: str
    impact: str
    risk_score: str
    mitigation_strategy: str


class RiskOutput(BaseModel):
    risks: list[Risk]


def run(
    raw_input: str,
    domain: str,
    generated_doc_summary: str,
    token_log: Optional[list] = None
) -> tuple[Optional[RiskOutput], dict]:
    client = get_llm_client()
    model  = get_model_name()
    metadata = {"chain": "risk", "prompt_version": PROMPT_VERSION,
                "tokens_used": 0, "latency_ms": 0, "status": "success", "error": None}

    req_summary = (raw_input[:2000] + "\n\n" + generated_doc_summary[:1500]).strip()
    system = SYSTEM_PROMPT.format(domain=domain)
    user = USER_PROMPT.format(domain=domain, requirements_summary=req_summary)
    extra_instruction = ""

    for attempt in range(settings.ai_max_retries + 1):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user + extra_instruction}
                ],
                max_tokens=2000,
                timeout=settings.ai_timeout_seconds,
            )
            latency_ms = int((time.time() - start) * 1000)
            raw_json = response.choices[0].message.content
            usage = response.usage
            metadata["tokens_used"] = usage.total_tokens
            metadata["latency_ms"] = latency_ms

            parsed = RiskOutput.model_validate(json.loads(raw_json))
            if token_log is not None:
                token_log.append({"chain": "risk", "input": usage.prompt_tokens,
                                  "output": usage.completion_tokens, "total": usage.total_tokens})
            return parsed, metadata

        except (ValidationError, json.JSONDecodeError) as e:
            extra_instruction = f"\n\nSchema error: {str(e)[:200]}. Return ONLY {{'risks': [...]}} JSON."
            metadata["status"] = "retry"
            if attempt == settings.ai_max_retries:
                metadata["status"] = "error"
                metadata["error"] = str(e)
                return None, metadata
        except Exception as e:
            metadata["status"] = "error"
            metadata["error"] = str(e)
            return None, metadata

    return None, metadata
