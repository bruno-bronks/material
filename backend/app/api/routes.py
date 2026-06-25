import json
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.graph import build_graph
from app.agent.node_labels import NODE_LABELS
from app.ingestion.pipeline import ingest_materials, ingest_papers
from app.memory import short_term
from app.memory.db import get_db
from app.memory.models import FeedbackRecord, QuestionRecord, SessionRecord
from app.schemas.api import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    IngestRequest,
    IngestResponse,
)

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    graph = build_graph()

    try:
        result = graph.invoke({"session_id": session_id, "user_question": request.question})
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    report = result.get("report", "")
    intent = result.get("intent", "")
    ranking = result.get("ranking", [])

    short_term.append_turn(session_id, request.question, intent, report)
    question_id = _persist_question(session_id, request.question, intent, report, ranking)

    return ChatResponse(
        session_id=session_id,
        question_id=question_id,
        intent=intent,
        report=report,
        materials=result.get("materials", []),
        papers=result.get("papers", []),
        ranking=ranking,
    )


@router.post("/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Mesmo fluxo de /chat, mas emite um evento SSE a cada node concluído do grafo —
    pensado pro frontend mostrar progresso em tempo real nos fluxos mais longos
    (em especial o loop de descoberta do V5/V6, que pode levar ~1min)."""
    session_id = request.session_id or str(uuid.uuid4())
    graph = build_graph()

    def event_stream():
        state: dict = {"session_id": session_id, "user_question": request.question}
        try:
            for chunk in graph.stream(state, stream_mode="updates"):
                node_name, update = next(iter(chunk.items()))
                state.update(update)
                payload = {
                    "type": "progress",
                    "node": node_name,
                    "label": NODE_LABELS.get(node_name, node_name),
                    "iteration": state.get("discovery_iteration"),
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)}, ensure_ascii=False)}\n\n"
            return

        report = state.get("report", "")
        intent = state.get("intent", "")
        ranking = state.get("ranking", [])

        short_term.append_turn(session_id, request.question, intent, report)
        question_id = _persist_question(session_id, request.question, intent, report, ranking)

        final_payload = {
            "type": "done",
            "session_id": session_id,
            "question_id": question_id,
            "intent": intent,
            "report": report,
            "materials": state.get("materials", []),
            "papers": state.get("papers", []),
            "ranking": ranking,
        }
        yield f"data: {json.dumps(final_payload, ensure_ascii=False, default=str)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/feedback")
def feedback(request: FeedbackRequest) -> dict:
    db = get_db()
    try:
        db.add(
            FeedbackRecord(
                question_id=request.question_id,
                rating=request.rating,
                comment=request.comment,
            )
        )
        db.commit()
    finally:
        db.close()
    return {"status": "stored"}


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    papers_indexed = 0
    materials_indexed = 0

    if request.kind in ("papers", "both"):
        papers_indexed = ingest_papers(request.query, limit=request.limit)
    if request.kind in ("materials", "both"):
        materials_indexed = ingest_materials(request.query, limit=request.limit)

    return IngestResponse(papers_indexed=papers_indexed, materials_indexed=materials_indexed)


def _persist_question(
    session_id: str, question: str, intent: str, report: str, ranking: list[dict]
) -> int:
    db = get_db()
    try:
        if not db.get(SessionRecord, session_id):
            db.add(SessionRecord(id=session_id))
            db.flush()

        question_record = QuestionRecord(
            session_id=session_id,
            question=question,
            intent=intent,
            report=report,
            ranking=ranking,
        )
        db.add(question_record)
        db.commit()
        return question_record.id
    finally:
        db.close()
