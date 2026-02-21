"""
AI Orchestrator — Main Pipeline Controller
Coordinates all 5 chains: BRD → FRD → Agile (parallel) → Gap → Risk (sequential)
"""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional

from ai.chains import brd_chain, frd_chain, agile_chain, gap_chain, risk_chain
from ai.llm_client import get_model_name
from ai.domain_context import get_domain_context
from utils.text_chunker import chunk_text


@dataclass
class PipelineResult:
    brd: Optional[dict] = None
    frd: Optional[dict] = None
    agile: Optional[dict] = None
    gap: Optional[dict] = None
    risk: Optional[dict] = None
    completeness_score: int = 0
    total_tokens: int = 0
    errors: list[str] = field(default_factory=list)
    token_log: list[dict] = field(default_factory=list)

    def to_summary(self) -> str:
        """Build a compact text summary for gap/risk context injection."""
        parts = []
        if self.brd:
            objectives = self.brd.get("business_objectives", [])
            parts.append(f"BRD: {len(objectives)} objectives, stakeholders: {len(self.brd.get('stakeholders',[]))}")
        if self.frd:
            frs = self.frd.get("functional_requirements", [])
            parts.append(f"FRD: {len(frs)} functional requirements")
        if self.agile:
            epics = self.agile.get("epics", [])
            stories = sum(len(e.get("stories", [])) for e in epics)
            parts.append(f"Agile: {len(epics)} epics, {stories} stories")
        return " | ".join(parts) if parts else "No structured output generated yet"


def run_pipeline(
    raw_text: str,
    domain: str,
    output_types: list[str],
    progress_callback=None,
    user_email: str = "System",
    user_name: str = "System User"
) -> PipelineResult:
    """
    Execute the full generation pipeline synchronously (suitable for Streamlit).
    
    Args:
        raw_text: The parsed plain text from user's upload/paste
        domain: 'bfsi' | 'saas' | 'healthcare' | 'generic'
        output_types: list of ['brd', 'frd', 'agile']
        progress_callback: optional callable(stage_name, pct) for Streamlit progress bar
        user_email: Email of the user generating the document
        user_name: Name of the user generating the document
    
    Returns:
        PipelineResult with all generated content
    """
    result = PipelineResult()
    token_log: list[dict] = []
    
    # Import datetime for document control
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")

    def _update(stage: str, pct: float):
        if progress_callback:
            progress_callback(stage, pct)

    # ── Stage 1: Prepare ────────────────────────────────────────
    _update("Analyzing input...", 0.05)
    chunks = chunk_text(raw_text, max_tokens=4000)
    primary_chunk = chunks[0]
    domain_ctx = get_domain_context(domain)

    # ── Stage 2: Parallel generation ────────────────────────────
    _update("Generating BRD, FRD, Agile artifacts...", 0.15)

    chain_tasks = {}
    if "brd" in output_types:
        chain_tasks["brd"] = (brd_chain.run, (primary_chunk, domain, domain_ctx, token_log))
    if "frd" in output_types:
        chain_tasks["frd"] = (frd_chain.run, (primary_chunk, domain, domain_ctx, token_log))
    if "agile" in output_types:
        chain_tasks["agile"] = (agile_chain.run, (primary_chunk, domain, domain_ctx, token_log))

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {
            executor.submit(fn, *args): name
            for name, (fn, args) in chain_tasks.items()
        }
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                output, meta = future.result()
                
                # Make sure every attempt gets a proper log line with the model attached
                if "model" not in meta:
                    meta["model"] = get_model_name()

                if output:
                    result_dict = output.model_dump()
                    
                    # Post-process BRD to populate document_control with real user data
                    if name == "brd" and result_dict.get("document_control"):
                        doc_control = result_dict["document_control"]
                        # Replace INSUFFICIENT_DATA with actual values
                        if doc_control.get("prepared_by") == "INSUFFICIENT_DATA":
                            doc_control["prepared_by"] = user_name
                        if doc_control.get("reviewed_by") == "INSUFFICIENT_DATA":
                            doc_control["reviewed_by"] = "Pending Review"
                        if doc_control.get("approved_by") == "INSUFFICIENT_DATA":
                            doc_control["approved_by"] = "Pending Approval"
                        if doc_control.get("date") == "INSUFFICIENT_DATA":
                            doc_control["date"] = current_date
                        if doc_control.get("version") == "INSUFFICIENT_DATA":
                            doc_control["version"] = "1.0"
                    
                    setattr(result, name, result_dict)
                    # The chain has likely already appended to token_log implicitly, but we need to ensure the model is injected
                    for log in token_log:
                        if log.get("chain") == name and "model" not in log:
                            log["model"] = meta["model"]
                else:
                    err_msg = meta.get('error', 'Unknown Error')
                    result.errors.append(f"{name.upper()} generation failed: {err_msg}")
                    # Force inject failing logs so admins can track them
                    token_log.append({
                        "chain": name, "model": meta["model"],
                        "input": 0, "output": 0, "total": 0,
                        "status": "error", "error_code": err_msg[:50]
                    })
            except Exception as e:
                result.errors.append(f"{name.upper()} chain error: {str(e)}")
                token_log.append({
                    "chain": name, "model": get_model_name(),
                    "input": 0, "output": 0, "total": 0,
                    "status": "error", "error_code": str(e)[:50]
                })

    _update("Running Gap Analysis...", 0.70)

    # ── Stage 3: Gap Detection (needs Stage 2 output) ───────────
    doc_summary = result.to_summary()
    gap_out, gap_meta = gap_chain.run(primary_chunk, doc_summary, token_log)
    if "model" not in gap_meta: gap_meta["model"] = get_model_name()
    
    if gap_out:
        result.gap = gap_out.model_dump()
        for log in token_log:
            if log.get("chain") == "gap" and "model" not in log: log["model"] = gap_meta["model"]
    else:
        err_msg = gap_meta.get('error', 'Unknown Error')
        result.errors.append(f"Gap analysis failed: {err_msg}")
        token_log.append({"chain": "gap", "model": gap_meta["model"], "input": 0, "output": 0, "total": 0, "status": "error", "error_code": err_msg[:50]})

    _update("Running Risk Analysis...", 0.85)

    # ── Stage 4: Risk Engine ────────────────────────────────────
    risk_out, risk_meta = risk_chain.run(primary_chunk, domain, doc_summary, token_log)
    if "model" not in risk_meta: risk_meta["model"] = get_model_name()
    
    if risk_out:
        result.risk = risk_out.model_dump()
        for log in token_log:
            if log.get("chain") == "risk" and "model" not in log: log["model"] = risk_meta["model"]
    else:
        err_msg = risk_meta.get('error', 'Unknown Error')
        result.errors.append(f"Risk analysis failed: {err_msg}")
        token_log.append({"chain": "risk", "model": risk_meta["model"], "input": 0, "output": 0, "total": 0, "status": "error", "error_code": err_msg[:50]})

    # ── Stage 5: Finalize ───────────────────────────────────────
    result.token_log = token_log
    result.total_tokens = sum(t.get("total", 0) for t in token_log)
    result.completeness_score = _compute_score(result)
    _update("Complete!", 1.0)

    return result


def _compute_score(result: PipelineResult) -> int:
    score = 0
    if result.brd:   score += 35
    if result.frd:   score += 30
    if result.agile: score += 15
    if result.gap:   score += 10
    if result.risk:  score += 10
    return score


def estimate_cost_usd(token_log: list[dict], model: str = "gpt-4o") -> float:
    PRICING = {"gpt-4o": {"input": 0.0000025, "output": 0.00001}}
    p = PRICING.get(model, PRICING["gpt-4o"])
    total = 0.0
    for log in token_log:
        total += log.get("input", 0) * p["input"]
        total += log.get("output", 0) * p["output"]
    return round(total, 6)
