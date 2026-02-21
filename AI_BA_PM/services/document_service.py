"""
Service: Document Service
Persists generated artifacts to MySQL and retrieves them.
"""
import json
import uuid
from datetime import datetime
from sqlalchemy import text
from database.connection import get_db
from ai.orchestrator import PipelineResult, estimate_cost_usd


def save_document(
    user_id: str,
    raw_input_text: str,
    input_type: str,
    domain: str,
    output_types: list[str],
    title: str = None
) -> str:
    """Create a document record. Returns new document_id."""
    doc_id = str(uuid.uuid4())
    output_types_str = ",".join(output_types)
    doc_title = title or f"Document — {datetime.now().strftime('%b %d, %Y %H:%M')}"

    with get_db() as db:
        db.execute(text("""
            INSERT INTO documents (id, user_id, title, input_type, raw_input_text, domain, status, output_types)
            VALUES (:id, :uid, :title, :itype, :text, :domain, 'processing', :otypes)
        """), {
            "id": doc_id, "uid": user_id, "title": doc_title,
            "itype": input_type, "text": raw_input_text[:65535],
            "domain": domain, "otypes": output_types_str
        })
    return doc_id


def save_pipeline_result(
    doc_id: str,
    user_id: str,
    result: PipelineResult,
    generation_start: float
) -> None:
    """Persist all pipeline outputs to the database."""
    import time
    gen_ms = int((time.time() - generation_start) * 1000)
    status = "completed" if not result.errors else ("partial" if any([result.brd, result.frd, result.agile]) else "failed")
    cost_usd = estimate_cost_usd(result.token_log)

    with get_db() as db:
        # Update document status
        db.execute(text("""
            UPDATE documents
            SET status=:status, completeness_score=:score, generation_time_ms=:ms,
                error_message=:err, updated_at=NOW()
            WHERE id=:id
        """), {
            "status": status, "score": result.completeness_score,
            "ms": gen_ms, "err": "; ".join(result.errors)[:500] if result.errors else None,
            "id": doc_id
        })

        # Save artifacts
        for art_type, content in [("brd", result.brd), ("frd", result.frd), ("agile", result.agile)]:
            if content:
                db.execute(text("""
                    INSERT INTO generated_artifacts (id, document_id, artifact_type, content_json, tokens_used, model_used)
                    VALUES (:id, :doc_id, :type, :content, :tokens, :model)
                """), {
                    "id": str(uuid.uuid4()), "doc_id": doc_id,
                    "type": art_type, "content": json.dumps(content),
                    "tokens": sum(t.get("total",0) for t in result.token_log if t.get("chain") == art_type),
                    "model": "gpt-4o"
                })

        # Save gap report
        if result.gap:
            gaps = result.gap.get("gaps", [])
            high = sum(1 for g in gaps if g.get("severity") == "HIGH")
            med  = sum(1 for g in gaps if g.get("severity") == "MEDIUM")
            low  = sum(1 for g in gaps if g.get("severity") == "LOW")
            db.execute(text("""
                INSERT INTO gap_reports (id, document_id, gaps_json, total_gaps, high_count, medium_count, low_count)
                VALUES (:id, :doc_id, :gaps, :total, :high, :med, :low)
            """), {
                "id": str(uuid.uuid4()), "doc_id": doc_id,
                "gaps": json.dumps(gaps), "total": len(gaps),
                "high": high, "med": med, "low": low
            })

        # Save risk report
        if result.risk:
            risks = result.risk.get("risks", [])
            critical = sum(1 for r in risks if r.get("risk_score") == "Critical")
            db.execute(text("""
                INSERT INTO risk_reports (id, document_id, risks_json, total_risks, critical_count)
                VALUES (:id, :doc_id, :risks, :total, :critical)
            """), {
                "id": str(uuid.uuid4()), "doc_id": doc_id,
                "risks": json.dumps(risks), "total": len(risks), "critical": critical
            })

        # Log AI usage
        for log in result.token_log:
            db.execute(text("""
                INSERT INTO ai_usage_logs (id, user_id, document_id, chain_name, model, input_tokens, output_tokens, total_tokens, estimated_cost_usd, status, error_code)
                VALUES (:id, :uid, :doc_id, :chain, :model, :inp, :out, :total, :cost, :status, :err_code)
            """), {
                "id": str(uuid.uuid4()), "uid": user_id, "doc_id": doc_id,
                "chain": log["chain"], "model": log.get("model", "unknown-model"),
                "inp": log.get("input", 0), "out": log.get("output", 0),
                "total": log.get("total", 0),
                "cost": cost_usd / max(len(result.token_log), 1) if log.get("status") != "error" else 0.0,
                "status": log.get("status", "success"),
                "err_code": str(log.get("error_code", ""))[:50] if log.get("error_code") else None
            })


def get_document(doc_id: str, user_id: str) -> dict | None:
    """Fetch a full document with all artifacts for display."""
    with get_db() as db:
        doc = db.execute(
            text("SELECT * FROM documents WHERE id=:id AND user_id=:uid"),
            {"id": doc_id, "uid": user_id}
        ).fetchone()
        if not doc:
            return None

        result = {
            "id": doc.id, "title": doc.title, "domain": doc.domain,
            "status": doc.status, "completeness_score": doc.completeness_score,
            "created_at": str(doc.created_at), "output_types": doc.output_types.split(","),
            "brd": None, "frd": None, "agile": None, "gap": None, "risk": None
        }

        # Artifacts
        artifacts = db.execute(
            text("SELECT artifact_type, content_json, is_edited, edited_content FROM generated_artifacts WHERE document_id=:id"),
            {"id": doc_id}
        ).fetchall()
        for art in artifacts:
            content = json.loads(art.edited_content if art.is_edited and art.edited_content else art.content_json)
            result[art.artifact_type] = content

        # Gap
        gap = db.execute(text("SELECT gaps_json, total_gaps, high_count, medium_count, low_count FROM gap_reports WHERE document_id=:id"), {"id": doc_id}).fetchone()
        if gap:
            result["gap"] = {"gaps": json.loads(gap.gaps_json), "total_gaps": gap.total_gaps,
                             "high_count": gap.high_count, "medium_count": gap.medium_count, "low_count": gap.low_count}

        # Risk
        risk = db.execute(text("SELECT risks_json, total_risks, critical_count FROM risk_reports WHERE document_id=:id"), {"id": doc_id}).fetchone()
        if risk:
            result["risk"] = {"risks": json.loads(risk.risks_json), "total_risks": risk.total_risks, "critical_count": risk.critical_count}

        return result


def get_user_documents(user_id: str, limit: int = 20) -> list[dict]:
    """Return list of recent documents for the history page."""
    with get_db() as db:
        rows = db.execute(text("""
            SELECT id, title, domain, status, completeness_score, output_types, created_at
            FROM documents WHERE user_id=:uid ORDER BY created_at DESC LIMIT :lim
        """), {"uid": user_id, "lim": limit}).fetchall()
        return [{"id": r.id, "title": r.title, "domain": r.domain, "status": r.status,
                 "score": r.completeness_score, "types": r.output_types, "created": str(r.created_at)} for r in rows]
