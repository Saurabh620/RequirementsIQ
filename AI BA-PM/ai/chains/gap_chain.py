"""
AI Chain: Gap Detection Engine
Detects 7 categories of missing requirements in the generated document.
"""
import json
import time
from pydantic import BaseModel, ValidationError
from typing import Optional
from config import settings
from ai.llm_client import get_llm_client, get_model_name

PROMPT_VERSION = "gap_v1"

GAP_TYPES = [
    "missing_stakeholders",
    "undefined_scope_boundaries",
    "missing_performance_criteria",
    "missing_security_requirements",
    "missing_edge_cases",
    "missing_admin_roles",
    "missing_data_retention_policy",
]

SYSTEM_PROMPT = """\
You are a requirements completeness auditor.
Analyze the original stakeholder input AND the generated BRD/FRD summary.
Identify missing or under-specified requirements across these 7 gap categories:

1. missing_stakeholders — Key people or teams not mentioned
2. undefined_scope_boundaries — What is in/out of scope is unclear
3. missing_performance_criteria — No SLAs, response times, or throughput defined
4. missing_security_requirements — Auth, authorization, encryption not specified
5. missing_edge_cases — Failure scenarios, boundary conditions not covered
6. missing_admin_roles — Admin/superuser workflows or back-office not defined
7. missing_data_retention_policy — Data storage duration, archival, deletion not mentioned

OUTPUT RULES:
- Respond ONLY with valid JSON matching the schema below.
- If no gaps in a category, omit it from results.
- Be specific and actionable in recommendations.

JSON SCHEMA:
{{
  "gaps": [
    {{
      "type": "one of the 7 categories above",
      "severity": "HIGH|MEDIUM|LOW",
      "description": "What is missing and why it matters",
      "recommendation": "Specific action to resolve this gap"
    }}
  ]
}}"""

USER_PROMPT = """\
ORIGINAL INPUT SUMMARY:
{raw_input_summary}

GENERATED DOCUMENT SUMMARY:
{generated_doc_summary}

Identify all gaps and return JSON:"""


class Gap(BaseModel):
    type: str
    severity: str
    description: str
    recommendation: str


class GapOutput(BaseModel):
    gaps: list[Gap]


def run(
    raw_input: str,
    generated_doc_summary: str,
    token_log: Optional[list] = None
) -> tuple[Optional[GapOutput], dict]:
    client = get_llm_client()
    model  = get_model_name()
    metadata = {"chain": "gap", "prompt_version": PROMPT_VERSION,
                "tokens_used": 0, "latency_ms": 0, "status": "success", "error": None}

    raw_summary = raw_input[:3000]
    doc_summary = generated_doc_summary[:3000]

    user = USER_PROMPT.format(raw_input_summary=raw_summary, generated_doc_summary=doc_summary)
    extra_instruction = ""

    for attempt in range(settings.ai_max_retries + 1):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,  # Lower for more consistent gap detection
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
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

            parsed = GapOutput.model_validate(json.loads(raw_json))
            if token_log is not None:
                token_log.append({"chain": "gap", "input": usage.prompt_tokens,
                                  "output": usage.completion_tokens, "total": usage.total_tokens})
            return parsed, metadata

        except (ValidationError, json.JSONDecodeError) as e:
            extra_instruction = f"\n\nSchema error: {str(e)[:200]}. Return ONLY {{'gaps': [...]}} JSON."
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
