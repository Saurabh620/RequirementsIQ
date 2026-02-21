"""
AI Chain: FRD Generator
Produces structured Functional Requirements Document JSON.
"""
import json
import time
from pydantic import BaseModel, ValidationError
from typing import Optional
from config import settings
from ai.llm_client import get_llm_client, get_model_name

PROMPT_VERSION = "frd_v1"

SYSTEM_PROMPT = """\
You are a senior Business Analyst creating a Functional Requirements Document (FRD).
Analyze the input and generate a complete, numbered FRD.

{domain_context}

OUTPUT RULES:
- Respond ONLY with valid JSON matching the schema below.
- Use "INSUFFICIENT_DATA" if a section cannot be determined.
- Number functional requirements as FR-001, FR-002, etc.
- Number non-functional requirements as NFR-001, NFR-002, etc.

JSON SCHEMA:
{{
  "system_overview": {{"content": "string", "confidence": "high|medium|low"}},
  "functional_requirements": [
    {{"id": "FR-001", "title": "string", "description": "string",
      "priority": "Must|Should|Could|Won't", "business_rule": "string|null"}}
  ],
  "data_requirements": [{{"entity": "string", "attributes": ["string"], "notes": "string"}}],
  "error_handling": [{{"scenario": "string", "expected_behavior": "string"}}],
  "integration_points": [{{"system": "string", "type": "string", "description": "string"}}],
  "non_functional_requirements": [
    {{"id": "NFR-001", "category": "Performance|Security|Scalability|Availability|Reliability|Usability",
      "requirement": "string", "metric": "string|null"}}
  ],
  "overall_confidence": "high|medium|low"
}}"""

USER_PROMPT = """\
Analyze the following input and generate the FRD JSON:
---
{input_text}
---"""


class FRItem(BaseModel):
    id: str
    title: str
    description: str
    priority: str = "Should"
    business_rule: Optional[str] = None


class DataRequirement(BaseModel):
    entity: str
    attributes: list[str]
    notes: str = ""


class ErrorHandling(BaseModel):
    scenario: str
    expected_behavior: str


class IntegrationPoint(BaseModel):
    system: str
    type: str
    description: str


class NFRItem(BaseModel):
    id: str
    category: str
    requirement: str
    metric: Optional[str] = None


class SystemOverview(BaseModel):
    content: str
    confidence: str = "medium"


class FRDOutput(BaseModel):
    system_overview: SystemOverview
    functional_requirements: list[FRItem]
    data_requirements: list[DataRequirement]
    error_handling: list[ErrorHandling]
    integration_points: list[IntegrationPoint]
    non_functional_requirements: list[NFRItem]
    overall_confidence: str = "medium"


def run(
    input_text: str,
    domain: str,
    domain_context: str,
    token_log: Optional[list] = None
) -> tuple[Optional[FRDOutput], dict]:
    client = get_llm_client()
    model  = get_model_name()
    metadata = {"chain": "frd", "prompt_version": PROMPT_VERSION,
                "tokens_used": 0, "latency_ms": 0, "status": "success", "error": None}
    system = SYSTEM_PROMPT.format(domain_context=domain_context)
    user = USER_PROMPT.format(input_text=input_text[:15000])
    extra_instruction = ""

    for attempt in range(settings.ai_max_retries + 1):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model,
                temperature=settings.ai_temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user + extra_instruction}
                ],
                max_tokens=settings.ai_max_tokens_output,
                timeout=settings.ai_timeout_seconds,
            )
            latency_ms = int((time.time() - start) * 1000)
            raw_json = response.choices[0].message.content
            usage = response.usage
            metadata["tokens_used"] = usage.total_tokens
            metadata["latency_ms"] = latency_ms

            parsed = FRDOutput.model_validate(json.loads(raw_json))
            if token_log is not None:
                token_log.append({"chain": "frd", "input": usage.prompt_tokens,
                                  "output": usage.completion_tokens, "total": usage.total_tokens})
            return parsed, metadata

        except ValidationError as e:
            extra_instruction = f"\n\nSchema error: {str(e)[:200]}. Fix and return valid JSON only."
            metadata["status"] = "retry"
            if attempt == settings.ai_max_retries:
                metadata["status"] = "error"
                metadata["error"] = f"Validation failed after {attempt+1} attempts"
                return None, metadata
        except Exception as e:
            metadata["status"] = "error"
            metadata["error"] = str(e)
            return None, metadata

    return None, metadata
