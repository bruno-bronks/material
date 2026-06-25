from pydantic import BaseModel, Field


class SubstitutionTarget(BaseModel):
    element_from: str = Field(description="elemento da estrutura base a ser substituído")
    rationale: str = Field(description="por que esse elemento é o ponto certo para intervir, dado o objetivo")


class CriticVerdict(BaseModel):
    accepted: bool = Field(description="o candidato atende ao objetivo do usuário?")
    reasons: list[str] = Field(description="razões objetivas para aceitar ou rejeitar")
