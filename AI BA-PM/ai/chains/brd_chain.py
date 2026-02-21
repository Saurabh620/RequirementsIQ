"""
AI Chain: BRD Generator
Calls the active LLM provider with a structured prompt and validates the JSON output.
"""
import json
import time
from pydantic import BaseModel, ValidationError
from typing import Optional
from config import settings
from ai.llm_client import get_llm_client, get_model_name

SYSTEM_PROMPT = """\
You are a senior Business Analyst with 15+ years of experience in {domain}.
Analyze the stakeholder input provided and generate a complete Business Requirements Document (BRD) strictly following the exact Enterprise format requested.

{domain_context}

OUTPUT RULES:
- Respond ONLY with valid JSON matching the schema below. No markdown, no explanations.
- If a section cannot be determined from the input, use "INSUFFICIENT_DATA" as the value.
- Never invent stakeholder names, metrics, or technical specifications not present in the input.
- Mark fields with low confidence using "confidence": "low".

JSON SCHEMA:
{{
  "project_name": "string",
  "document_control": {{"version": "string", "prepared_by": "string", "reviewed_by": "string", "approved_by": "string", "date": "string", "status": "Draft | Review | Final"}},
  "executive_summary": {{"content": "string", "confidence": "high|medium|low"}},
  "business_objectives": ["string"],
  "success_criteria": ["string"],
  "problem_statement": {{"content": "string", "confidence": "high|medium|low"}},
  "scope_in": ["string"],
  "scope_out": ["string"],
  "stakeholders": [{{"name": "string", "role": "string", "responsibility": "string"}}],
  "business_requirements": [{{"id": "string", "description": "string", "priority": "High|Medium|Low"}}],
  "functional_requirements": [{{"id": "string", "description": "string", "priority": "High|Medium|Low"}}],
  "non_functional_requirements": {{"performance": "string", "security": "string", "scalability": "string", "availability": "string", "usability": "string"}},
  "assumptions": ["string"],
  "constraints": ["string"],
  "dependencies": ["string"],
  "risks": [{{"id": "string", "description": "string", "impact": "High|Medium|Low", "mitigation": "string"}}],
  "acceptance_criteria": ["string"],
  "timeline_milestones": [{{"phase": "string", "description": "string", "target_date": "string"}}],
  "overall_confidence": "high|medium|low"
}}"""

USER_PROMPT = """\
Analyze the following stakeholder input and generate the BRD JSON:
---
{input_text}
---"""


class BRDSection(BaseModel):
    content: str
    confidence: str = "medium"

class Stakeholder(BaseModel):
    name: str
    role: str
    responsibility: str

class BRDRequirement(BaseModel):
    id: str
    description: str
    priority: str

class BRDRisk(BaseModel):
    id: str
    description: str
    impact: str
    mitigation: str

class Milestone(BaseModel):
    phase: str
    description: str
    target_date: str

class BRDOutput(BaseModel):
    project_name: str
    document_control: dict
    executive_summary: BRDSection
    business_objectives: list[str]
    success_criteria: list[str]
    problem_statement: BRDSection
    scope_in: list[str]
    scope_out: list[str]
    stakeholders: list[Stakeholder]
    business_requirements: list[BRDRequirement]
    functional_requirements: list[BRDRequirement]
    non_functional_requirements: dict
    assumptions: list[str]
    constraints: list[str]
    dependencies: list[str]
    risks: list[BRDRisk]
    acceptance_criteria: list[str]
    timeline_milestones: list[Milestone]
    overall_confidence: str = "medium"


PROMPT_VERSION = "brd_v1"


def run(
    input_text: str,
    domain: str,
    domain_context: str,
    token_log: Optional[list] = None
) -> tuple[Optional[BRDOutput], dict]:
    """
    Run the BRD chain. Returns (BRDOutput | None, metadata_dict).
    Retries once on schema validation failure.
    """
    client = get_llm_client()
    model  = get_model_name()
    metadata = {"chain": "brd", "prompt_version": PROMPT_VERSION,
                "tokens_used": 0, "latency_ms": 0, "status": "success", "error": None}
    system = SYSTEM_PROMPT.format(domain=domain, domain_context=domain_context)
    user = USER_PROMPT.format(input_text=input_text[:15000])  # Hard cap

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

            parsed = BRDOutput.model_validate(json.loads(raw_json))

            if token_log is not None:
                token_log.append({"chain": "brd", "input": usage.prompt_tokens,
                                  "output": usage.completion_tokens, "total": usage.total_tokens})
            return parsed, metadata

        except ValidationError as e:
            extra_instruction = f"\n\nCRITICAL: Previous response had schema errors: {str(e)[:200]}. Return ONLY valid JSON matching the schema exactly."
            metadata["status"] = "retry"
            if attempt == settings.ai_max_retries:
                metadata["status"] = "error"
                metadata["error"] = f"Schema validation failed after {attempt+1} attempts"
                return None, metadata

        except Exception as e:
            metadata["status"] = "error"
            metadata["error"] = str(e)
            return None, metadata

    return None, metadata
