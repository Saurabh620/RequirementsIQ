"""
AI Chain: Agile Artifacts Generator
Produces Epics, User Stories with Gherkin Acceptance Criteria.
"""
import json
import time
from pydantic import BaseModel, ValidationError
from typing import Optional
from config import settings
from ai.llm_client import get_llm_client, get_model_name

PROMPT_VERSION = "agile_v1"

SYSTEM_PROMPT = """\
You are an Agile delivery expert. Analyze the stakeholder input and generate Agile artifacts.

{domain_context}

OUTPUT RULES:
- Respond ONLY with valid JSON matching the schema below.
- Acceptance Criteria MUST use Gherkin format: Given / When / Then
- Story Points use Fibonacci: 1, 2, 3, 5, 8, 13 (estimate complexity, not time)
- User story format: "As a [role], I want to [action] so that [benefit]"

JSON SCHEMA:
{{
  "epics": [
    {{
      "id": "EP-001",
      "title": "string",
      "description": "string",
      "stories": [
        {{
          "id": "US-001",
          "title": "string",
          "story": "As a [role], I want to [action] so that [benefit]",
          "story_points": 3,
          "priority": "Must|Should|Could|Won't",
          "acceptance_criteria": [
            {{
              "given": "string",
              "when": "string",
              "then": "string"
            }}
          ]
        }}
      ]
    }}
  ],
  "overall_confidence": "high|medium|low"
}}"""

USER_PROMPT = """\
Analyze the following input and generate Agile artifacts JSON:
---
{input_text}
---"""


class AcceptanceCriteria(BaseModel):
    given: str
    when: str
    then: str


class UserStory(BaseModel):
    id: str
    title: str
    story: str
    story_points: int = 3
    priority: str = "Should"
    acceptance_criteria: list[AcceptanceCriteria]


class Epic(BaseModel):
    id: str
    title: str
    description: str
    stories: list[UserStory]


class AgileOutput(BaseModel):
    epics: list[Epic]
    overall_confidence: str = "medium"


def run(
    input_text: str,
    domain: str,
    domain_context: str,
    token_log: Optional[list] = None
) -> tuple[Optional[AgileOutput], dict]:
    client = get_llm_client()
    model  = get_model_name()
    metadata = {"chain": "agile", "prompt_version": PROMPT_VERSION,
                "tokens_used": 0, "latency_ms": 0, "status": "success", "error": None}
    system = SYSTEM_PROMPT.format(domain_context=domain_context)
    user = USER_PROMPT.format(input_text=input_text[:12000])
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

            parsed = AgileOutput.model_validate(json.loads(raw_json))
            if token_log is not None:
                token_log.append({"chain": "agile", "input": usage.prompt_tokens,
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
