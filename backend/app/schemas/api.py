from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    question_id: int
    intent: str
    report: str
    materials: list[dict] = []
    papers: list[dict] = []
    ranking: list[dict] = []


class FeedbackRequest(BaseModel):
    question_id: int
    rating: str  # positivo | negativo | parcial | especialista
    comment: str = ""


class IngestRequest(BaseModel):
    query: str
    kind: str = "both"  # papers | materials | both
    limit: int = 10


class IngestResponse(BaseModel):
    papers_indexed: int = 0
    materials_indexed: int = 0
